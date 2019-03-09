

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from datetime import datetime, timedelta

import time
import subprocess
import json
import urllib2

# Setup
octoPrintHostname = 'octopi'
apiKey            = ''

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    try:
        jobData = json.load(urllib2.urlopen('http://' + octoPrintHostname + '/api/job?apikey=' + apiKey))
        printerData = json.load(urllib2.urlopen('http://' + octoPrintHostname + '/api/printer?history=false&apikey=' + apiKey))
    except:
        draw.text((x, top), "Printer is offline",  font=font, fill=255)
        disp.image(image)
        disp.display()
        time.sleep(.10)
        continue

    if jobData["state"] == "Printing":
        sec = timedelta(seconds=int(jobData["progress"]["printTimeLeft"]))
        d = datetime(1,1,1) + sec

        daysLeft    = ("%d" % (d.day-1))
        hoursLeft   = ("%d" % (d.hour))
        minutesLeft = ("%d" % (d.minute))

        if int(daysLeft) > 0:
            timeLeftString = daysLeft + "d " + hoursLeft + "h " + minutesLeft + "m"
        elif int(hoursLeft) > 0:
            timeLeftString = hoursLeft + "h " + minutesLeft + "m"
        else:
            timeLeftString = minutesLeft + "m"

    draw.text((x, top),    "State: " + str(jobData["state"]),  font=font, fill=255)
    draw.text((x, top+10), "Tool:  " + str(printerData["temperature"]['tool0']['actual']),  font=font, fill=255)
    draw.text((x, top+20), "Bed:   " + str(printerData["temperature"]['bed']['actual']),  font=font, fill=255)

    if jobData["state"] == "Printing":
        percentDone = int(jobData["progress"]["completion"])
        draw.line((x, top+32, x+128, top+32), fill=255)
        draw.text((x, top+40),    "Left:  " + timeLeftString,  font=font, fill=255)
        draw.text((x+102, top+55),    str(percentDone) + "%",  font=font, fill=255)
        draw.rectangle((x, top+56, x+100, top+64), outline=255, fill=0)
        draw.rectangle((x, top+56, x+(100/100*percentDone), top+64), outline=255, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)
