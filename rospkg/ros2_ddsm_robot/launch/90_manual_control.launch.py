#!/usr/bin/env python3
# coding: utf-8

import os
from launch                            import LaunchDescription
from launch.actions                    import IncludeLaunchDescription
from launch_ros.actions                import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions              import PathJoinSubstitution
from launch_ros.substitutions          import FindPackageShare
from ament_index_python.packages       import get_package_share_directory


def generate_launch_description():
    ld       = LaunchDescription()

    other_launch_file = os.path.join( get_package_share_directory('ros2_ddsm_robot'), 'launch', '00_base_controller.launch.py' )
    nodes_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(other_launch_file),
        launch_arguments={'some_arg': 'value'}.items()
    )

    other_launch_file = os.path.join( get_package_share_directory('ros2_ddsm_robot'), 'launch', '01_joystick_teleop.launch.py' )    
    nodes_teleop = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(other_launch_file),
        launch_arguments={'some_arg': 'value'}.items()
    )
    
    ld.add_action(nodes_control)
    ld.add_action(nodes_teleop)

    return ld
