# PCA9685四电机差速控制器安装指南

本指南介绍如何在树莓派5上安装和配置基于PCA9685的四电机差速控制系统，并集成到Donkey Car框架中。

## 硬件要求

1. 树莓派5
2. PCA9685 PWM控制器模块
3. 四个DC电机
4. L298N/TB6612等电机驱动模块
5. 12V电源(取决于电机规格)

## 接线图

### PCA9685连接

| 树莓派5 | PCA9685 |
|---------|---------|
| 5V      | VCC     |
| GND     | GND     |
| SCL (GPIO 3) | SCL |
| SDA (GPIO 2) | SDA |

### 电机连接

- **左前电机(A)**: PCA9685控制
  - PWM: 通道0
  - IN1: 通道2
  - IN2: 通道1

- **右前电机(B)**: PCA9685控制
  - PWM: 通道5
  - IN1: 通道3
  - IN2: 通道4

- **左后电机(C)**: PCA9685控制
  - PWM: 通道6
  - IN1: 通道8
  - IN2: 通道7

- **右后电机(D)**: PCA9685 + GPIO控制
  - PWM: 通道11 (PCA9685)
  - IN1: GPIO 25 (树莓派)
  - IN2: GPIO 24 (树莓派)

## 软件安装

### 1. 安装必要的依赖

```bash
# 安装smbus2和gpiozero
pip install smbus2 gpiozero

# 安装其他Donkey Car依赖
pip install -e .[pi]
```

### 2. 添加控制器文件

将`quad_motor_pca9685.py`文件复制到Donkey Car项目的`donkeycar/parts/`目录下：

```bash
cp quad_motor_pca9685.py ~/mycar/donkeycar/parts/
```

### 3. 修改完整模板文件

编辑`donkeycar/templates/complete.py`文件，在`add_drivetrain`函数中添加对四电机差速控制器的支持（参考`donkeycar_integration.py`中的代码）。

### 4. 配置myconfig.py

编辑您的`myconfig.py`文件，添加以下配置：

```python
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
```

## 测试和调试

### 1. 测试控制器

可以直接运行控制器文件测试电机控制：

```bash
python donkeycar/parts/quad_motor_pca9685.py
```

这将执行前进、左转、右转和后退的测试序列。

### 2. 使用Donkey Car启动

使用标准命令启动Donkey Car：

```bash
python manage.py drive
```

### 3. 调试

如果遇到问题，可以在配置中启用调试模式：

```python
DC_QUAD_WHEEL_PCA9685 = {
    # ...其他配置...
    "DEBUG": True  # 启用调试日志
}
```

## 常见问题排查

1. **I2C通信问题**：
   - 检查I2C连接是否正确
   - 使用`i2cdetect -y 1`命令确认PCA9685设备是否被识别
   - 确保I2C接口已启用(`sudo raspi-config` -> Interface Options -> I2C)

2. **电机不转动**：
   - 检查PWM和方向控制引脚配置是否正确
   - 确认电源供应是否足够
   - 使用万用表测量电机驱动板输出
   
3. **方向错误**：
   - 交换电机的方向控制引脚或配置
   - 或在代码中修改方向逻辑

4. **树莓派GPIO权限问题**：
   - 确保当前用户属于gpio用户组：`sudo usermod -a -G gpio $USER`
   - 重新登录使权限生效

## 高级配置

### 1. 电机校准

如果四个电机的响应特性不同，可以添加校准系数：

```python
# 在quad_motor_pca9685.py中的QuadMotorController类中添加
def __init__(self, ..., 
             left_front_scale=1.0, left_rear_scale=1.0,
             right_front_scale=1.0, right_rear_scale=1.0):
    # ...其他代码
    self.left_front_scale = left_front_scale
    self.left_rear_scale = left_rear_scale
    self.right_front_scale = right_front_scale
    self.right_rear_scale = right_rear_scale
    
# 然后在run方法中应用这些系数
```

### 2. 添加编码器反馈

如果需要更精确的速度控制，可以添加编码器支持：

```python
# 在myconfig.py中添加编码器配置
USE_ENCODERS = True
ENCODER_LEFT_A_GPIO = 17
ENCODER_LEFT_B_GPIO = 18
ENCODER_RIGHT_A_GPIO = 22
ENCODER_RIGHT_B_GPIO = 23
```

然后修改控制器代码实现闭环速度控制。 