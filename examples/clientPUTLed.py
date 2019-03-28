'''
Created on 08-09-2012

@author: Maciej Wasilak
'''

import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address

class Agent():
    """
    Example class which performs single PUT request to iot.eclipse.org
    port 5683 (official IANA assigned CoAP port), URI "/large-update".
    Request is sent 1 second after initialization.

    Payload is bigger than 64 bytes, and with default settings it
    should be sent as several blocks.
    """

    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.putResource)

    def putResource(self):
        payload = "on"
        print "led on run"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = ("counter",)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = (ip_address('1XX.1XX.1XX.1XX'), coap.COAP_PORT)
        d = protocol.request(request)
        d.addCallback(self.printResponse)

    def printResponse(self, response):
        print 'Response Code: ' + coap.responses[response.code]
        print 'Payload: ' + response.payload
        reactor.crash()
log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)
reactor.listenMulticast(15153, protocol, listenMultiple=True)
