#!/usr/bin/env python3
# coding: utf-8

from launch                   import LaunchDescription
from launch_ros.actions       import Node
from launch.substitutions     import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ld = LaunchDescription()

    node_ddsm = Node(
        package    = 'ros2_ddsm_robot',
        executable = 'controller',
        name       = 'ddsm_controller',
        namespace  = 'ddsm_robot',
        parameters = [PathJoinSubstitution([FindPackageShare('ros2_ddsm_robot'), 'config', 'robot_params.yaml'])]
    )

    ld.add_action(node_ddsm)

    return ld
