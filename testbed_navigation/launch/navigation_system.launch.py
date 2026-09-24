from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    bringup_dir = get_package_share_directory('testbed_bringup')
    navigation_dir = get_package_share_directory('testbed_navigation')

    robot_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                bringup_dir,
                'launch',
                'testbed_full_bringup.launch.py'
            )
        )
    )

    map_loader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_dir,
                'launch',
                'map_loader.launch.py'
            )
        )
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_dir,
                'launch',
                'localization.launch.py'
            )
        )
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                navigation_dir,
                'launch',
                'navigation.launch.py'
            )
        )
    )

    return LaunchDescription([
        robot_bringup,
        map_loader,
        localization,
        navigation
    ])
