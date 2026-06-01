from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sensors',
            namespace='gps',
            executable ='gps_module',
            name='gps',
            # parameters=[{"parameter" : value}, ... ]
        ),

        Node(
            package='sensors',
            namespace='mpu6050',
            executable ='mpu_sensor',
            name='mpu6050',
            # parameters=[{"parameter" : value}, ... ]
        ),

        Node(
            package='teleop_twist_joy',
            executable ='teleop_node',
            name='teleop_node',
            # parameters=[{"parameter" : value}, ... ]
        ),

        Node(
            package='joy',
            executable ='joy_node',
            # parameters=[{"parameter" : value}, ... ]
        ),
    ])
