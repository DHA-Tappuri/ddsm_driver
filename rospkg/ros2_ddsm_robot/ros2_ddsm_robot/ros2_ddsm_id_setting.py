#!/usr/bin/env python3
# coding: utf-8

import os, time
import rclpy
from rclpy.node import Node
from .DDSM115   import DDSM115, DDSM115_STATUS



class ros2_ddsm_id_setting(Node):

    def __init__(self):
        # initialize node
        super().__init__('ros2_ddsm_id_setting')

        # declare parameter
        self.declare_parameter( 'port', '/dev/ttyUSB0')
        self.declare_parameter( 'baud', 115200)
        
        # read parameter
        self._port         = self.get_parameter('port').value
        self._baud         = int(self.get_parameter('baud').value)

        # initialize DDSM115
        #self._ddsm = DDSM115( port=self._port, baud=self._baud, ids=[] )
        
        # ID setting
        print(' make sure to ONLY ONE motor module is connected. ')
        time.sleep(1.0)
        print(' If it is OK, please input new ID. ')
        print(' If you want to cancel, please input minus number ')
        
        
        new_id = int(input('new motor ID :'))
        if( new_id < 0 ):
            print( ' ID setting canceled. ' )
            return
        
        print( 'new motor ID :', new_id )        
        print( 'setting new ID...' )
        for _ in range(3):
            #mot.set_id( _id = new_id )
            time.sleep(1)

        print( 'done' )
        return




# main function
def main(args=None):
    # initialize ROS2
    rclpy.init(args=args)

    # initialize node
    node = ros2_ddsm_id_setting()

    # Destroy the node explicitly
    node.destroy_node()
    rclpy.shutdown()




# main function
if(__name__ == '__main__'):
    main()

