import sys
import rclpy
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from turtle_test_pkg.test_ui import Ui_Form
from turtle_test_pkg.move_turtle import Move_turtle
from turtle_test_pkg.dist_tutle_action_server import DistTurtleServer, TurtleSub_Action
from turtle_test_pkg.distance_calc import Distance_calc

from geometry_msgs.msg import Twist
from PySide6.QtCore import QThread, Signal
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
import rclpy
from rclpy.node import Node

from rclpy.action import ActionClient
from my_first_package_msgs.action import DistTurtle
from std_srvs.srv import Trigger
import math

class RclpyThread(QThread):
  odom_signal = Signal(str)
  msg_signal = Signal(str)
  dist_signal = Signal(str)

  def __init__(self, executor):
    super().__init__()
    self.executor = executor

  def run(self):
    try:
      self.executor.spin()
    finally:
      rclpy.shutdown()


class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.ui = Ui_Form()
    # setupUi 함수를 호출해 MainWindow에 있는 위젯을 배치한다.
    self.ui.setupUi(self)
    # button clicked 이벤트 핸들러로 button_clicked 함수와 연결한다.
    self.ui.btn_go.clicked.connect(self.btn_go_clicked)
    self.ui.btn_back.clicked.connect(self.btn_back_clicked)
    self.ui.btn_right.clicked.connect(self.btn_right_clicked)
    self.ui.btn_left.clicked.connect(self.btn_left_clicked)

    self.ui.btn_stop.clicked.connect(self.btn_stop_clicked)
    self.ui.btn_home.clicked.connect(self.btn_home_clicked)
    self.ui.auto_check.stateChanged.connect(self.auto_mode_checked)

    rclpy.init()
    self.executor = MultiThreadedExecutor()
    self.rclpy_thread = RclpyThread(self.executor)

    # 시그널 연결
    self.rclpy_thread.odom_signal.connect( # 0,0 기준 좌표 출력
      lambda text: self.smart_scroll(text, self.ui.list_pose)
      )
    self.rclpy_thread.msg_signal.connect( # 각 이벤트 관련 출력
      lambda text: self.smart_scroll(text, self.ui.list_mesage)
      )
    self.rclpy_thread.dist_signal.connect( # 누적 거리 관련 출력
      lambda text: self.smart_scroll(text, self.ui.list_total_dist)
      )

    # 준비된 시그널을 노드에 넘기기
    self.pub_move = Move_turtle()
    self.service_node = Distance_calc()

    # 노드 추가 및 시작
    self.executor.add_node(self.pub_move)
    self.executor.add_node(self.service_node)

    # 구독 채널 생성
    self.pose_sub = self.pub_move.create_subscription(
      String,
      '/turtle_pose',
      self.pose_callback,
      10
    )

    self.pub_move.timer = self.pub_move.create_timer(1, self.turtle_move_check)
    self.velocity = 0.0
    self.angular = 0.0
    self.rclpy_thread.start()

    # 클라이언트 설정
    self.action_client = ActionClient(self.pub_move, DistTurtle, 'dist_turtle')
    self.dist_client = self.pub_move.create_client(Trigger, 'get_total_dist')

  def pose_callback(self, msg):
    self.rclpy_thread.odom_signal.emit(msg.data) # 서버 글자를 ui에 뿌림

  def turtle_move_check(self):
    if self.ui.auto_check.isChecked():
      self.auto_turtle_move()
    else:
      self.turtle_move()

  def auto_turtle_move(self):
    msg = Twist()
    msg.linear.x = self.velocity
    msg.linear.y = 0.0
    msg.linear.z = 0.0

    msg.angular.x = 0.0
    msg.angular.y = 0.0
    msg.angular.z = -0.5

    self.pub_move.move_turtle.publish(msg)
    self.pub_move.get_logger().info(f'auto mode: x={msg.linear._x:.2f}, z={msg.angular._z:.2f}')
    self.rclpy_thread.msg_signal.emit(f'auto mode: x={msg.linear._x:.2f}, z={msg.angular._z:.2f}') # 수정
    self.velocity += 0.08
    if self.velocity >2:
      self.velocity = 0.0

  def turtle_move(self):
    msg = Twist()
    msg.linear.x = self.velocity
    msg.linear.y = 0.0
    msg.linear.z = 0.0

    msg.angular.x = 0.0
    msg.angular.y = 0.0
    msg.angular.z = self.angular
    self.pub_move.move_turtle.publish(msg)
    # self.goal_handle이 없거나, 있어도 작업이 끝난 상태라면 출력 허용
    if not hasattr(self, 'goal_handle') or self.goal_handle is None:
      self.pub_move.get_logger().info(f'manual mode: x={msg.linear._x:.2f}, z={msg.angular._z:.2f}')
      self.rclpy_thread.msg_signal.emit(f'manual mode: x={msg.linear._x:.2f}, z={msg.angular._z:.2f}') # 수정

  def goal_response_callback(self, future):
    self.goal_handle = future.result()
    if not self.goal_handle.accepted:
      self.rclpy_thread.msg_signal.emit("[EVENT_HOME] Goal Rejected")
      return
    self.rclpy_thread.msg_signal.emit("[EVENT_HOME] Returning to Home...")
    # 도착 시 결과 알림
    self.goal_handle.get_result_async().add_done_callback(self.get_result_callback)

  # 홈(원점) 도착
  def get_result_callback(self, future):
    result = future.result().result
    final_dist = math.sqrt(result.pos_x**2 + result.pos_y**2)

    if final_dist < 0.2:
      self.rclpy_thread.msg_signal.emit("[EVENT_HOME] Arrived at Home!")
    else:
      self.rclpy_thread.msg_signal.emit("[EVENT_HOME] Home Return Aborted.")

    self.goal_handle = None

  def action_feedback(self, feedback_msg):
    remained = feedback_msg.feedback.remained_dist
    self.rclpy_thread.msg_signal.emit(f"Distance remaining: {remained:.2f}m")

  ### 버튼 이벤트용 함수 모음 ###
  def btn_home_clicked(self):
    self.ui.auto_check.setChecked(False) # 강제 해제
    self.velocity = 0.0
    self.angular = 0.0

    if not self.action_client.server_is_ready():
      self.rclpy_thread.msg_signal.emit("Error: not action_server")
      return

    goal_msg = DistTurtle.Goal()
    goal_msg.dist = 0.0

    self.send_goal_future = self.action_client.send_goal_async(
      goal_msg,
      feedback_callback=self.action_feedback
    )
    self.send_goal_future.add_done_callback(self.goal_response_callback)

  def auto_mode_checked(self):
    if self.ui.auto_check.isChecked():
      if hasattr(self, 'goal_handle') and self.goal_handle is not None:
        self.goal_handle.cancel_goal_async()
        self.goal_handle = None # 초기화
      self.velocity = 1.0
    else:
      self.velocity = 0.0
      self.angular = 0.0
      stop_msg = Twist()
      self.pub_move.move_turtle.publish(stop_msg)

  def get_dist_callback(self, future):
    try:
      response = future.result()
      if response.success:
        # 서버에서 보낸 f"{self.sum_dist:.2f}" 문자열을 받아 출력
        sum_dist = response.message
        self.rclpy_thread.dist_signal.emit(f"Final Distance: {sum_dist}m ")
    except Exception as e:
      self.rclpy_thread.dist_signal.emit(f"[EVENT] Service call failed: {e}")

  def btn_stop_clicked(self):
    self.velocity = 0.0
    self.angular = 0.0

    self.stop_all_control()

    # 즉시 정지
    stop_msg = Twist()
    self.pub_move.move_turtle.publish(stop_msg)
    self.rclpy_thread.msg_signal.emit("[EVENT_STOP] Stop command sent.")

    # 누적 거리 서비스 호출 액션
    if self.dist_client.wait_for_service(timeout_sec=1.0):
      req = Trigger.Request()
      # 비동기 호출 후 대답이 오면 get_dist_callback 함수 실행 예약
      self.future = self.dist_client.call_async(req)
      self.future.add_done_callback(self.get_dist_callback)
    else:
      self.rclpy_thread.dist_signal.emit("Distance Service not available")

  def btn_go_clicked(self):
    self.stop_all_control()
    self.velocity += 0.2

  def btn_back_clicked(self):
    self.stop_all_control()
    self.velocity -= 0.2

  def btn_right_clicked(self):
    self.stop_all_control()
    self.angular -= 0.2

  def btn_left_clicked(self):
    self.stop_all_control()
    self.angular += 0.2

  ### 시스템 초기화 관련 함수 ###
  def stop_all_control(self):
    self.ui.auto_check.setChecked(False)

    if hasattr(self, 'goal_handle') and self.goal_handle is not None:
      self.goal_handle.cancel_goal_async()
      self.goal_handle = None # 초기화

  ### ui 스크롤 관련 함수 ###
  def smart_scroll(self, text, list_widget):
    list_widget.addItem(text)
    scrollbar = list_widget.verticalScrollBar()

    # 위치 > 스크롤 맨 아래 - (범위)
    if scrollbar.value() > (scrollbar.maximum() - 5):
      list_widget.scrollToBottom() # 맨 아래로 내림

  def ros_executer(self):
    self.executor.spin()

  def closeEvent(self, event):
    # 종료 시 리소스 정리
    self.executor.shutdown()
    self.rclpy_thread.quit()
    self.rclpy_thread.wait()
    super().closeEvent(event)

def main(args=Node):
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()

  sys.exit(app.exec())

if __name__ == "__main__":
  main()

