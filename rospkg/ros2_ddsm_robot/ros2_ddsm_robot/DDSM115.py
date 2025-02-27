#!/usr/bin/env python3
# coding: utf-8

import time
import serial
import struct
import crcmod.predefined
import numpy as np
from enum import Enum
from dataclasses import dataclass


# print driver information
def print_info(text):
    print("DDSM115_INFO | {}".format(text))


# print driver warning
def print_warning(text):
    print("DDSM115_WARNING | {}".format(text))


# drive mode
class DDSM115_MODE(Enum):
    UNDEFINED = 0
    CURRENT   = 1
    VELOCITY  = 2
    POSITION  = 3


# error
class DDSM115_ERROR(Enum):
    UNDEFINED = 0
    CURRENT   = 1
    VELOCITY  = 2
    POSITION  = 3
    
    
# status
@dataclass
class DDSM115_STATUS:
    device_id   : int
    mode        : int
    current     : float
    velocity    : float
    position    : float
    temperature : float
    error       : int


# driver class
class DDSM115(object):
    # constructor
    def __init__(self, port:str='/dev/ttyUSB0', baud:int=115200, ids=[], callback=None, timeout=0.01):
        self._timeout     = timeout
        self._ser         = serial.Serial(port, baud, timeout=self._timeout)
        self._crc8        = crcmod.predefined.mkPredefinedCrcFun('crc-8-maxim')
        self._str_10bytes = ">BBBBBBBBBB"
        self._str_9bytes  = ">BBBBBBBBB"        
        self._buffer      = bytearray(b'')
        self._status      = {}
        self._bus_busy    = False
        
        # start thread
        #self._th_receive = threading.Thread(target=self._process_receive)
        #self._th_receive.setDaemon(True)
        #self._th_receive.start()
        
        # initialize status
        if( len(ids) > 0 ):
            for _id in ids:
                self._status[_id] = DDSM115_STATUS( device_id=_id, mode=0, current=0.0, velocity=0.0, position=0.0, temperature=0.0, error=0 )


    # destructor
    def __del__(self):
        self._ser.close()
        return
        

    # convert int16 to bytesarray
    def _int16_to_bytesarray(self, data: int):
        byte1 = (data & 0xFF00) >> 8
        byte2 = (data & 0x00FF)
        return [byte1, byte2]


    # convert bytesarray to int16
    def _bytesarray_to_int16(self, high_byte: int, lo_byte: int):
        int16 = ((high_byte & 0xFF)) << 8 | (lo_byte & 0xFF)
        return np.array(int16).astype(np.int16).item()


    # map function
    def _map(self, val, in_min, in_max, out_min, out_max):
        return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


    # parse packet        
    def _parse_feedback( self, buffer: bytes ):
        # check length
        if( len(buffer) != 10 ):            
            #print( 'invalid packet length' )
            return False
            
        # check CRC
        if( buffer[9] != self._crc8( bytes(buffer[:-1]) ) ):
            #print( 'invalid CRC' )
            return False

        # get data
        _id    = buffer[0]                                          # motor ID
        _mode  = buffer[1]                                          # drive mode
        _cur_i = self._bytesarray_to_int16( buffer[2], buffer[3] )  # current
        _vel_i = self._bytesarray_to_int16( buffer[4], buffer[5] )  # velocity
        _pos_i = self._bytesarray_to_int16( buffer[6], buffer[7] )  # position
        _error = buffer[8]                                          # error
        _crc   = buffer[9]                                          # CRC
                
        _current  = self._map( _cur_i, -32767, 32767, -8.0, 8.0 )
        _velocity = float(_vel_i)
        _position = self._map( _pos_i, 0, 32767, 0.0, 360.0 )
        
        if( not( _id in self._status ) ):
            #print( 'undefined ID' )
            return False
            
        # get motor status
        self._status[_id].device_id = _id
        self._status[_id].mode      = _mode
        self._status[_id].current   = _current
        self._status[_id].velocity  = _velocity
        self._status[_id].position  = _position
        self._status[_id].error     = _error
        
        return True


    # get motor state
    def get_state( self, device_id: int ):
        if( not( device_id in self._status ) ):
            print( 'undefined ID' )
            return None
        return self._status[device_id]


    # send command to DDSM115
    def _send_com( self, data: bytes ):
        # wait serial bus is writable
        # send packet
        self._ser.write(data)
        
        # receive data
        buf = self._ser.read(10)

        return buf
 

    # convert current(A) to int16
    def _current_to_int16(self, cur_raw: int):
        return self._map(cur_raw, -32767, 32767, -8.0, 8.0)


    # calc and attach CRC code to packet
    def _crc_attach(self, data_bytes : bytes):
        crc_int         = self._crc8(data_bytes)
        data_bytesarray = bytearray(data_bytes)
        data_bytesarray.append(crc_int)
        full_cmd        = bytes(data_bytesarray)
        return full_cmd


    # check CRC
    def _crc_check( self, data_bytes: bytes ):        
        return self._crc8(data_bytes)


    # set motor ID
    # connect only 1 motor, and call this function to set the ID of that motor
    def set_id(self, _id: int):
        # make packet
        cmd_bytes = struct.pack(self._str_10bytes, 0xAA, 0x55, 0x53, _id, 0x00, 0x00, 0x00, 0x00, 0x00, 0xDE)
        # send packet 5 times
        for i in range(5):
            self._send_com(cmd_bytes)
            time.sleep(1.0)
        return


    # set drive mode
    def set_mode(self, device_id: int, mode: int):
        # make packet
        if(   mode == 1 ):
            print_info(f"Set {device_id} as current (torque) mode")
        elif( mode == 2 ):
            print_info(f"Set {device_id} as velocity mode")
        elif( mode == 3 ):
            print_info(f"Set {device_id} as position mode")
        else:
            print_info(f"Error {mode} is unknown")
        # make packet
        cmd_bytes = struct.pack(self._str_10bytes, device_id, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, mode)
        
        # send packet
        buffer = self._send_com(cmd_bytes)
        """
        if( self._parse_feedback(buffer) ):
            return self._status[device_id]
        """

        return None


    # set degree
    def send_current(self, device_id: int, current):
        cur_ints  = self._int16_to_bytesarray(self._map(current,-8.0,8.0,-32767,32767))
        # make packet
        cmd_bytes = struct.pack( self._str_9bytes, device_id, 0x64, cur_ints[0], cur_ints[1], 0x00, 0x00, 0x00, 0x00, 0x00 )
        cmd_bytes = self._crc_attach(cmd_bytes)

        # send packet
        buffer = self._send_com(cmd_bytes)

        # parse feedback        
        if( self._parse_feedback(buffer) ):
            return self._status[device_id]
        
        return None


    # set RPM
    def send_velocity(self, device_id: int, rpm: int):
        rpm_ints  = self._int16_to_bytesarray( int(rpm) )
        # make packet
        cmd_bytes = struct.pack( self._str_9bytes, device_id, 0x64, rpm_ints[0], rpm_ints[1], 0x00, 0x00, 0x00, 0x00, 0x00 )
        cmd_bytes = self._crc_attach(cmd_bytes)

        # send packet
        buffer = self._send_com(cmd_bytes)

        # parse feedback
        if( self._parse_feedback(buffer) ):
            return self._status[device_id]
        
        return None


    # set degree
    def send_position(self, device_id: int, deg: int):
        deg_ints  = self._current_to_int16( self._map(deg,0,360,0,32767) )
        # make packet
        cmd_bytes = struct.pack( self._str_9bytes,device_id, 0x64, deg_ints[0], deg_ints[1], 0x00, 0x00, 0x00, 0x00, 0x00 )
        cmd_bytes = self._crc_attach(cmd_bytes)
        # wait for serial port is writeable
        while( not self._ser.writable() ):
            print_warning("send_position not writable")
            time.sleep(0.1)

        # send packet
        buffer = self._send_com(cmd_bytes)
        
        # parse feedback
        if( self._parse_feedback(buffer) ):
            return self._status[device_id]

        return


    # get motor ID
    def get_motor_id(self):
        cmd_bytes = struct.pack(self.str_10bytes, 0xC8, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xDE)
        self._ser.write(cmd_bytes)
        return None


    # get feedback
    def get_motor_feedback(self, device_id: int):
        # make command
        cmd_bytes = struct.pack(self._str_9bytes, device_id, 0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        cmd_bytes = self._crc_attach(cmd_bytes)

        # send command
        self._send_com(cmd_bytes)
        

    # reply motor status
    def get_motor_state( self, device_id: int ):
        if( not device_id in self._status ):
            print( 'invalid ID' )
            return None
    
        return self._status[device_id]




# main function
def main(args=None):

    try:
        mot = DDSM115( ids=[1, 2] )
        mot.set_mode(1, 2)        
        mot.set_mode(2, 2)
        print( mot.get_motor_state(1) )        
        print( mot.get_motor_state(2) )
        time.sleep(3.0)
        
        while(1):
            for _ in range(50):
                print( mot.send_velocity(1,  50) )
                print( mot.send_velocity(2, -50) )
                time.sleep(0.1)
                
            for _ in range(50):
                print( mot.send_velocity(1, -50) )
                print( mot.send_velocity(2,  50) )
                time.sleep(0.1)

    except KeyboardInterrupt:
        print('interrupt')
        
    print('exit')
    mot.send_velocity(1, 0)
    mot.send_velocity(2, 0)




# entry point
if( __name__ == "__main__" ):
    main()
