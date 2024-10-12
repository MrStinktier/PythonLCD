from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import time
from os import system
system("sudo killall pigpiod")
time.sleep(5)
system("sudo pigpiod")
import pigpio
from smbus2 import SMBus
import subprocess
from datetime import datetime

bus = SMBus(1)
# Change the address based on your i2cdetect result
lcd = CharLCD('PCF8574', 0x27)

pi = pigpio.pi()

SENSOR_PIN = 15

bewegungssensor_state = True
bus.write_byte(0x27, 0b00000000)
backlight_on = False
starttime = 19

old_text_string_line1 = "lol"
old_text_string_line2 = "lel"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SENSOR_PIN, GPIO.IN)

try:
    def update_lcd(old_text, new_text, line):
        max_len = min(len(old_text), len(new_text))

        for i in range(max_len):
            if old_text[i] != new_text[i]:
                lcd.cursor_pos = (line, i)
                lcd.write_string(new_text[i])

        if len(new_text) > len(old_text):
            for i in range(len(old_text), len(new_text)):
                lcd.cursor_pos = (line, i)
                lcd.write_string(new_text[i])

        old_text = new_text

    def normalrun():
#wenn der bewegungssensor geht, zwischen diesen kommentaren alles rauskommentieren...
#        global backlight_on
#        localtime = datetime.now().strftime("%H:%M")
#        if localtime <= "16:00" or localtime >= "21:00":
#            if backlight_on:
#                bus.write_byte(0x27, 0b00000000)
#                backlight_on = False
#        else:
#            if not backlight_on:
#                bus.write_byte(0x27, 0b00000001)
#                backlight_on = True
#wenn der bewegungssensor geht, zwischen diesen kommentaren alles rauskommentieren...
            new_text_string_line1 = datetime.now().strftime("  %H:%M %d-%m")
            update_lcd(old_text_string_line1, new_text_string_line1, line=0)
            new_text_string_line2 = str("     " + subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE).stdout.decode("utf-8").split("=")[1])
            update_lcd(old_text_string_line2, new_text_string_line2, line=1)
            

    def sensor_check():
        global bewegungssensor_state
        global backlight_on
        global starttime
        localtime = datetime.now().strftime("%H:%M")
        if localtime <= "8:00" or localtime >= "21:00":
            if backlight_on:
                bus.write_byte(0x27, 0b00000000)
                backlight_on = False
        else:
            if bewegungssensor_state:
                if backlight_on:
                    bus.write_byte(0x27, 0b00000000)
                    backlight_on = False
                if (pi.read(SENSOR_PIN)):
                    starttime = localtime
                    bewegungssensor_state = False
            else:
                if (pi.read(SENSOR_PIN)):
                    starttime = localtime
                    bewegungssensor_state = False
                if not backlight_on:
                    bus.write_byte(0x27, 0b00000001)
                    backlight_on = True
                if (str(int(starttime.split(":")[0] + starttime.split(":")[1]) + 3)) <= str(int(localtime.split(":")[0] + localtime.split(":")[1])):
                    bewegungssensor_state = True
                    time.sleep(0.25)
                else:
                    normalrun()

    while True:
        sensor_check()
        time.sleep(0.5)  # Display for 0.5 seconds
except KeyboardInterrupt:
    pass
finally:
    time.sleep(0.1)
    GPIO.cleanup()
    lcd.clear()  # Clear the LCD when exiting
    lcd.close()  # Close the LCD connection
    bus.write_byte(0x27, 0b00000000)
