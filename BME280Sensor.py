# coding: utf-8
import random
from smbus2 import SMBus

class BME280Sensor:

    def __init__(self, simulated_data):
        self.simulated_data = simulated_data
        if simulated_data == True:
            print "Use simulated data."
        else:
            print "Use real world data."
            bus_number = 1
            self.__i2c_address = 0x76
            self.__dig_temperature = []
            self.__dig_pressure = []
            self.__dig_humidity = []
            self.__bus = SMBus(bus_number)
            self.__setup()
            self.__get_calib_param()

    def read_temperature(self):
        if self.simulated_data:
            return "%.2f" % random.uniform(20, 50)
        else:
            data = []
            for i in range(0xF7, 0xF7 + 8):
                data.append(self.__bus.read_byte_data(self.__i2c_address, i))
            temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
            return self.__compensate_temperature(temp_raw)

    def read_humidity(self):
        if self.simulated_data:
            return "%.2f" % random.uniform(20, 30)
        else:
            data = []
            for i in range(0xF7, 0xF7 + 8):
                data.append(self.__bus.read_byte_data(self.__i2c_address, i))
            hum_raw = (data[6] << 8) | data[7]
            return self.__compensate_humidity(hum_raw)

    def read_pressure(self):
        if self.simulated_data:
            return "%.2f" % random.uniform(800, 1200)
        else:
            data = []
            for i in range(0xF7, 0xF7 + 8):
                data.append(self.__bus.read_byte_data(self.__i2c_address, i))
            pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
            return self.__compensate_pressure(pres_raw)

    def __write_reg(self, reg_address, data):
        self.__bus.write_byte_data(self.__i2c_address, reg_address, data)

    def __get_calib_param(self):
        calib = []

        for i in range(0x88, 0x88 + 24):
            calib.append(self.__bus.read_byte_data(self.__i2c_address, i))
        calib.append(self.__bus.read_byte_data(self.__i2c_address, 0xA1))
        for i in range(0xE1, 0xE1 + 7):
            calib.append(self.__bus.read_byte_data(self.__i2c_address, i))

        self.__dig_temperature.append((calib[1] << 8) | calib[0])
        self.__dig_temperature.append((calib[3] << 8) | calib[2])
        self.__dig_temperature.append((calib[5] << 8) | calib[4])
        self.__dig_pressure.append((calib[7] << 8) | calib[6])
        self.__dig_pressure.append((calib[9] << 8) | calib[8])
        self.__dig_pressure.append((calib[11] << 8) | calib[10])
        self.__dig_pressure.append((calib[13] << 8) | calib[12])
        self.__dig_pressure.append((calib[15] << 8) | calib[14])
        self.__dig_pressure.append((calib[17] << 8) | calib[16])
        self.__dig_pressure.append((calib[19] << 8) | calib[18])
        self.__dig_pressure.append((calib[21] << 8) | calib[20])
        self.__dig_pressure.append((calib[23] << 8) | calib[22])
        self.__dig_humidity.append(calib[24])
        self.__dig_humidity.append((calib[26] << 8) | calib[25])
        self.__dig_humidity.append(calib[27])
        self.__dig_humidity.append((calib[28] << 4) | (0x0F & calib[29]))
        self.__dig_humidity.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.__dig_humidity.append(calib[31])

        for i in range(1, 2):
            if self.__dig_temperature[i] & 0x8000:
                self.__dig_temperature[i] = (-self.__dig_temperature[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if self.__dig_pressure[i] & 0x8000:
                self.__dig_pressure[i] = (-self.__dig_pressure[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.__dig_humidity[i] & 0x8000:
                self.__dig_humidity[i] = (-self.__dig_humidity[i] ^ 0xFFFF) + 1

    def __compensate_pressure(self, adc_p):
        global t_fine
        pressure = 0.0

        v1 = (t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.__dig_pressure[5]
        v2 = v2 + ((v1 * self.__dig_pressure[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.__dig_pressure[3] * 65536.0)
        v1 = (((self.__dig_pressure[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)
                ) / 8) + ((self.__dig_pressure[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.__dig_pressure[0]) / 32768

        if v1 == 0:
            return 0
        pressure = ((1048576 - adc_p) - (v2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2
        v1 = (self.__dig_pressure[8] * (((pressure / 8.0)
                                 * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.__dig_pressure[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.__dig_pressure[6]) / 16.0)

        return "%.2f" % (pressure / 100)

    def __compensate_temperature(self, adc_t):
        global t_fine
        v1 = (adc_t / 16384.0 - self.__dig_temperature[0] / 1024.0) * self.__dig_temperature[1]
        v2 = (adc_t / 131072.0 - self.__dig_temperature[0] / 8192.0) * (
            adc_t / 131072.0 - self.__dig_temperature[0] / 8192.0) * self.__dig_temperature[2]
        t_fine = v1 + v2
        temperature = t_fine / 5120.0
        # print "temp : %-6.2f ℃" % (temperature)
        return "%.2f" % (temperature)

    def __compensate_humidity(self, adc_h):
        global t_fine
        var_h = t_fine - 76800.0
        if var_h != 0:
            var_h = (adc_h - (self.__dig_humidity[3] * 64.0 + self.__dig_humidity[4] / 16384.0 * var_h)) * (self.__dig_humidity[1] / 65536.0 * (
                1.0 + self.__dig_humidity[5] / 67108864.0 * var_h * (1.0 + self.__dig_humidity[2] / 67108864.0 * var_h)))
        else:
            return 0
        var_h = var_h * (1.0 - self.__dig_humidity[0] * var_h / 524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0
        # print "hum : %6.2f ％" % (var_h)
        return "%.2f" % (var_h)

    def __setup(self):
        osrs_t = 1  # Temperature oversampling x 1
        osrs_p = 1  # Pressure oversampling x 1
        osrs_h = 1  # Humidity oversampling x 1
        mode = 3  # Normal mode
        t_sb = 5  # Tstandby 1000ms
        filter_off = 0  # Filter off
        spi3w_en = 0  # 3-wire SPI Disable

        ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
        config_reg = (t_sb << 5) | (filter_off << 2) | spi3w_en
        ctrl_hum_reg = osrs_h

        self.__write_reg(0xF2, ctrl_hum_reg)
        self.__write_reg(0xF4, ctrl_meas_reg)
        self.__write_reg(0xF5, config_reg)
