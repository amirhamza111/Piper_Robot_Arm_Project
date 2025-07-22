#!/usr/bin/env python3
# -*-coding:utf8-*-
# 注意demo无法直接运行，需要pip安装sdk后才能运行


'''This code is all about providing data to ML model to get values of joints.
so the joint moves to their respective position and perform the task.'''


## Importing All the Important Libraries
from typing import (
    Optional,
)
import time
from piper_sdk import *

import pickle 
from sklearn.tree import DecisionTreeRegressor
import joblib


## Importing The ML model which is provided in the same forlder. we can import it with 
## help of pickle or joblib.
## you can Import rf_model from file named as "Piper_Robot_Arm_Model_for_End_Effector_and_Joint_Angles.ipynb"

with open("rf_model.pkl","rb") as file:
    model = joblib.load(file)
    print("------------------------------------------------")
    print("Loaded Successfully")
    print("------------------------------------------------")



def enable_fun(piper:C_PiperInterface_V2):
    '''
    使能机械臂并检测使能状态,尝试5s,如果使能超时则退出程序
    ''' 
    enable_flag = False
    # 设置超时时间（秒）
    timeout = 5
    # 记录进入循环前的时间
    start_time = time.time()
    elapsed_time_flag = False
    while not (enable_flag):
        elapsed_time = time.time() - start_time
        print("--------------------")
        enable_flag = piper.GetArmLowSpdInfoMsgs().motor_1.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_2.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_3.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_4.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_5.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_6.foc_status.driver_enable_status
        print("使能状态:",enable_flag)
        piper.EnableArm(7)
        piper.GripperCtrl(0,1000,0x01, 0)
        print("--------------------")
        # 检查是否超过超时时间
        if elapsed_time > timeout:
            print("超时....")
            elapsed_time_flag = True
            enable_flag = True
            break
        time.sleep(1)
        pass
    if(elapsed_time_flag):
        print("程序自动使能超时,退出程序")
        exit(0)

if __name__ == "__main__":
    piper = C_PiperInterface_V2("can0")
    piper.ConnectPort()
    piper.EnableArm(7)
    enable_fun(piper=piper)
    # piper.DisableArm(7)
    piper.GripperCtrl(0,1000,0x01, 0)
    factor = 57295.7795 #1000*180/3.1415926
    # factor =1
    position = [0,0,0,0,0,0,0]
    count = 0
    while True:
        import time
        count  = count + 1
        # print(count)
        if(count == 0):
            print("1-----------")
            position = [0,0,0,0,0,0,0] # Original Values
            # position = [0.2,0.2,-0.2,0.3,-0.2,0.5,0.08]
        elif(count == 600):
            x_axis = float(input("Enter the X : ")) # Provide X_axis value
            y_axis = float(input("Enter the Y : ")) # Provide Y_axis value
            z_axis = float(input("Enter the Z : ")) # Provide Z_axis value
            gripper = float(input("Enter the Value of Gripper b/w 0.0 to 1.0: ")) # Provide value for gripper to open.
            position_getting = ((model.predict([[x_axis,y_axis,z_axis]]))[0]).tolist() # Model will predict the joint values
            position_getting = [round(x/factor,2) for x in position_getting]
            position_getting.append(gripper)
    

            print("2-----------")
            # position = [1.0,0.2,-0.2,0.3,-0.2,0.5,0.08]   # Original Values
            position = position_getting
            # position = [0,0,0,0,0,0,0]
            # position = [-8524,104705,-78485,-451,-5486,29843,0]
        elif(count == 1200):
            print("1-----------")
            position = [0,0,0,0,0,0,0] # Original Values
            # position = [0.2,0.2,-0.2,0.3,-0.2,0.5,0.08]
            count = 0
        
        joint_0 = round(position[0]*factor)
        joint_1 = round(position[1]*factor)
        joint_2 = round(position[2]*factor)
        joint_3 = round(position[3]*factor)
        joint_4 = round(position[4]*factor)
        joint_5 = round(position[5]*factor)
        joint_6 = round(position[6]*1000*1000)
        # piper.MotionCtrl_1()
        piper.MotionCtrl_2(0x01, 0x01, 20, 0x00)
        piper.JointCtrl(joint_0, joint_1, joint_2, joint_3, joint_4, joint_5)
        piper.GripperCtrl(abs(joint_6), 1000, 0x01, 0)
        print(piper.GetArmStatus())
        print(position)
        time.sleep(0.005)
        pass