#!/usr/bin/env python3
# coding: utf-8

import os
from launch                      import LaunchDescription
from launch_ros.actions          import Node
from launch.substitutions        import PathJoinSubstitution
from launch_ros.substitutions    import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    ld       = LaunchDescription()

    node_joy = Node(
        package    = 'joy',
        executable = 'joy_node',
        name       = 'joy',
        namespace  = 'ddsm_robot'
    )

    node_teleop = Node(
        package    = 'teleop_twist_joy',
        executable = 'teleop_node',
        name       = 'teleop_node',
        namespace  = 'ddsm_robot',
        parameters = [PathJoinSubstitution([FindPackageShare('ros2_ddsm_robot'), 'config', 'teleop_params.yaml'])]
    )

    ld.add_action(node_joy)
    ld.add_action(node_teleop)

    return ld
