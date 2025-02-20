import os
from glob import glob
from setuptools import setup

package_name = 'ros2_ddsm_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/config', glob('config/*.rviz')),        
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sajisaka',
    maintainer_email='s_ajisaka@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu        = ros2_ddsm_robot.ros2_ddsm_robot_imu:main',
            'controller = ros2_ddsm_robot.ros2_ddsm_robot_controller:main',
            'id_setting = ros2_ddsm_robot.ros2_ddsm_id_setting:main',
        ],
    },
)
