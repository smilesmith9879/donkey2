import time
import math
import logging
from typing import Tuple
import smbus2 as smbus
from gpiozero import LED

import donkeycar as dk
from donkeycar.utils import clamp

logger = logging.getLogger(__name__)

class PCA9685:
    """
    PCA9685 PWM控制器类
    基于I2C总线通信，提供16通道PWM输出
    """
    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD
    
    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            logger.info("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)
        
    def write(self, reg, value):
        """Writes an 8-bit value to the specified register/address"""
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            logger.debug("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
            
    def read(self, reg):
        """Read an unsigned byte from the I2C device"""
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            logger.debug("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result
        
    def setPWMFreq(self, freq):
        """Sets the PWM frequency"""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            logger.info("Setting PWM frequency to %d Hz" % freq)
            logger.debug("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            logger.debug("Final pre-scale: %d" % prescale)
            
        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
        
    def setPWM(self, channel, on, off):
        """Sets a single PWM channel"""
        self.write(self.__LED0_ON_L + 4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4*channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4*channel, off >> 8)
        if (self.debug):
            logger.debug("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))
            
    def setDutycycle(self, channel, pulse):
        """
        设置占空比（0-100%）
        """
        self.setPWM(channel, 0, int(pulse * (4096 / 100)))
        
    def setLevel(self, channel, value):
        """
        设置通道输出高低电平
        """
        if (value == 1):
            self.setPWM(channel, 0, 4095)
        else:
            self.setPWM(channel, 0, 0)


class QuadMotorController:
    """
    四电机差速控制器
    使用PCA9685 PWM控制器和GPIO
    基于DonkeyCar框架设计，支持标准差速驱动接口
    """
    
    def __init__(self, 
                 pca9685_addr=0x40,
                 pwm_freq=50,
                 # A电机对应左前
                 pwma_channel=0,
                 ain1_channel=2,
                 ain2_channel=1,
                 # B电机对应右前
                 pwmb_channel=5,
                 bin1_channel=3,
                 bin2_channel=4,
                 # C电机对应左后
                 pwmc_channel=6,
                 cin1_channel=8,
                 cin2_channel=7,
                 # D电机对应右后
                 pwmd_channel=11,
                 din1_gpio=25,
                 din2_gpio=24,
                 # 控制参数
                 max_speed=100,
                 debug=False):
        """
        初始化四电机控制器
        
        参数说明:
        pca9685_addr - PCA9685的I2C地址
        pwm_freq - PWM频率
        pwm*_channel - 各电机PWM通道
        *in*_channel - PCA9685上的方向控制通道
        din*_gpio - 树莓派GPIO引脚编号(BCM)
        max_speed - 最大速度百分比(0-100)
        debug - 是否启用调试信息
        """
        # 初始化PWM控制器
        self.pwm = PCA9685(address=pca9685_addr, debug=debug)
        self.pwm.setPWMFreq(pwm_freq)
        
        # 电机A - 左前
        self.PWMA = pwma_channel
        self.AIN1 = ain1_channel
        self.AIN2 = ain2_channel
        
        # 电机B - 右前
        self.PWMB = pwmb_channel
        self.BIN1 = bin1_channel
        self.BIN2 = bin2_channel
        
        # 电机C - 左后
        self.PWMC = pwmc_channel
        self.CIN1 = cin1_channel
        self.CIN2 = cin2_channel
        
        # 电机D - 右后
        self.PWMD = pwmd_channel
        # 使用gpiozero替代pigpio
        self.motorD1 = LED(din1_gpio)  # GPIO方向控制
        self.motorD2 = LED(din2_gpio)  # GPIO方向控制
        
        # 控制参数
        self.max_speed = max_speed
        self.debug = debug
        
        # 方向定义
        self.Dir = ['forward', 'backward']
        
        logger.info("四电机差速控制器初始化完成")
    
    def MotorRun(self, motor, direction, speed):
        """
        控制单个电机运行
        
        参数:
        motor - 电机编号(0:左前, 1:右前, 2:左后, 3:右后)
        direction - 方向('forward'或'backward')
        speed - 速度(0-100)
        """
        if speed > self.max_speed:
            speed = self.max_speed
            
        if (motor == 0):  # 左前
            self.pwm.setDutycycle(self.PWMA, speed)
            if (direction == self.Dir[0]):  # 前进
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            else:  # 后退
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
                
        elif (motor == 1):  # 右前
            self.pwm.setDutycycle(self.PWMB, speed)
            if (direction == self.Dir[0]):  # 前进
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)
            else:  # 后退
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
                
        elif (motor == 2):  # 左后
            self.pwm.setDutycycle(self.PWMC, speed)
            if (direction == self.Dir[0]):  # 前进
                self.pwm.setLevel(self.CIN1, 1)
                self.pwm.setLevel(self.CIN2, 0)
            else:  # 后退
                self.pwm.setLevel(self.CIN1, 0)
                self.pwm.setLevel(self.CIN2, 1)
                
        elif (motor == 3):  # 右后
            self.pwm.setDutycycle(self.PWMD, speed)
            if (direction == self.Dir[0]):  # 前进
                self.motorD1.off()  # 低电平
                self.motorD2.on()   # 高电平
            else:  # 后退
                self.motorD1.on()   # 高电平
                self.motorD2.off()  # 低电平
    
    def MotorStop(self, motor):
        """停止指定电机"""
        if (motor == 0):
            self.pwm.setDutycycle(self.PWMA, 0)
        elif (motor == 1):
            self.pwm.setDutycycle(self.PWMB, 0)
        elif (motor == 2):
            self.pwm.setDutycycle(self.PWMC, 0)
        elif (motor == 3):
            self.pwm.setDutycycle(self.PWMD, 0)
    
    def run(self, left_throttle, right_throttle):
        """
        Donkey Car兼容的接口函数，控制左右两侧电机组
        
        参数:
        left_throttle - 左侧电机油门值(-1到1)
        right_throttle - 右侧电机油门值(-1到1)
        """
        # 确保输入值在有效范围内
        left_throttle = clamp(left_throttle, -1, 1)
        right_throttle = clamp(right_throttle, -1, 1)
        
        # 将-1到1的范围映射到0-100的速度值
        left_speed = abs(left_throttle) * self.max_speed
        right_speed = abs(right_throttle) * self.max_speed
        
        # 确定方向
        left_dir = self.Dir[0] if left_throttle >= 0 else self.Dir[1]
        right_dir = self.Dir[0] if right_throttle >= 0 else self.Dir[1]
        
        # 控制左侧电机组(左前和左后)
        self.MotorRun(0, left_dir, left_speed)  # 左前
        self.MotorRun(2, left_dir, left_speed)  # 左后
        
        # 控制右侧电机组(右前和右后)
        self.MotorRun(1, right_dir, right_speed)  # 右前
        self.MotorRun(3, right_dir, right_speed)  # 右后
    
    def shutdown(self):
        """关闭所有电机，Donkey Car框架要求的方法"""
        self.MotorStop(0)  # 左前
        self.MotorStop(1)  # 右前
        self.MotorStop(2)  # 左后
        self.MotorStop(3)  # 右后
        logger.info("四电机控制器已关闭")


# 测试代码
if __name__ == "__main__":
    import time
    
    # 创建控制器
    controller = QuadMotorController(debug=True)
    
    try:
        # 前进测试
        print("前进测试...")
        controller.run(0.5, 0.5)  # 左右两侧电机都50%速度前进
        time.sleep(2)
        
        # 左转测试
        print("左转测试...")
        controller.run(-0.3, 0.3)  # 左侧电机30%速度后退，右侧电机30%速度前进
        time.sleep(2)
        
        # 右转测试
        print("右转测试...")
        controller.run(0.3, -0.3)  # 左侧电机30%速度前进，右侧电机30%速度后退
        time.sleep(2)
        
        # 后退测试
        print("后退测试...")
        controller.run(-0.5, -0.5)  # 左右两侧电机都50%速度后退
        time.sleep(2)
        
    finally:
        # 停止所有电机
        controller.shutdown()
        print("测试完成，电机已停止") 