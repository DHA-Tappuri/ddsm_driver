#!/usr/bin/env python3
# coding: utf-8

import rclpy
from rclpy.clock       import Clock
from rclpy.node        import Node
from rclpy.time        import Time
from rclpy.duration    import Duration

from geometry_msgs.msg import Twist
from nav_msgs.msg      import Odometry

from .DDSM115          import DDSM115, DDSM115_STATUS

import numpy as np



class ros2_ddsm_robot_controller(Node):

    def __init__(self):
        # initialize node
        super().__init__('ros2_ddsm_robot_controller')

        # declare parameter
        self.declare_parameter( 'port', '/dev/ttyUSB0')
        self.declare_parameter( 'baud', 115200)
        self.declare_parameter( 'left_motor_id',  1)
        self.declare_parameter( 'right_motor_id', 2)
        self.declare_parameter( 'wheel_radius', 0.05)
        self.declare_parameter( 'wheel_tread',  1.00)
        self.declare_parameter( 'frame_id', 'odom')
        self.declare_parameter( 'timeout', 1.0)
        
        # read parameter
        self._port         = self.get_parameter('port').value
        self._baud         = int(self.get_parameter('baud').value)
        self._left_id      = int(self.get_parameter('left_motor_id').value)
        self._right_id     = int(self.get_parameter('right_motor_id').value)
        self._wheel_radius = float(self.get_parameter('wheel_radius').value)
        self._wheel_tread  = float(self.get_parameter('wheel_tread').value)
        self._frame_id     = self.get_parameter('frame_id').value
        self._timeout      = float(self.get_parameter('timeout').value)

        # control
        self._rot_vel     = 0.0
        self._trans_vel   = 1.0
        
        # odometry
        self._x           = 0
        self._y           = 0
        self._yaw         = 0

        # initialize topic
        self._pub_odom   = self.create_publisher( Odometry, 'odom', 10 )
        self._sub_cmdvel = self.create_subscription( Twist, 'cmd_vel', self._callback_cmdvel, 10 )

        # initialize DDSM115
        self._ddsm = DDSM115( port=self._port, baud=self._baud, ids=[self._left_id, self._right_id] )
        self._ddsm.set_mode(self._left_id,  2)        
        self._ddsm.set_mode(self._right_id, 2)
        self._state_left  = DDSM115_STATUS( device_id=self._left_id,  mode=0, current=0.0, velocity=0.0, position=0.0, temperature=0.0, error=0 )
        self._state_right = DDSM115_STATUS( device_id=self._right_id, mode=0, current=0.0, velocity=0.0, position=0.0, temperature=0.0, error=0 )
        
        # initialize timer
        self._last_time   = Clock().now()
        self._last_cmdvel = Clock().now()        
        self._tim_ctrl = self.create_timer(0.02, self._callback_control)


    # callback
    def _callback_cmdvel( self, msg ):
        self._rot_vel     = msg.linear.x
        self._trans_vel   = msg.angular.z
        self._last_cmdvel = Clock().now()
        return


    # control timer
    def _callback_control(self):
        if( ( Clock().now() - self._last_cmdvel ).nanoseconds * 1.0e-9 > self._timeout ):
            self._rot_vel     = 0.0
            self._trans_vel   = 0.0
    
        _left_rpm  = int( (self._trans_vel - self._wheel_tread*0.5*self._rot_vel) * 30.0/(np.pi*self._wheel_radius) )
        _right_rpm = int( (self._trans_vel + self._wheel_tread*0.5*self._rot_vel) * 30.0/(np.pi*self._wheel_radius) )
        self._state_left  = self._ddsm.send_velocity(self._left_id,  _left_rpm)
        self._state_right = self._ddsm.send_velocity(self._right_id, _right_rpm)
        
        if( self._state_left == None or self._state_right == None ):
            return
            
        _left_rpm   = self._state_left.velocity        
        _right_rpm  = self._state_right.velocity
        _trans_vel  = (_right_rpm + _left_rpm) * np.pi*self._wheel_radius/60.0
        _rot_vel    = (_right_rpm - _left_rpm) * np.pi*self._wheel_radius/(30.0*self._wheel_tread)

        # calc odometry        
        _dt = ( Clock().now() - self._last_time ).nanoseconds * 1.0e-9
        self._yaw = self._yaw + _rot_vel * _dt
        self._x   = self._x + _trans_vel * np.cos(self._yaw) * _dt
        self._y   = self._y + _trans_vel * np.sin(self._yaw) * _dt
        self._last_time = Clock().now()
        
        msg = Odometry()
        msg.header.stamp    = Clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.child_frame_id  = self._frame_id

        # position
        msg.pose.pose.position.x = self._x
        msg.pose.pose.position.y = self._y
        msg.pose.pose.position.z = 0.0

        # orientation
        msg.pose.pose.orientation.w = np.cos(self._yaw / 2.0)
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = np.sin(self._yaw / 2.0)

        # velocity
        msg.twist.twist.linear.x = _trans_vel
        msg.twist.twist.linear.y = 0.0
        msg.twist.twist.linear.z = 0.0
        msg.twist.twist.angular.x = 0.0
        msg.twist.twist.angular.y = 0.0
        msg.twist.twist.angular.z = _rot_vel
        
        self._pub_odom.publish(msg)

        return




# main function
def main(args=None):
    # initialize ROS2
    rclpy.init(args=args)

    # initialize node
    node = ros2_ddsm_robot_controller()
    rclpy.spin(node)

    # Destroy the node explicitly
    node.destroy_node()
    rclpy.shutdown()




# main function
if(__name__ == '__main__'):
    main()

