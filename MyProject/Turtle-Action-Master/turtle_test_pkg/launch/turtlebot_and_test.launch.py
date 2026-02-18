import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
  # 가제보 런치 파일 경로 설정
  gazebo_world_path = os.path.join(
    get_package_share_directory('turtlebot3_gazebo'),
    'launch', 'empty_world.launch.py'
  )

  return LaunchDescription(
    [
      IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_world_path)
      ),
      Node(
        package='turtle_test_pkg',
        executable='turtle_test_pub', # setup.py의 entry_points 이름
        output='screen'
      ),
      Node(
        package='turtle_test_pkg',
        executable='dist_tutle_action_server',
        output='screen'
      ),
    ]
  )
