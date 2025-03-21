#!/usr/bin/env python3
"""
PCA9685四电机差速控制系统接线图生成器
生成SVG格式的接线图，展示树莓派5、PCA9685和四个电机的连接方式
"""

import svgwrite
from svgwrite import cm, mm

# 创建SVG绘图
def create_wiring_diagram(filename="wiring_diagram.svg", size=('800px', '600px')):
    dwg = svgwrite.Drawing(filename, size=size)
    
    # 定义颜色
    colors = {
        'raspberry': '#BC1142',
        'pca9685': '#1B75BB',
        'motor_driver': '#39B54A',
        'motor': '#FBB03B',
        'i2c_line': '#FF5500',
        'pwm_line': '#00AAFF',
        'gpio_line': '#7F3F98',
        'power_line': '#FF0000',
        'gnd_line': '#000000'
    }
    
    # 添加标题
    dwg.add(dwg.text('PCA9685四电机差速控制系统接线图', 
                      insert=(400, 30), 
                      font_family="Arial", 
                      font_weight="bold",
                      font_size=24, 
                      text_anchor="middle"))
    
    # 绘制树莓派
    rpi = dwg.rect((50, 100), (150, 100), 
                    fill=colors['raspberry'], 
                    stroke='#000000', 
                    stroke_width=2, 
                    rx=5, ry=5)
    dwg.add(rpi)
    dwg.add(dwg.text('树莓派5', 
                      insert=(125, 150), 
                      font_family="Arial", 
                      font_size=12, 
                      text_anchor="middle"))
    
    # GPIO引脚
    gpio_pins = [
        ("5V", 65, "VCC"),
        ("GND", 85, "GND"),
        ("GPIO 2 (SDA)", 105, "I2C SDA"),
        ("GPIO 3 (SCL)", 125, "I2C SCL"),
        ("GPIO 24", 145, "D电机 IN2"),
        ("GPIO 25", 165, "D电机 IN1")
    ]
    
    for label, y, desc in gpio_pins:
        dwg.add(dwg.text(label, 
                         insert=(45, y), 
                         font_family="Consolas", 
                         font_size=10, 
                         text_anchor="end"))
        dwg.add(dwg.circle((50, y-4), 2, fill='black'))
        dwg.add(dwg.text(desc, 
                         insert=(55, y), 
                         font_family="Consolas", 
                         font_size=10, 
                         text_anchor="start"))
    
    # 绘制PCA9685
    pca = dwg.rect((300, 100), (150, 150), 
                    fill=colors['pca9685'], 
                    stroke='#000000', 
                    stroke_width=2, 
                    rx=5, ry=5)
    dwg.add(pca)
    dwg.add(dwg.text('PCA9685 PWM控制器', 
                      insert=(375, 125), 
                      font_family="Arial", 
                      font_size=12, 
                      text_anchor="middle"))
    
    # PCA9685引脚
    pca_pins = [
        ("VCC", 140, "电源"),
        ("GND", 160, "地线"),
        ("SDA", 180, "I2C数据"),
        ("SCL", 200, "I2C时钟"),
        ("PWM0", 220, "A电机 PWM"),
        ("PWM1/2", 240, "A电机 方向")
    ]
    
    for label, y, desc in pca_pins:
        dwg.add(dwg.text(label, 
                         insert=(295, y), 
                         font_family="Consolas", 
                         font_size=10, 
                         text_anchor="end"))
        dwg.add(dwg.circle((300, y-4), 2, fill='black'))
        dwg.add(dwg.text(desc, 
                         insert=(305, y), 
                         font_family="Consolas", 
                         font_size=10, 
                         text_anchor="start"))
    
    # 绘制电机驱动板
    motor_driver = dwg.rect((300, 350), (150, 100), 
                            fill=colors['motor_driver'], 
                            stroke='#000000', 
                            stroke_width=2, 
                            rx=5, ry=5)
    dwg.add(motor_driver)
    dwg.add(dwg.text('电机驱动板', 
                      insert=(375, 400), 
                      font_family="Arial", 
                      font_size=12, 
                      text_anchor="middle"))
    
    # 绘制电机
    motors = [
        ("左前电机 (A)", 150, 500),
        ("右前电机 (B)", 300, 500),
        ("左后电机 (C)", 450, 500),
        ("右后电机 (D)", 600, 500)
    ]
    
    for label, x, y in motors:
        motor = dwg.rect((x-50, y-25), (100, 50), 
                          fill=colors['motor'], 
                          stroke='#000000', 
                          stroke_width=2, 
                          rx=10, ry=10)
        dwg.add(motor)
        dwg.add(dwg.text(label, 
                         insert=(x, y), 
                         font_family="Arial", 
                         font_size=12, 
                         text_anchor="middle"))
    
    # 绘制连接线
    # I2C连接
    dwg.add(dwg.line((200, 105), (300, 180), 
                      stroke=colors['i2c_line'], 
                      stroke_width=3, 
                      stroke_dasharray="5,3"))
    dwg.add(dwg.line((200, 125), (300, 200), 
                      stroke=colors['i2c_line'], 
                      stroke_width=3, 
                      stroke_dasharray="5,3"))
    
    # VCC和GND连接
    dwg.add(dwg.line((200, 65), (300, 140), 
                      stroke=colors['power_line'], 
                      stroke_width=3))
    dwg.add(dwg.line((200, 85), (300, 160), 
                      stroke=colors['gnd_line'], 
                      stroke_width=3))
    
    # PWM连接
    dwg.add(dwg.line((375, 250), (375, 350), 
                      stroke=colors['pwm_line'], 
                      stroke_width=2))
    
    # 电机驱动到电机的连接
    dwg.add(dwg.line((325, 450), (150, 475), 
                      stroke='#000000', 
                      stroke_width=2))
    dwg.add(dwg.line((350, 450), (300, 475), 
                      stroke='#000000', 
                      stroke_width=2))
    dwg.add(dwg.line((400, 450), (450, 475), 
                      stroke='#000000', 
                      stroke_width=2))
    
    # GPIO到D电机的连接
    dwg.add(dwg.line((200, 145), (550, 350), 
                      stroke=colors['gpio_line'], 
                      stroke_width=2))
    dwg.add(dwg.line((200, 165), (575, 350), 
                      stroke=colors['gpio_line'], 
                      stroke_width=2))
    dwg.add(dwg.line((450, 200), (600, 475), 
                      stroke=colors['pwm_line'], 
                      stroke_width=2))
    
    # 添加图例
    legend_items = [
        (700, 100, "I2C总线", colors['i2c_line'], "5,3"),
        (700, 130, "电源线", colors['power_line'], None),
        (700, 160, "地线", colors['gnd_line'], None),
        (700, 190, "PWM信号", colors['pwm_line'], None),
        (700, 220, "GPIO信号", colors['gpio_line'], None),
        (700, 250, "连接线", '#000000', None)
    ]
    
    for x, y, text, color, dasharray in legend_items:
        line_props = {
            'stroke': color,
            'stroke_width': 2
        }
        if dasharray:
            line_props['stroke_dasharray'] = dasharray
            
        dwg.add(dwg.line((x-40, y), (x-10, y), **line_props))
        dwg.add(dwg.text(text, 
                         insert=(x, y+5), 
                         font_family="Arial", 
                         font_size=14))
    
    # 添加注释
    notes = [
        "注意：",
        "1. 图中仅显示主要连接，实际接线请参考文档",
        "2. 所有模块必须共地",
        "3. 请确保电源电压符合要求",
        "4. D电机使用GPIO直连控制方向"
    ]
    
    for i, note in enumerate(notes):
        dwg.add(dwg.text(note, 
                         insert=(50, 550 + i*20), 
                         font_family="Arial", 
                         font_size=14))
    
    # 保存SVG文件
    dwg.save()
    print(f"接线图已保存为: {filename}")

if __name__ == "__main__":
    create_wiring_diagram("docs/wiring_diagram.svg")
    # 也可以生成PNG格式 (需要安装cairosvg: pip install cairosvg)
    try:
        import cairosvg
        cairosvg.svg2png(url="docs/wiring_diagram.svg", write_to="docs/wiring_diagram.png", scale=2)
        print("接线图已同时保存为PNG格式")
    except ImportError:
        print("如需生成PNG格式，请安装cairosvg: pip install cairosvg") 