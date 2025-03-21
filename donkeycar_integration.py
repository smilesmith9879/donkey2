# 修改Donkey Car的驱动程序加载代码
# 将以下代码添加到donkeycar/templates/complete.py的add_drivetrain函数中

"""
在donkeycar/templates/complete.py中找到add_drivetrain函数，
然后在现有的驱动类型条件判断后添加以下代码:
"""

# 在add_drivetrain函数中添加以下代码

def add_drivetrain(V, cfg):
    # 原有代码...
    
    if (not cfg.DONKEY_GYM) and cfg.DRIVE_TRAIN_TYPE != "MOCK":
        from donkeycar.parts import actuator, pins
        from donkeycar.parts.actuator import TwoWheelSteeringThrottle
        
        # 导入四电机控制器
        from donkeycar.parts.quad_motor_pca9685 import QuadMotorController
        
        # 判断是否使用差速驱动
        is_differential_drive = (
            cfg.DRIVE_TRAIN_TYPE.startswith("DC_TWO_WHEEL") or 
            cfg.DRIVE_TRAIN_TYPE == "DC_QUAD_WHEEL_PCA9685"
        )
        
        if is_differential_drive:
            V.add(TwoWheelSteeringThrottle(steering_zero=getattr(cfg, 'STEERING_ZERO', 0.01)),
                  inputs=['throttle', 'steering'],
                  outputs=['left/throttle', 'right/throttle'])
                  
        # 原有代码...
        
        # 新增四电机PCA9685差速驱动支持
        elif cfg.DRIVE_TRAIN_TYPE == "DC_QUAD_WHEEL_PCA9685":
            dt = cfg.DC_QUAD_WHEEL_PCA9685
            
            quad_motor = QuadMotorController(
                # PCA9685配置
                pca9685_addr=dt.get('PCA9685_ADDRESS', 0x40),
                pwm_freq=dt.get('PWM_FREQUENCY', 50),
                
                # 左前电机(A)
                pwma_channel=dt.get('MOTOR_A_PWM', 0),
                ain1_channel=dt.get('MOTOR_A_IN1', 2),
                ain2_channel=dt.get('MOTOR_A_IN2', 1),
                
                # 右前电机(B)
                pwmb_channel=dt.get('MOTOR_B_PWM', 5),
                bin1_channel=dt.get('MOTOR_B_IN1', 3),
                bin2_channel=dt.get('MOTOR_B_IN2', 4),
                
                # 左后电机(C)
                pwmc_channel=dt.get('MOTOR_C_PWM', 6),
                cin1_channel=dt.get('MOTOR_C_IN1', 8),
                cin2_channel=dt.get('MOTOR_C_IN2', 7),
                
                # 右后电机(D)
                pwmd_channel=dt.get('MOTOR_D_PWM', 11),
                din1_gpio=dt.get('MOTOR_D_IN1_GPIO', 25),
                din2_gpio=dt.get('MOTOR_D_IN2_GPIO', 24),
                
                # 控制参数
                max_speed=dt.get('MAX_SPEED', 100),
                debug=dt.get('DEBUG', False)
            )
            
            # 添加到车辆控制管道
            V.add(quad_motor, inputs=['left/throttle', 'right/throttle'])
            
        # 原有代码... 