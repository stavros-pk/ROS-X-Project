from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='xros_control',
            namespace='xros',
            executable='mode_node',
            name='mode',
            remappings=[('joy', '/xros/joy'),
                        ('control_effort', '/xros/control_effort')
            
            ],
        ),
        Node(
            package='xros_control',
            namespace='xros',
            executable='manual_operation_node',
            name='manual_operation_mode',
            remappings=[
                ('joy', '/xros/joy')],
        ),
        Node(
            package='xros_control',
            namespace='xros',
            executable='vessel_control',
            name='manual_control',
            remappings=[
                ('joy', '/xros/joy'),
                ('desired_heading', '/xros/desired_heading'),
                ('current_heading', '/xros/current_heading'), 
                ('pid_effort', '/xros/pid_effort')   
            ],
        ),
        Node(
            package='joy',
            namespace='xros',
            executable='joy_node',
            name='commands',
        ),
        Node(
            package='xros_automation',
            namespace='xros',
            executable='pid_control',
            name='heading_pid',
            parameters=[{'kp': 200.0, 'ki': 80.0, 'kd': 180.0
            }],
            remappings=[
                ('setpoint', '/xros/desired_heading'),
                ('feedback', '/xros/current_heading'),
                ('control_effort', '/xros/pid_effort')
            ],
        ),
        Node(
            package='xros_path_planning',
            namespace='xros',
            executable='waypoint_service_node',
            name='waypoint_handler',
        ),
        Node(
            package='xros_path_planning',
            namespace='xros',
            executable='point_of_interest',
            name='poi_handler',
        ),
    ])