# RPI_temperature_controller

This project is a Raspberry Pi-based temperature control system for monitoring and regulating temperature and humidity.
Utilizing GPIO, it connects three sensors, three heating lamps, and two fans to monitor and adjust environmental
temperature. An efficient temperature control solution for greenhouses, animal husbandry, and agriculture.
中文版：

本项目是一个基于树莓派的温控系统，旨在实现对温度和湿度的监测与控制。通过使用树莓派的 GPIO
引脚，连接三个温湿度传感器和三个加温灯，以及两个风扇，实现对环境温度的监测和调节。

树莓派作为控制模块，通过读取温湿度传感器的数据，并根据预设的温度阈值控制加温灯和风扇的开关。当环境温度低于设定值时，加温灯会被启动以升高温度；当环境温度超过设定值时，风扇会被启动以降低温度。通过这种方式，可以有效地维持环境温度在理想范围内。

本项目的设计可用于温室、养殖、种植等应用场景，为用户提供一个简单而高效的温控解决方案。

英文版：

This project is a temperature control system based on the Raspberry Pi, designed to achieve temperature and humidity
monitoring and control. By utilizing the GPIO pins of the Raspberry Pi, three temperature and humidity sensors, three
heating lamps, and two fans are connected to achieve environmental temperature monitoring and regulation.

The Raspberry Pi acts as the control module, reading data from the temperature and humidity sensors, and controlling the
on-off status of the heating lamps and fans based on preset temperature thresholds. When the ambient temperature is
below the set value, the heating lamps will be activated to raise the temperature; when the ambient temperature exceeds
the set value, the fans will be activated to lower the temperature. Through this mechanism, the environmental
temperature can be effectively maintained within an ideal range.

The design of this project can be used in applications such as greenhouses, animal husbandry, and agriculture, providing
users with a simple yet efficient temperature control solution.
