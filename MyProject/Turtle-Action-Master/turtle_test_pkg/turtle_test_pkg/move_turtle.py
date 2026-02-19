import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile


class Move_turtle(Node):
  def __init__(self):
    super().__init__('move_turtle')
    self.qos_profile = QoSProfile(depth = 10)
    self.move_turtle = self.create_publisher(Twist, '/cmd_vel', self.qos_profile)
    self.velocity = -1.0

def main(args=None):
  rclpy.init(args=args)
  node = Move_turtle()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard Interrupt (SIGINT)')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()
