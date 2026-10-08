from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    vision_source = LaunchConfiguration('vision_source')
    max_speed = LaunchConfiguration('max_speed')

    # Simulated xArm 6 + MoveIt Servo (fake hardware, no robot IP, ever)
    servo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            FindPackageShare('xarm_moveit_servo'), 'launch', 'xarm_moveit_servo_fake.launch.py',
        ])),
        launch_arguments={'dof': '6'}.items(),
    )

    vision = Node(
        package='hand_vision', executable='vision_node', output='screen',
        parameters=[{'source': vision_source}],
    )

    teleop = Node(
        package='hand_teleop', executable='teleop_node', output='screen',
        parameters=[{'max_speed': max_speed}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('vision_source', default_value='fake',
                              description="'fake' or the camera URL"),
        DeclareLaunchArgument('max_speed', default_value='0.05',
                              description='Teleop hard speed cap in m/s'),
        servo,
        vision,
        teleop,
    ])