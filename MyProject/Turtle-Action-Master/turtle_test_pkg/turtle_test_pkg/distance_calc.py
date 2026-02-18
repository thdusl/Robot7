# 거리 계산 서비스
from std_srvs.srv import Trigger

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math

class Distance_calc(Node):
  def __init__(self):
    super().__init__('distance_calc')
    self.service = self.create_service(
      Trigger,
      "get_total_dist",
      self.calculate_callback)
    self.odom_sub = self.create_subscription(
    Odometry,
    '/odom',
    self.odom_callback,
    10)

    # 계산용 변수 초기화
    self.sum_dist = 0.0
    self.previous_x = None # 위치 값을 아직 안받음
    self.previous_y = None

  def odom_callback(self, msg):
    # 위치 저장
    curr_x = msg.pose.pose.position.x
    curr_y = msg.pose.pose.position.y

    if self.previous_x is not None:
      # 거리 계산
      dist = math.sqrt((curr_x - self.previous_x)**2 + (curr_y - self.previous_y)**2)
      self.sum_dist += dist

    self.previous_x = curr_x
    self.previous_y = curr_y

  def calculate_callback(self, request, response):
    response.success = True
    response.message = f"{self.sum_dist:.2f}" # 계산된 거리를 문자로 전달

    self.get_logger().info(f"Final Distance: {response.message}m")

    # 전송 후 초기화
    self.sum_dist = 0.0
    self.previous_x = None
    self.previous_y = None

    return response


def main(args=None):
  rclpy.init(args=args)
  node = Distance_calc()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard Interrupt (SIGINT)')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
  main()

