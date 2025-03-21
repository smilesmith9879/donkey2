# PCA9685四电机差速驱动配置模板
# 将此内容添加到您的config.py或myconfig.py文件中

# 指定使用四电机差速驱动类型
DRIVE_TRAIN_TYPE = "DC_QUAD_WHEEL_PCA9685"

# PCA9685四电机差速驱动配置
DC_QUAD_WHEEL_PCA9685 = {
    # PCA9685控制器配置
    "PCA9685_ADDRESS": 0x40,          # I2C地址
    "PWM_FREQUENCY": 50,              # PWM频率
    
    # 左前电机配置(A电机)
    "MOTOR_A_PWM": 0,                 # PWM通道
    "MOTOR_A_IN1": 2,                 # 方向控制1通道
    "MOTOR_A_IN2": 1,                 # 方向控制2通道
    
    # 右前电机配置(B电机)
    "MOTOR_B_PWM": 5,                 # PWM通道
    "MOTOR_B_IN1": 3,                 # 方向控制1通道
    "MOTOR_B_IN2": 4,                 # 方向控制2通道
    
    # 左后电机配置(C电机)
    "MOTOR_C_PWM": 6,                 # PWM通道
    "MOTOR_C_IN1": 8,                 # 方向控制1通道
    "MOTOR_C_IN2": 7,                 # 方向控制2通道
    
    # 右后电机配置(D电机)
    "MOTOR_D_PWM": 11,                # PWM通道
    "MOTOR_D_IN1_GPIO": 25,           # GPIO引脚(BCM编号)
    "MOTOR_D_IN2_GPIO": 24,           # GPIO引脚(BCM编号)
    
    # 控制参数
    "MAX_SPEED": 100,                 # 最大速度百分比(0-100)
    "DEBUG": False                    # 调试模式
}

# 可选：差速转向参数
STEERING_ZERO = 0.01                  # 转向死区阈值 