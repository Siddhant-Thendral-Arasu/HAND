from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# The fake arm starts with every joint at 0, which is a wrist singularity:
# Servo refuses to move from there. Bend the arm into this pose first.
READY_POSE = ('{joint_names: [joint1, joint2, joint3, joint4, joint5, joint6], '
              'points: [{positions: [0.0, -0.3, -0.5, 0.0, 0.8, 0.0], '
              'time_from_start: {sec: 3}}]}')


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

    # 6 s in: once the controller is up, move to the ready pose (takes 3 s)
    ready_pose = TimerAction(period=6.0, actions=[ExecuteProcess(
        cmd=['ros2', 'topic', 'pub', '--once', '/xarm6_traj_controller/joint_trajectory',
             'trajectory_msgs/msg/JointTrajectory', READY_POSE],
        output='screen',
    )])

    vision = Node(
        package='hand_vision', executable='vision_node', output='screen',
        parameters=[{'source': vision_source}],
    )

    # 11 s in: start teleop only after the arm has reached the ready pose
    teleop = TimerAction(period=11.0, actions=[Node(
        package='hand_teleop', executable='teleop_node', output='screen',
        parameters=[{'max_speed': max_speed}],
    )])

    return LaunchDescription([
        DeclareLaunchArgument('vision_source', default_value='fake',
                              description="'fake' or the camera URL"),
        DeclareLaunchArgument('max_speed', default_value='0.05',
                              description='Teleop hard speed cap in m/s'),
        servo,
        ready_pose,
        vision,
        teleop,
    ])
