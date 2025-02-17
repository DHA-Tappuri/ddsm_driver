#!/usr/bin/env python3
# coding: utf-8

import rclpy
from rclpy.clock     import Clock
from rclpy.node      import Node

from sensor_msgs.msg import Imu

from .bno055_imu     import bno055_imu



class ros2_ddsm_robot_imu(Node):

    def __init__(self):
        # initialize node
        super().__init__('ros2_ddsm_robot_imu')

        # declare parameter

        # moving object detection
        self.declare_parameter( 'port', '/dev/ttyACM0')
        self.declare_parameter( 'baud', 115200)
        self.declare_parameter( 'frame_id', 'imu')

        # read parameter
        self._port     = self.get_parameter('port').value
        self._baud     = int(self.get_parameter('baud').value)
        self._frame_id = self.get_parameter('frame_id').value

        # initialize topic
        self._pub_imu = self.create_publisher( Imu, 'imu', 10 )

        # initialize delta 2G
        self._imu = bno055_imu( port=self._port, baud=self._baud, callback=self._cb_imu )


    # callback
    def _cb_imu( self, quat ):
        if( not 'w' in quat ):
            return
        if( not 'x' in quat ):
            return
        if( not 'y' in quat ):
            return
        if( not 'z' in quat ):
            return
    
        msg = Imu()
        msg.header.stamp    = Clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        msg.orientation.w   = quat['w']
        msg.orientation.x   = quat['x']
        msg.orientation.y   = quat['y']
        msg.orientation.z   = quat['z']
        self._pub_imu.publish(msg)



# main function
def main(args=None):
    # initialize ROS2
    rclpy.init(args=args)

    # initialize node
    node = ros2_ddsm_robot_imu()
    rclpy.spin(node)

    # Destroy the node explicitly
    node.destroy_node()
    rclpy.shutdown()




# main function
if(__name__ == '__main__'):
    main()

