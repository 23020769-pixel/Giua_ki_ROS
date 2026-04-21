import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_robot_pkg'
    urdf_file = 'robot.urdf' # Thay bằng tên file urdf của bạn nếu khác

    pkg_share = get_package_share_directory(package_name)
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_file)
    world_path = os.path.join(pkg_share, 'worlds', 'small_house.world')

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += os.pathsep + os.path.join(pkg_share, '..')
    else:
        os.environ['GAZEBO_MODEL_PATH'] = os.path.join(pkg_share, '..')
        
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # 1. Node xuất dữ liệu trạng thái robot
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 2. Khởi động Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
        launch_arguments={
            'world': world_path,
            'verbose': 'true'
        }.items()
    )

    # 3. Spawn (Thả) robot vào Gazebo
    spawn_entity = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=[
        '-topic', 'robot_description', 
        '-entity', 'my_robot', 
        '-x', '0.5',    # Lùi lại một chút theo trục X
        '-y', '-0.5',   # Đẩy sang bên phải theo trục Y (dấu âm)
        '-z', '0.1'     # Cho robot "rơi" từ trên cao xuống một tí để tránh dính sàn
    ],
    output='screen'
    )
    # 4. Khởi động RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_entity,
        rviz
    ])
