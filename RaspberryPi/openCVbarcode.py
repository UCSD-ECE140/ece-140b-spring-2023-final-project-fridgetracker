# Based off of work at https://note.nkmk.me/en/python-opencv-barcode/
# FridgeTracker Group
# Barcode scanning and api usage on Raspberry Pi

import RPi.GPIO as GPIO
import cv2, requests
from Dependencies.PCF8574 import PCF8574_GPIO #import necessary files for LCD
from Dependencies.Adafruit_LCD1602 import Adafruit_CharLCD #import necessary files for LCD

camera_id = 0   # default value is 0 if you only have one camera
delay = 1

bd = cv2.barcode.BarcodeDetector()
cap = cv2.VideoCapture(camera_id)

barcodes = [0]*5

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

addButton = 12
delButton = 16

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(addButton, GPIO.IN)
    GPIO.setup(delButton, GPIO.IN)

def scan_barcode(button):
    while True:
        ret, frame = cap.read()
        if ret:
            ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
            if ret_bc:
                
                for s, p in zip(decoded_info, points):
                    
                    # if a valid barcode value is found
                    if s:                    
                        # shift data through a 5 element list each time a new barcode is detected, with the newest barcode at index 0
                        # and the oldest at index 4. If a new barcode is detected, the list shifts up by one (data @ index 0 -> index 1),
                        # the barcode previously at index 4 is discarded, and the new barcode is added at index 0
                        for i in reversed(range(len(barcodes))):
                            barcodes[i] = barcodes[i-1]
                        barcodes[0] = s

                # if all elements in the barcodes list are the same (aka the scanner has scanned the same barcode number 5 times in a row)
                if len(set(barcodes)) == 1:
                    # retrieve product data from api
                    rawdata = requests.get('https://api.barcodelookup.com/v3/products?barcode=%s&key=6zusy8frdfgq2uriti6lu5v74ws6n5' % barcodes[0]).json()
                    productdata = rawdata['products'][0]
                    
                    # display product data
                    operation = 'Adding\n' if button == addButton else 'Deleting\n'
                    display = operation + productdata['title']
                    return display

        if cv2.waitKey(delay) & GPIO.input(button):   # exit loop if the button is pressed after one second of usage
            return 'Cancelling Operation'

def loop():
    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns

    while True:
        lcd.setCursor(0,0)  # set cursor position
        if GPIO.input(addButton):
            lcd.message(scan_barcode(addButton))
        if GPIO.input(delButton):
            lcd.message(scan_barcode(delButton))

if __name__ == '__main__':
    setup()
    loop()