from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            '/home/urvi/assignment_ws/src/level01_ros_assignment/'
            'testbed_navigation/config/amcl_params.yaml'
        ]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'autostart': True},
            {'node_names': ['amcl']}
        ]
    )

    return LaunchDescription([
        amcl,
        lifecycle_manager
    ])
