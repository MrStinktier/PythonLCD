from RPLCD.i2c import CharLCD
from smbus2 import SMBus
import subprocess
from datetime import datetime
import time

bus = SMBus(1)
# Change the address based on your i2cdetect result
lcd = CharLCD('PCF8574', 0x27)

backlight_on = False

old_text_string_line1 = "lol"
old_text_string_line2 = "lel"

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

    while True:
        localtime = datetime.now().strftime("%H:%M")
        if localtime <= "16:00" or localtime >= "21:00":
            if backlight_on:
                bus.write_byte(0x27, 0b00000000)
                backlight_on = False
        else:
            if not backlight_on:
                bus.write_byte(0x27, 0b00000001)
                backlight_on = True
            new_text_string_line1 = datetime.now().strftime("  %H:%M %d-%m")
            update_lcd(old_text_string_line1, new_text_string_line1, line=0)
            new_text_string_line2 = str("     " + subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("=")[1])
            update_lcd(old_text_string_line2, new_text_string_line2, line=1)
        time.sleep(0.5)  # Display for 0.5 seconds
except KeyboardInterrupt:
    pass
finally:
    time.sleep(0.1)
    lcd.clear()  # Clear the LCD when exiting
    lcd.close()  # Close the LCD connection
    bus.write_byte(0x27, 0b00000000)
