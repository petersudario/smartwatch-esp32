
import ssd1306
import machine, onewire, ds18x20, time
from machine import Pin, ADC, I2C, RTC, PWM
from time import sleep
import network
import time
import dht
import ujson
from umqtt.simple import MQTTClient

MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "wokwi-temperature"

thresholdValue = 400 # Set the threshold value for led turn on
buzzer = PWM(Pin(2), freq=440, duty =512)

rtc = RTC()
now = (2023, 6, 5, 1, 21, 55, 0, 0)
rtc.init(now)

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
variavel = True

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')

while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")

def sonido (freq, sleep):
	buzzer.freq(freq)
	buzzer.duty(512)
	time.sleep(sleep)

while variavel == True:
    for i in range(4):
        ds_sensor.convert_temp()
        for rom in roms:
            timestamp = rtc.datetime()
            tempo = str(timestamp[4]) + ':' + str(timestamp[5]) + ':' + str(timestamp[6])
            dia = str(timestamp[2]) + '/' + str(timestamp[1]) + '/' + str(timestamp[0])
            if ds_sensor.read_temp(rom) > 37 or ds_sensor.read_temp(rom) < 36:
                sonido(1024, 1)
                sonido(1, 0)
                message = ujson.dumps({
                    "temp": ds_sensor.read_temp(rom),
                    "date": dia
                })

                print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
                client.publish(MQTT_TOPIC, message)

                oled.fill(0)
                oled.text('Temperatura', 10, 10)
                oled.text('anormal', 10, 20)
                oled.text(str(ds_sensor.read_temp(rom)) + ' graus', 10, 30)
                oled.text(tempo, 10, 40)
                oled.show()
                
            else:
                oled.fill(0)
                oled.text(str(ds_sensor.read_temp(rom)), 10, 10)
                oled.text('Normal', 10, 20) 

                oled.text(tempo, 10, 40)
                oled.show()


