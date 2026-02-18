import rclpy as rp
import numpy as np
from rclpy.node import Node

from nav_msgs.msg import Odometry


class TurtlebotSubscriber(Node):
    def __init__(self, ac_server):
        super().__init__('turtlebot_subscriber')
        self.ac_server = ac_server
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.callback,
            10)

    def callback(self, msg):
        # 위치 저장
        self.ac_server.current_pose.x = msg.pose.pose.position.x
        self.ac_server.current_pose.y = msg.pose.pose.position.y

        # 각도 저장
        _, _, self.last_pose_theta = self.euler_from_quaternion(msg.pose.pose.orientation)

    def euler_from_quaternion(self, quat):
        x = quat.x
        y = quat.y
        z = quat.z
        w = quat.w

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw


def main(args=None):
    rp.init(args=args)

    turtlebot_subscriber = TurtlebotSubscriber()
    rp.spin(turtlebot_subscriber)

    turtlebot_subscriber.destroy_node()
    rp.shutdown()


if __name__ == '__main__':
    main()
