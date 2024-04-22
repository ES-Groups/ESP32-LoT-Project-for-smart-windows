# -*- coding: UTF-8 -*-
"""
Author    				: 	 Junhan Lv
Email Address         	:    1322069095@qq.com
Filename             	:    main.py
Data                 	:    2023-11-9
Description           	:    windows control code.

 ------ -------             here is the main structure:
    |  -  |                 
    |     |                 wifi connect -> Acquire Device ID -> connect biogy service -> main code
    |  -  |                 main code: 1. motor encoder culculate speed   
 ------ ------                         2. IR sensor interupt        
                                       3. keep connetion with service  -> task1
                                       4. judge windows condition 
                                       5. read Pressure Sensor AD      -> task2 
                                       6. key interupt control 

Modification History    	: 
Data            Author       Version         Change Description
=======================================================
23/11/9        Junhan Lv    1.0              Original
24/4/3         Junhan Lv    1.1              Original update 


git commmit shell:

    git add .
    git commit -m "new added"
    git push origin master

"""

'''
PIN DESCRIPTION

电机控制:
IO 21 -> 电机转向AIN1
IO 18 -> 电机转向AIN2
IO 22 -> PWM输出PWMA
IO 26 -> 编码器输入1
IO 27 -> 编码器输入2 

红外和传感器:
IO 14 -> 红外输入引脚
IO 34 -> 风雨传感器输入

按键控制:
IO 16 -> 按键输入
IO 17 -> 按键输入
IO 19 -> 按键输入
IO 5  -> 按键输入
'''

import micropython
import machine
from machine import Pin,ADC,PWM,Timer
import utime
import _thread
import wifimgr
from Motor import Motor
from encoder import encoder
from bigconn import mybig
from state import *  
micropython.alloc_emergency_exception_buf(100)


gired_data = [0,0,0,0]  # 存储红外键值
value_num = 0


def IR_irq(IR_Recieve_Pin):  # 红外接收中断函数  中断开启后先结束所有线程
        #judge_work_is_done()
        global gired_data
        IR_High_time = 0  # 高电平时间
        if IR_Recieve_Pin.value() == 0:
            time_cnt = 1000
            while(not IR_Recieve_Pin.value()) and time_cnt:
                utime.sleep_us(10)
                time_cnt -= 1
                if time_cnt == 0:
                    return
            if IR_Recieve_Pin.value() == 1: # 进入4.5ms高电平
                time_cnt == 500
                while IR_Recieve_Pin.value() and time_cnt:  # 等待引导信号4.5ms高电平结束，超过5ms直接强制退出
                    utime.sleep_us(10)
                    time_cnt -= 1
                    if time_cnt == 0:
                        return
                for i in range(4):
                    for j in range(8):
                        time_cnt = 600
                        while (IR_Recieve_Pin.value() == 0) and time_cnt:
                            utime.sleep_us(10)
                            time_cnt -= 1
                            if time_cnt == 0:
                                return
                        time_cnt = 20
                        while IR_Recieve_Pin.value() == 1:
                            utime.sleep_us(100)
                            IR_High_time += 1
                            if IR_High_time > 20:
                                return
                        gired_data[i] >>= 1
                        if IR_High_time >= 8:
                            gired_data[i] |= 0x80
                        IR_High_time = 0
            if gired_data[2] != ~gired_data[3]:
                for i in range(4):
                    gired_data[i] = 0
                    return
        print(f"IR:{gired_data[2]}")
        SET_STATE_WINDOWS(gired_data[2])

        

def KEY_ON_irq(KEY_ON_Pin):   # 按键控制,打开窗
    SET_STATE_WINDOWS(STATE_DONE)
    pass

# def KEY_OFF_irq(KEY_OFF_Pin):  # 按键控制,关闭窗
    
#     pass

# def KEY_STOP_irq(KEY_STOP_Pin): # 按键控制,停止电机转动
    
