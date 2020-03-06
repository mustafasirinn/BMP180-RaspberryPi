#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import logging
import time

# Sensörümüz için I2C adresini tanımlıyoruz. Bu bilgiyi I2C kurulumu ardından öğrenmiştik.
BMP180_I2CADDR           = 0x77

# datasheetinde bulunan çalışma modlarını tanımlıyoruz. Biz standart modda kullanacağız.
BMP180_ULTRALOWPOWER     = 0
BMP180_STANDARD          = 1
BMP180_HIGHRES           = 2
BMP180_ULTRAHIGHRES      = 3

# BMP180 için datasheette yer alan kalibrasyon katsayılarını tanımlıyoruz.
BMP180_CAL_AC1           = 0xAA   
BMP180_CAL_AC2           = 0xAC   
BMP180_CAL_AC3           = 0xAE   
BMP180_CAL_AC4           = 0xB0   
BMP180_CAL_AC5           = 0xB2   
BMP180_CAL_AC6           = 0xB4   
BMP180_CAL_B1            = 0xB6   
BMP180_CAL_B2            = 0xB8   
BMP180_CAL_MB            = 0xBA   
BMP180_CAL_MC            = 0xBC   
BMP180_CAL_MD            = 0xBE   
BMP180_CONTROL           = 0xF4
BMP180_TEMPDATA          = 0xF6
BMP180_PRESSUREDATA      = 0xF6

# Datasheette yer alan okuma registerları
BMP180_READTEMPCMD       = 0x2E
BMP180_READPRESSURECMD   = 0x34

class BMP180(object):
    def __init__(self, mode=BMP180_STANDARD, address=BMP180_I2CADDR, i2c=None, **kwargs):
        self._logger = logging.getLogger('BMP180')
        # çalışma modunu kontrol ediyoruz.
        if mode not in [BMP180_ULTRALOWPOWER, BMP180_STANDARD, BMP180_HIGHRES, BMP180_ULTRAHIGHRES]:
            raise ValueError('{0} beklenmedik bir mod. BMP180_ULTRALOWPOWER, BMP180_STANDARD, BMP180_HIGHRES ya da BMP180_ULTRAHIGHRES modlarından birini seçiniz.'.format(mode))
        self._mode = mode
        # I2C sensörümüzü kuruyoruz.
        if i2c is None:
            import Adafruit_GPIO.I2C as I2C
            i2c = I2C
        self._device = i2c.get_i2c_device(address, **kwargs)
        # kalibrasyon değerlerini yüklüyoruz.
        self._load_calibration()

    def _load_calibration(self):
        self.cal_AC1 = self._device.readS16BE(BMP180_CAL_AC1)  
        self.cal_AC2 = self._device.readS16BE(BMP180_CAL_AC2)   
        self.cal_AC3 = self._device.readS16BE(BMP180_CAL_AC3)  
        self.cal_AC4 = self._device.readU16BE(BMP180_CAL_AC4)  
        self.cal_AC5 = self._device.readU16BE(BMP180_CAL_AC5)   
        self.cal_AC6 = self._device.readU16BE(BMP180_CAL_AC6)   
        self.cal_B1 = self._device.readS16BE(BMP180_CAL_B1)   
        self.cal_B2 = self._device.readS16BE(BMP180_CAL_B2)  
        self.cal_MB = self._device.readS16BE(BMP180_CAL_MB)   
        self.cal_MC = self._device.readS16BE(BMP180_CAL_MC)   
        self.cal_MD = self._device.readS16BE(BMP180_CAL_MD)    
        self._logger.debug('AC1 = {0:6d}'.format(self.cal_AC1))
        self._logger.debug('AC2 = {0:6d}'.format(self.cal_AC2))
        self._logger.debug('AC3 = {0:6d}'.format(self.cal_AC3))
        self._logger.debug('AC4 = {0:6d}'.format(self.cal_AC4))
        self._logger.debug('AC5 = {0:6d}'.format(self.cal_AC5))
        self._logger.debug('AC6 = {0:6d}'.format(self.cal_AC6))
        self._logger.debug('B1 = {0:6d}'.format(self.cal_B1))
        self._logger.debug('B2 = {0:6d}'.format(self.cal_B2))
        self._logger.debug('MB = {0:6d}'.format(self.cal_MB))
        self._logger.debug('MC = {0:6d}'.format(self.cal_MC))
        self._logger.debug('MD = {0:6d}'.format(self.cal_MD))

    def _load_datasheet_calibration(self):
        # Datasheetteki örnek değerler ile kalibrasyon değerlerini tanımlıyoruz. 
        self.cal_AC1 = 408
        self.cal_AC2 = -72
        self.cal_AC3 = -14383
        self.cal_AC4 = 32741
        self.cal_AC5 = 32757
        self.cal_AC6 = 23153
        self.cal_B1 = 6190
        self.cal_B2 = 4
        self.cal_MB = -32767
        self.cal_MC = -8711
        self.cal_MD = 2868

    def ham_sicaklik_olc(self):
        #Sensörden ham sıcaklık verisini okuyoruz.
        self._device.write8(BMP180_CONTROL, BMP180_READTEMPCMD)
        time.sleep(0.005)  # datasheette yer alan gecikme süresi > 5ms
        raw = self._device.readU16BE(BMP180_TEMPDATA)
        self._logger.debug('Ham sıcaklık 0x{0:X} ({1})'.format(raw & 0xFFFF, raw))
        return raw

    def ham_basinci_olc(self):
        #Sensörden ham basınç seviyesini okuyoruz.
        self._device.write8(BMP180_CONTROL, BMP180_READPRESSURECMD + (self._mode << 6))
        if self._mode == BMP180_ULTRALOWPOWER:
            time.sleep(0.005)
        elif self._mode == BMP180_HIGHRES:
            time.sleep(0.014)
        elif self._mode == BMP180_ULTRAHIGHRES:
            time.sleep(0.026)
        else:
            time.sleep(0.008)
        msb = self._device.readU8(BMP180_PRESSUREDATA)
        lsb = self._device.readU8(BMP180_PRESSUREDATA+1)
        xlsb = self._device.readU8(BMP180_PRESSUREDATA+2)
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self._mode)
        self._logger.debug('Ham basınç 0x{0:04X} ({1})'.format(raw & 0xFFFF, raw))
        return raw

#UP = Basınç verisi (16 - 19 bit)
#UT = Sıcaklık verisi (16 bit)

#Debugging için datasheet değerleri:
#    UT = 27898
#    UP = 23843

    def basinc_olc(self):
        #Ham basınç değerini Pascal haline getiriyoruz.
        UT = self.ham_sicaklik_olc()
        UP = self.ham_basinci_olc()
        
        # Datasheette yer alan hesaplamaları kullanarak aşağıda kodumuza entegre ediyoruz.
        # Gerçek sıcaklık katsayısı B5'i hesaplıyoruz.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
        B5 = X1 + X2
        self._logger.debug('B5 = {0}'.format(B5))
        # Basıncı hesaplıyoruz.
        B6 = B5 - 4000
        self._logger.debug('B6 = {0}'.format(B6))
        X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
        X2 = (self.cal_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.cal_AC1 * 4 + X3) << self._mode) + 2) // 4
        self._logger.debug('B3 = {0}'.format(B3))
        X1 = (self.cal_AC3 * B6) >> 13
        X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
        self._logger.debug('B4 = {0}'.format(B4))
        B7 = (UP - B3) * (50000 >> self._mode)
        self._logger.debug('B7 = {0}'.format(B7))
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        self._logger.debug('Basınç: {0} Pa'.format(p))
        return p