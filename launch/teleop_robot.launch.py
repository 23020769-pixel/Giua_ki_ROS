import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    # Chú ý: Tất cả code từ đây trở xuống phải được thụt vào 1 Tab (4 khoảng trắng)
    unified_teleop = ExecuteProcess(
        cmd=['xterm', '-e', 'python3', '-c', """
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import sys, select, termios, tty

msg = '''
-------------------------------------------
BẢNG ĐIỀU KHIỂN ROBOT TOÀN TẬP (KEYBOARD)
-------------------------------------------
1. ĐIỀU KHIỂN BÁNH XE:
   w : Tiến      s : DỪNG      x : Lùi
   a : Quay trái               d : Quay phải

2. ĐIỀU KHIỂN TAY MÁY:
   u : Link 1 (Lên)            j : Link 1 (Xuống)
   i : Link 2 (Xoay Trái)      k : Link 2 (Xoay Phải)

Bấm CTRL-C để thoát!
-------------------------------------------
'''

class UnifiedTeleop(Node):
    def __init__(self):
        super().__init__('unified_teleop')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.arm_pub = self.create_publisher(JointTrajectory, '/set_joint_trajectory', 10)
        self.link1_pos = 0.0
        self.link2_pos = 0.0

    def publish_base(self, linear, angular):
        t = Twist()
        t.linear.x = float(linear)
        t.angular.z = float(angular)
        self.cmd_pub.publish(t)

    def publish_arm(self):
        traj = JointTrajectory()
        traj.joint_names = ['link1_joint', 'link2_joint']
        pt = JointTrajectoryPoint()
        pt.positions = [self.link1_pos, self.link2_pos]
        pt.time_from_start.sec = 0
        pt.time_from_start.nanosec = 100000000 
        traj.points = [pt]
        self.arm_pub.publish(traj)

def main():
    rclpy.init()
    node = UnifiedTeleop()
    settings = termios.tcgetattr(sys.stdin)
    print(msg)
    
    try:
        while rclpy.ok():
            tty.setraw(sys.stdin.fileno())
            r, _, _ = select.select([sys.stdin], [], [], 0.1)
            key = sys.stdin.read(1) if r else ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

            if key:
                if ord(key) == 3: break
                elif key == 'w': node.publish_base(0.2, 0.0)
                elif key == 'x': node.publish_base(-0.2, 0.0)
                elif key == 'a': node.publish_base(0.0, 0.5)
                elif key == 'd': node.publish_base(0.0, -0.5)
                elif key == 's': node.publish_base(0.0, 0.0)
                elif key == 'u':
                    node.link1_pos = min(0.06, node.link1_pos + 0.002)
                    node.publish_arm()
                elif key == 'j':
                    node.link1_pos = max(0.0, node.link1_pos - 0.002)
                    node.publish_arm()
                elif key == 'i':
                    node.link2_pos = min(3.14, node.link2_pos + 0.1)
                    node.publish_arm()
                elif key == 'k':
                    node.link2_pos = max(-3.14, node.link2_pos - 0.1)
                    node.publish_arm()

    except Exception as e: print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
"""],
        output='screen'
    )

    return LaunchDescription([
        unified_teleop
    ])
