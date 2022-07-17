#!/usr/bin/python
# -*- coding: utf-8 -*
import socket
from tabnanny import check
import rospy
import time
import sys
import subprocess
from subprocess import Popen, PIPE
from std_msgs.msg import Int32
from move_base_msgs.msg import MoveBaseActionResult

from Logger import Logger


class EAICarSDK(Logger):
    flag_nav_finished = True
    flag_arm_finished = True

    def __init__(self, ip, port):
        Logger.__init__("EAICarSDK", Logger.INFO)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (ip, port)
        self.tcp_socket.connect(self.server_addr)

        rospy.init_node('EAICarSDK', anonymous=True)

    # EAI TCP CMD SDK

    def sendCmd(self, cmd):
        """发送指令

        Args:
            cmd (Str): EAI 指令
        """
        self.tcp_socket.send(cmd.encode())
        self.debug("send command %s" % cmd)

    def sendCmdRecv(self, cmd, timeout=2):
        self.tcp_socket.send(cmd.encode())
        self.tcp_socket.settimeout(timeout)
        data = self.tcp_socket.recv(1024)
        self.tcp_socket.settimeout(None)
        self.debug("send command %s and get response %s " % (cmd, data))

        return data

    # ros callback

    def navResultCallback(self):
        self.debug("navResultCallback() entered! set flag_nav_finished")
        self.flag_nav_finished = True

    def armResultCallback(self):
        self.debug("armResultCallback() entered! set flag_arm_finished")
        self.flag_arm_finished = True

    # pump operation

    def pumpOpen(self):

        self.sendCmd("B1M1Pump;1#")

    def pumpClose(self):
        self.sendCmd("B1M1Pump;0#")

    # car operation
    def catMoveTo(self, place_flag):
        """车辆移动到目标点，仅仅设置目标，非阻塞

        Args:
            place_flag (str): 在上位机设置的目标点标签
        """

        self.sendCmdRecv("B1GotoTarget;"+place_flag+"#")
        self.flag_nav_finished = False
        self.info("set car aim: %s" % place_flag)

    def ifNavFinished(self):
        return self.flag_nav_finished

    def waitNavFinished(self, timeout=None, check_duration=0.05):
        """等待导航结束

        Args:
            timeout (float, optional): 等待超时时间，单位s. Defaults to None.
            check_duration (float, optional): 检查完成的间隔. Defaults to 0.05.
        """

        start_time = time.time()
        while not self.flag_nav_finished:
            if time.time()-start_time > timeout:
                break
            time.sleep(check_duration)

    def carAdjusMove(self):
        None

    # Arm operation start from here
    def armMoveTo(self, position, precision=2):
        """向机械臂规划队列中加入新的目标点，非阻塞

        Args:
            position (元组): (pos_x, pos_y,pos_z,rot_z)
            precision (int): 指令精度，保留小数点后多少位
        """
        # TODO:: 检查工作空间有效
        self.sendCmd("B1M1SetCmd;1;%.2f;%.2f;%.2f;%.2f;1#" %
                     (position[0], position[1], position[2], position[3]))
        self.flag_arm_finished = False
        self.info("set arm aim: %f ; %f ; %f ; %f" %
                  (position[0], position[1], position[2], position[3]))

    # apriltag operation

    def getApriltag(self):
        """获取识别到的所有apriltag

        Returns:
            Dict: 返回字典格式：{ID:(pos_x,pos_y)}
        """
        apriltag_info = {}

        tagsdata = self.sendCmdRecv("B1M1GetAdjustPose;1#")
        tags = x = tagsdata.split("*")
        for tag in tags:
            codes = tag.split(",|(|)")
            apriltag_info[int(codes[2])] = ((float)codes[0], (float)codes[1])
        return apriltag_info