#     pass

# def KEY_EXPAND_irq(KEY_EXPAND_Pin): # 按键扩展 
#     pass


def judge_work_is_done(): 
    """
        this function is utilized to judge whether windows has done the task or not  
    """
    utime.sleep_ms(300)
    print(Encoder.read())
    if (Encoder.read() == 0):
        SET_STATE_WINDOWS(STATE_DONE)
        
    

        
def timer_irq(timer_pin):
    global value_num
    Value =  Pressure_Sensor_ADC_IN_1.read()
    if(Value > 0):
        value_num += 1
    if(value_num>1):
        value_num = 0
        print(f"AD:{Value}")
        SET_STATE_WINDOWS(STATE_CLOSE_FLAG)


if __name__ == '__main__':
    """----------------periph initial--------------"""
    PWM_pin = PWM(Pin(22),freq=15000)
    Encoder = encoder(Pin(26,Pin.IN),Pin(27,Pin.IN),1)  # 编码器引脚绑定
    smart_windows = Motor(Pin(21,Pin.OUT),Pin(18,Pin.OUT),PWM_pin)

    IR_Pin = Pin(14,Pin.IN,Pin.PULL_UP)  # 配置红外中断引脚
    IR_Pin.irq(IR_irq,Pin.IRQ_FALLING)
    
    timer = Timer(0)
    # 初始化定时器
    timer.init(period=20, mode=Timer.PERIODIC, callback=timer_irq)
    
    # 按键输出
    key_on = Pin(0,Pin.IN,Pin.PULL_UP)
    key_on.irq(KEY_ON_irq,Pin.IRQ_FALLING)

    judge_work_is_done_pin = Pin(15,Pin.IN,Pin.PULL_UP)
    # key_off = Pin(19,Pin.IN,Pin.PULL_UP)
    # key_off.irq(KEY_OFF_irq,Pin.IRQ_FALLING)

    # key_stop = Pin(5,Pin.IN,Pin.PULL_UP)
    # key_stop.irq(KEY_STOP_irq,Pin.IRQ_FALLING)

    # key_expand = Pin(17,Pin.IN,Pin.PULL_UP)
    # key_expand.irq(KEY_EXPAND_irq,Pin.IRQ_FALLING)
    
    Pressure_Sensor_ADC_IN_1 = ADC(Pin(34))  # 压力传感器模拟量输入
    Pressure_Sensor_ADC_IN_1.atten(ADC.ATTN_11DB)

    # LED_TEST_BOARD = Pin(2,Pin.OUT)

    """----------------------wifi connect------------------------"""
        
    # wlan = wifimgr.get_connection()
    # if wlan is None:
    #     print("Could not initialize the network connection.")

    # # Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
    # print("ESP OK") 


    """--------------------start to connect bigiot service-----------------"""

    # bigiot = mybig(ID = DEVICEID,API_KEY = APIKEY,check=1)  # 不进行自检操作 实例化
    
    
    """----------------------child thread----------------------"""
    


    # TODO
    

    """-------------------main thread to judge the condition of windows and if windows closes or turns--------------------"""
    while True:
        if (GET_STATE_WINDOWS() == STATE_OPEN_FLAG or GET_STATE_WINDOWS() == IR_OPEN):  # motor forward
            WORK = True
            smart_windows.forward(WINDOWS_SPEED)
            judge_work_is_done()

        elif(GET_STATE_WINDOWS() == STATE_CLOSE_FLAG or GET_STATE_WINDOWS() == IR_CLOSE): # motor backword
            WORK = True
            smart_windows.backwards(WINDOWS_SPEED)  
            judge_work_is_done()

        elif(GET_STATE_WINDOWS() == STATE_DONE or GET_STATE_WINDOWS() == IR_STOP):    # motor stop
            WORK = False
            gired_data[2] = 0  # clear ir code
            smart_windows.stop()

        else:
            pass
        
           
           
