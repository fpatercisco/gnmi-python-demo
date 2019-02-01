# created by fpater@cisco 1/30/2019
"""A demo gNMI client in python. Just Capabilities() and Get() for now."""

import argparse
import datetime
import json

import grpc
import gnmi_pb2
import gnmi_pb2_grpc


global args # for d_print() -- suboptimal, I know :)


def d_print(*msgs):
    """print debug messages"""
    # args is global
    if args.debug:
        print(datetime.datetime.now().isoformat(), " DEBUG: ", end='')
        for msg in msgs:
            print(str(msg) + " ", end='')
        print('')


argparser = argparse.ArgumentParser()
argparser.add_argument('-d', '--debug', action='store_true', default=False)
argparser.add_argument('-t', '--target', action='store', help='<host>:<port>', required=True)
argparser.add_argument('-c', '--cert', action='store', default=None, help='Client cert')
#argparser.add_argument('-a', '--cacert', action='store', default=None, help='CA cert')
#argparser.add_argument('-k', '--key', action='store', default=None, help='Private key')
argparser.add_argument('-o', '--cert-hostname-override', action='store',
                       default='localhost', help='Client certificate hostname override.')
argparser.add_argument('-u', '--username', action='store', default=None,
                       help='gNMI authentication username')
argparser.add_argument('-p', '--password', action='store', default=None,
                       help='gNMI password')
argparser.add_argument('-C', '--capabilities', action='store_true', default=False,
                       help='Request capabilities from target.')
argparser.add_argument('-P', '--paths', action='store', default=None, nargs='+', required=True,
                       help='Request paths from target (slash-delimited, no kvp support)')
argparser.add_argument('-O', '--origin', action='store', default=None,
                       help='Path origin (i.e. openconfig-acl')
argparser.add_argument('-T', '--timeout', action='store', default=30,
                       help='Timeout in seconds')

args = argparser.parse_args()

d_print("args=" + str(args))


# use secure channel if cert was provided. 
if args.cert is not None:
    with open(args.cert, 'rb') as cert:
        creds=grpc.ssl_channel_credentials(cert.read())
    d_print("Credentials supplied: ", creds, ". Opening secure channel to " +
            args.target + "...")
    channel = grpc.secure_channel(target=args.target, credentials=creds,
                                  options=(('grpc.ssl_target_name_override',
                                            args.cert_hostname_override,),))
    d_print("Secure channel connected.")
else:
    d_print("Credentials not supplied. Opening _INSECURE_ channel to " +
            args.target + "...")
    channel = grpc.insecure_channel(target=args.target)
    d_print("Insecure channel connected.")

d_print("Creating gNMI stub...")
stub = gnmi_pb2_grpc.gNMIStub(channel)
d_print("Done.")


# metadata for gNMI authentication:
# https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-authentication.md
metadata = None
if args.username is not None and args.password is not None:
    metadata = (('username', args.username),('password', args.password))

# get & show capabilities if requested
if args.capabilities:
    d_print("Requesting capabilities...")
    capabilityResponse = stub.Capabilities(gnmi_pb2.CapabilityRequest(),
                                           metadata=metadata,
                                           timeout=args.timeout)
    #d_print("capabilityResponse: ", capabilityResponse)
    print("Capabilities received.")
    print("Supported models:")
    for m in capabilityResponse.supported_models:
        print(m)
    print("Supported Encodings:")
    for e in capabilityResponse.supported_encodings:
        print(e)
    print("gNMI Version: ", capabilityResponse.gNMI_version)


if args.paths:
    d_print("Creating getRequest...")
    prefix=gnmi_pb2.Path(origin=args.origin)
    # "repeated" PB message fields like "elem" and "path" must be Python iterables
    paths = []
    for path in args.paths:
        pathElems = []
        for elem in path.strip("/").split("/"):
            # TODO: add support for key-value pairs
            pathElems.append(gnmi_pb2.PathElem(name=elem))
            d_print("pathElems=", pathElems)
            paths.append(gnmi_pb2.Path(elem=pathElems))
            d_print("constructed paths=", paths)

    getRequest = gnmi_pb2.GetRequest(prefix=prefix, path=paths, type='ALL',
                                 encoding='JSON_IETF')
    d_print("getRequest=", getRequest)

    d_print("Executing gNMI Get()...")
    getResponse = stub.Get(getRequest, metadata=metadata, timeout=args.timeout)
    #d_print("getResponse: ", getResponse.notification)
    print("Response content: ")
    for n in getResponse.notification: # response can have multiple notifications
        print("timestamp: ", n.timestamp)
        print("alias: ", n.alias)
        for u in n.update: # a notification can have multiple updates
            print("update path: ", u.path)
            print("update val: ", json.dumps(json.loads(u.val.json_ietf_val), indent=4))
