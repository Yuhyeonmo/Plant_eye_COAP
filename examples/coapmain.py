# -*- coding: utf-8 -*-

import threading
# 주기적인 실행을 위한 함수
import json
import datetime
import socket

date = str(datetime.datetime.now())
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 2002))


def send_sectorSensor(second=2.0):
    tempData = {}

    tempData['TYPE'] = "01"
    # TY

    tempData['PLANT'] = "PLANT A"  # 플랜트 이름
    tempData['DATE'] = date
    # TS

    tempData['SECTOR'] = "SECTOR 1"  # 섹터이름
    tempData['HUMI'] = 1
    tempData['TEMP'] = 50
    tempData['CO2'] = 1
    tempData['O2'] = 4
    tempData['FLAM_GAS'] = 1
    tempData['HARM_GAS'] = 1

    print(tempData)

    data_string = json.dumps(tempData)
    # https://stackoverflow.com/questions/15190362/sending-a-dictionary-using-sockets-in-python

    sock.sendto(data_string.encode(), ('59.27.2.54', 2002))
    # 데이터프레임!

    threading.Timer(second, send_sectorSensor, [second]).start()  # 2초마다 반복


def send_humanSensor(second=2.0):
    tempData = {}

    tempData['TYPE'] = "02"
    # TY

    tempData['PLANT'] = "PLANT A"
    tempData['DATE'] = date

    tempData['ID'] = "사람"
    tempData['LOC'] = 1
    tempData['HEART_RATE'] = 1
    tempData['TEMP'] = 1
    print(tempData)

    data_string = json.dumps(tempData)
    # https://stackoverflow.com/questions/15190362/sending-a-dictionary-using-sockets-in-python

    sock.sendto(data_string.encode(), ('59.27.2.54', 2002))
    # 데이터프레임!

    threading.Timer(second, send_humanSensor, [second]).start()  # 2초마다 반복

