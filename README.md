# Donkey Car四电机差速控制系统

适用于树莓派5的Donkey Car四电机差速控制系统，通过PCA9685 PWM控制器实现准确可靠的四轮驱动。

## 项目特点

- 基于PCA9685 PWM控制器的四电机差速驱动
- 解决了树莓派5上pigpiod不稳定的问题
- 支持混合控制模式(PCA9685 PWM + GPIO)
- 无缝集成到Donkey Car自动驾驶框架
- 优化的PWM频率和死区处理
- 支持可调校准参数

## 文件结构

- `donkeycar/parts/quad_motor_pca9685.py` - 四电机控制器实现
- `donkeycar_integration.py` - Donkey Car集成代码
- `INSTALLATION.md` - 详细安装和配置指南

## 快速启动

1. 安装依赖
   ```bash
   pip install smbus2 gpiozero
   ```

2. 配置`myconfig.py`
   ```python
   DRIVE_TRAIN_TYPE = "DC_QUAD_WHEEL_PCA9685"
   ```

3. 启动
   ```bash
   python manage.py drive
   ```

详细安装和配置说明请参见[安装指南](INSTALLATION.md)。

## 控制原理

系统采用差速驱动原理，通过控制四个电机的速度差实现转向：

- 直行：四个电机速度相同
- 左转：右侧电机速度大于左侧
- 右转：左侧电机速度大于右侧
- 后退：所有电机反向运行

## 硬件连接

![接线图示意](/docs/wiring_diagram.png)

基本连接参考[安装指南](INSTALLATION.md)中的接线图。

## 自定义配置

可以通过`myconfig.py`调整以下参数：

- PWM频率
- 电机通道映射
- 最大速度
- 校准系数
- 转向灵敏度

## 常见应用场景

- 自动驾驶小车
- 机器人底盘
- 四轮差速移动平台
- 教育和研究项目

## 贡献与支持

欢迎提交Issue和Pull Request。如有问题，请参考[安装指南](INSTALLATION.md)中的故障排除部分。
