#!/usr/bin/env python3
# coding: utf-8

import os
import time
import serial
import json
import threading


# voice recognition class
class bno055_imu(object):

    # constructor
    def __init__(self, port:str='/dev/ttyACM1', baud:int=115200, callback=None):
        self._ser       = serial.Serial(port, baud)
        self._callback  = callback
        self._quat      = {}
        self._quat['w'] = 1.0
        self._quat['x'] = 0.0
        self._quat['y'] = 0.0
        self._quat['z'] = 0.0

        self._th_receive = threading.Thread(target=self._proc_receive)
        self._th_receive.setDaemon(True)
        self._th_receive.start()
        return


    # constructor
    def __del__(self):
        return


    def _proc_receive(self):
        while(True):
            try:
                _buf  = self._ser.readline()
                _jstr = _buf.decode('utf-8')
                self._quat = json.loads(_jstr)
                
                if( not self._callback == None ):
                    self._callback(self._quat)
            except:
                continue


    # get quaternion
    def get_quaternion(self):
        return self._quat




# callback function
def cb_quat(quat):
    print(quat)


# main function
def main(args=None):
    imu = bno055_imu(callback=cb_quat)

    while(True):
        time.sleep(0.1)

    return


# main function
if(__name__ == '__main__'):
    main()

