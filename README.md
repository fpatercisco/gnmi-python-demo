# gnmi-python-demo
A demo gNMI client in python. Currently Capabilities() and Get() are supported (Get() does not support key-value pairs yet). Set() and Subscribe() are not supported yet.

## Requirements
* Python 3
* `python3 -m pip install grpcio grpcio-tools`
* I've included pre-built python gRPC stubs for gNMI in this repo. To compile them yourself, [grab the protobufs from openconfig](https://github.com/openconfig/gnmi/tree/master/proto) and [follow the instructions from Google](https://grpc.io/docs/tutorials/basic/python.html#generating-client-and-server-code) :)

## Usage
`$ python3 ./gnmi-demo.py --help` for usage instructions. 

Generally you'll need to provide a client certificate (so you'll probably also need to override the cert hostname) and also need to provide a username and password for call-level authentication ([required by gNMI](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-authentication.md)).

Presently you can request the target's capabilites or provide a path and origin to retrieve configuration.

Here's an example of invoking the script to do both:

`$ python3 ./gnmi-demo.py -t [2001:420:2cff:1204::5502:2]:57344 --debug --cert ./ems.pem --cert-hostname-override ems.cisco.com --username cisco --password cisco --capabilities --paths /network-instances --origin openconfig-network-instance`
