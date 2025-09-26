#############################################################################

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration

import launch_ros.actions
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument

# from launch_ros.parameters import declare_parameter

def generate_launch_description():
    # arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    points_topic = LaunchConfiguration('points_topic', default='/sync_velo')
    odom_child_frame_id = LaunchConfiguration('odom_child_frame_id', default='velodyne')
    imu_topic = LaunchConfiguration('imu_topic', default='/sync_imu')
    globalmap_pcd = DeclareLaunchArgument('globalmap_pcd', default_value='/home/robit/colcon_ws/src/map.pcd', description='Path to the global map PCD file')

    # optional arguments
    use_imu = LaunchConfiguration('use_imu', default='true')
    invert_imu_acc = LaunchConfiguration('invert_imu_acc', default='false')
    invert_imu_gyro = LaunchConfiguration('invert_imu_gyro', default='false')
    use_global_localization = LaunchConfiguration('use_global_localization', default='false')
    enable_robot_odometry_prediction = LaunchConfiguration('enable_robot_odometry_prediction', default='false')
    robot_odom_frame_id = LaunchConfiguration('robot_odom_frame_id', default='odom')
    plot_estimation_errors = LaunchConfiguration('plot_estimation_errors', default='false')

    # include hdl_global_localization launch file
    # hdl_global_localization_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([get_package_share_directory('hdl_global_localization'), '/launch/hdl_global_localization.launch.py']),
    #     # condition=IfCondition(use_global_localization),
    # )

    # # nodelet manager
    # lidar_tf = Node(
    #     name='lidar_tf',
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     arguments=['0.27255', '0.00053', '0.17954', '0', '0',
    #                '0', '1', 'odom', 'velodyne']
    # )
    lidar_tf = Node(
        name='lidar_tf',
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.0', '0.0', '0.0', '0', '0',
                   '0', '1', 'odom', 'velodyne']
    )

    container = ComposableNodeContainer(
        name='container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            ComposableNode(
                package='hdl_localization',
                plugin='hdl_localization::GlobalmapServerNodelet',
                name='GlobalmapServerNodelet',
                parameters=[
                    {'globalmap_pcd': LaunchConfiguration('globalmap_pcd')},
                    {'convert_utm_to_local': True},
                    {'downsample_resolution': 0.1}]),
            ComposableNode(
                package='hdl_localization',
                plugin='hdl_localization::HdlLocalizationNodelet',
                name='HdlLocalizationNodelet',
                # remapping
                # 원래는 /velodyne_points, /gpsimu_driver/imu_data 토픽이 들어올 때 imu, lidar callback이 수행되는데,
                # remapping을 통해서 points_topic, imu_topic이 들어올 때 callback이 수행되도록 함.
                remappings=[('/sync_velo', points_topic), ('/sync_imu', imu_topic),('/gpsimu_driver/imu_data', imu_topic)],
                parameters=[
                    {'odom_child_frame_id': odom_child_frame_id},
                    {'use_imu': use_imu},
                    {'invert_acc': invert_imu_acc},
                    {'invert_gyro': invert_imu_gyro},
                    {'cool_time_duration': 2.0},
                    {'enable_robot_odometry_prediction': enable_robot_odometry_prediction},
                    {'robot_odom_frame_id': robot_odom_frame_id},
                    # <!-- available reg_methods: NDT_OMP, NDT_CUDA_P2D, NDT_CUDA_D2D-->
                    {'reg_method': 'NDT_OMP'},
                    {'ndt_neighbor_search_method': 'KDTREE'},
                    {'ndt_neighbor_search_radius': 2.5},
                    {'ndt_resolution': 0.8},
                    {'downsample_resolution': 0.6},
                    {'specify_init_pose': True},
                    {'init_pos_x': 0.0},
                    {'init_pos_y': 0.0},
                    {'init_pos_z': 0.0},
                    {'init_ori_w': 1.0},
                    {'init_ori_x': 0.0},
                    {'init_ori_y': 0.0},
                    {'init_ori_z': 0.0},
                    {'use_global_localization': use_global_localization}])
        ],
        output='screen',   
    )


    return LaunchDescription([
        DeclareLaunchArgument(
            'globalmap_pcd',
            default_value='/home/robit/colcon_ws/src/map.pcd',
            description='Path to the global map PCD file'
        ),
        launch_ros.actions.SetParameter(name='use_sim_time', value=True),
        lidar_tf, 
        container
    ])
    # return LaunchDescription([container])


