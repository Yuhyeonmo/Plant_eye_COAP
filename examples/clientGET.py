# -*- coding: utf-8 -*-

import sys
import threading
# 주기적인 실행을 위한 함수
import json
import datetime
import socket
from ipaddress import ip_address
import time
import clientPUT
from firebase import firebase
import clientPUTLed
import clientPUTLEDoff
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource



sensordatas = 'sensor'
check = 'alert'

humi = 1.0
temp = 1.0
o2 = 1
co2 = 1
result = ''
#초기값
fire = firebase.FirebaseApplication('https://fognode-71631.firebaseio.com/', )

def send_sectorSensor():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 2023))
    tempData = {}
    date = str(datetime.datetime.now())

    tempData['TYPE'] = "04"


    tempData['PLANT'] = "PLANT A"  # 플랜트 이름
    tempData['DATE'] = date


    tempData['SECTOR'] = "1"  # 섹터이름
    tempData['HUMI'] = humi
    tempData['TEMP'] = temp
    tempData['CO2'] = co2
    tempData['O2'] = o2
    tempData['FLAM_GAS'] = co2+o2
    tempData['HARM_GAS'] = humi+co2

    print(tempData)

    data_string = json.dumps(tempData)
    # https://stackoverflow.com/questions/15190362/sending-a-dictionary-using-sockets-in-python

    sock.sendto(data_string.encode(), ('1.245.182.84', 2023))
    # 데이터프레임!

    # threading.Timer(second, send_sectorSensor, [second]).start()  # 3초마다 반복
    sock.close()

class Agent:
        """
        Example class which performs single GET request to coap.me
        port 5683 (official IANA assigned CoAP port), URI "test".
        Request is sent 1 second after initialization.

        Remote IP address is hardcoded - no DNS lookup is preformed.

        Method requestResource constructs the request message to
        remote endpoint. Then it sends the message using protocol.request().
        A deferred 'd' is returned from this operation.

        Deferred 'd' is fired internally by protocol, when complete response is received.

        Method printResponse is added as a callback to the deferred 'd'. This
        method's main purpose is to act upon received response (here it's simple print).
        """


        def __init__(self, protocol):
            self.protocol = protocol
            reactor.callLater(1, self.requestResource)

        def requestResource(self):

                request = coap.Message(code=coap.GET)
                # Send request to "coap://coap.me:5683/test, raspberry addr"
                request.opt.uri_path = ('counter',)
                request.opt.observe = 0
                request.remote = (ip_address("168.188.1XX.1XX"), coap.COAP_PORT)
                d = protocol.request(request, observeCallback=self.printResponse)
                d.addCallback(self.printResponse)
                d.addErrback(self.noResponse)


        def printResponse(self, response):
            print 'First result: ' + response.payload

            global sensordatas
            sensordatas = response.payload
            global check
            check = sensordatas.split()
            global humi
            global temp
            global o2
            global co2
            # 습도, 온도 , o2(빗물), co2(수위)
            humi = float(check[1])
            temp = float(check[3])
            o2 = float(check[5])
            co2 = float(check[7])
            global result
            result = fire.get('/control_HW/ONOFF', None)

            if result == "alert":
                print 'check alert'
                Danger = clientPUT.Agent(self)
                # 현재는 모터 회전으로 사용
                reactor.crash()
            elif result == "ON" or result == "on":
                # Led on
                test = clientPUTLed.Agent(self)
                print "check on"
                reactor.crash()
            elif result == "OFF" or result == "off":
                # Led off
                test = clientPUTLEDoff.Agent(self)
                print "check off"
                reactor.crash()

            reactor.crash()

        def printLaterResponse(self, response):
            print 'Observe result: ' + response.payload


        def noResponse(self, failure):
            print('Failed to fetch resource:')
            print(failure)
            #reactor.stop()


log.startLogging(sys.stdout)
# 로그 출력

port = 30001
# 임의로 지정
while 1:
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = Agent(protocol)

    reactor.listenMulticast(port, protocol, listenMultiple=True)  # , interface="::")
    reactor.run()
    port = port + 1
    print sensordatas
    splitdata = sensordatas.split()
    # test split, test[1] :humi , test[3]= temperature, test[5]=sen(rain sensor), test[7]=sen2(water heigt)
    print splitdata

    send_sectorSensor()
    # 데이터 전송

    time.sleep(3)
    # 대기-> 아두이노 데이터처리 시간이 안맞음.