import rclpy as rp
from rclpy.action import ActionServer, CancelResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import Twist, Point
from std_msgs.msg import String
from my_first_package_msgs.action import DistTurtle
from turtle_test_pkg.my_subscriber import TurtlebotSubscriber


from rcl_interfaces.msg import SetParametersResult

import math
import time


class TurtleSub_Action(TurtlebotSubscriber):
  def __init__(self, ac_server):
    super().__init__(ac_server)

  def callback(self, msg):
    super().callback(msg)

    # 변수 업데이트
    curr_x = self.ac_server.current_pose.x
    surr_y = self.ac_server.current_pose.y
    self.ac_server.current_theta = self.last_pose_theta

    pose_text = f"Pose: x={curr_x:.2f}, y={surr_y:.2f}"
    self.ac_server.log_to_ui(pose_text)

class DistTurtleServer(Node):
  def __init__(self):
    super().__init__('dist_turtle_action_server')

    self.total_dist = 0.0
    self.is_first_time = True
    self.current_pose = Point()
    self.current_theta = 0.0

    self.pose_pub = self.create_publisher(String, '/turtle_pose', 10)

    self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
    self.action_server = ActionServer(
      self, DistTurtle, 'dist_turtle',
      execute_callback = self.excute_callback,
      cancel_callback=self.cancel_callback
    )
    self.log_to_ui('Dist turtle action server is started.')

  def log_to_ui(self, text):
    msg = String()
    msg.data = f"[SERVER] {text}"
    self.pose_pub.publish(msg)
    self.get_logger().info(text)

  def calc_diff_pose(self):
    if self.is_first_time:
      self.previous_pose.x = self.current_pose.x
      self.previous_pose.y = self.current_pose.y
      self.is_first_time = False

    diff_dist = math.sqrt((self.current_pose.x - self.previous_pose.x)**2 +\
                          (self.current_pose.y - self.previous_pose.y)**2)

    self.previous_pose = self.current_pose

    return diff_dist

  def cancel_callback(self, goal_handle):
    self.log_to_ui('Received cancel request!')
    return CancelResponse.ACCEPT

  def excute_callback(self, goal_handle):
    msg = Twist()
    stop_msg = Twist()
    self.last_log_dist = 100.0

    while True:
      # 중단 요청 체크
      if goal_handle.is_cancel_requested:
        self.publisher.publish(stop_msg)
        goal_handle.canceled()
        self.get_logger().info("Action Canceled and Robot Stopped")
        return DistTurtle.Result()

      # 목표까지 거리 계산
      dist_to_home = math.sqrt(self.current_pose.x**2 + self.current_pose.y**2)
      # 목표까지의 각도 계산
      target_theta = math.atan2(-self.current_pose.y, -self.current_pose.x)
      # 현재 각도와의 차이
      diff_theta = target_theta - self.current_theta

      ## 피드백 전송 ##
      dist_to_home = math.sqrt(self.current_pose.x**2 + self.current_pose.y**2)
      # 마지막 거리 - 현재 거리 차이가 3미터 이상일 때만 피드백 전송
      if (self.last_log_dist - dist_to_home) >= 3.0:
        fb_msg = DistTurtle.Feedback()
        fb_msg.remained_dist = dist_to_home
        goal_handle.publish_feedback(fb_msg)
        self.last_log_dist = dist_to_home # 현재 거리를 마지막 거리로 덮어씌우기

      # 각도 보정
      if diff_theta > math.pi: diff_theta -= 2*math.pi
      if diff_theta < -math.pi: diff_theta += 2*math.pi

      # 각도를 맞추기 위한 회전 (0.8은 속도)
      msg.angular.z = 0.8 * diff_theta

      if abs(diff_theta) < 0.3:
        msg.linear.x = 0.8
      else:
        msg.linear.x = 0.0

      if dist_to_home < 0.2:  # 도착 범위
        self.publisher.publish(stop_msg)
        break

      self.publisher.publish(msg) # 최종 명령 전송

      # 좌표 정보 보내기
      pose_msg = String()
      pose_msg.data = f"x={self.current_pose.x:.2f}, y={self.current_pose.y:.2f}"
      self.pose_pub.publish(pose_msg)

      time.sleep(0.05)

    self.get_logger().info('Success: Arrived at Home!')
    goal_handle.succeed()

    result = DistTurtle.Result()

    result.pos_x = self.current_pose.x
    result.pos_y = self.current_pose.y
    result.pos_theta = self.current_theta
    result.result_dist = self.total_dist

    # 액션을 위한 상태 초기화
    self.total_dist = 0
    self.is_first_time = True

    return result


def main(args=None):
  rp.init(args=args)

  executor = MultiThreadedExecutor()

  ac = DistTurtleServer()
  sub = TurtleSub_Action(ac_server = ac)

  executor.add_node(sub)
  executor.add_node(ac)

  try:
    executor.spin()

  finally:
    executor.shutdown()
    sub.destroy_node()
    ac.destroy_node()
    rp.shutdown()


if __name__ == '__main__':
  main()
