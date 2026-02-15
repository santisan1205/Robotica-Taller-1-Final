import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/robotica/Robotica-Taller-1-Final/ros2_ws/install/turtle_bot_3'
