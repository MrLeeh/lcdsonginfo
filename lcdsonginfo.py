#!/usr/bin/python
#*-* coding: utf-8 *-*

# Todo
# * display brightness timout, i.e. turn off display when stopped or paused
#   for a while

import subprocess
import textwrap
from time import sleep
from adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate


def _utf8_to_lcd(s):
    """
    Replace special characters (umlauts) by the appropriate HD44780 character
    code.

    """
    out = s.replace('ö', '\xef')
    out = out.replace('Ö', '\xef')
    out = out.replace('ä', '\xe1')
    out = out.replace('Ä', '\xe1')
    out = out.replace('ü', '\xf5')
    out = out.replace('Ü', '\xf5')
    return out


class TextScroller:
    """
    Class for scrolling text.

    """
    text = ''
    position = 0
    textLength = 0

    def __init__(self, initialText, textLength):
        self.text = initialText
        self.textLength = textLength

    def scroll(self):
        doubleText = self.text + '     ' + self.text
        scrolledText = doubleText[self.position:len(doubleText)]
        self.position = self.position + 1

        # We add five extra spaces between each complete text scroll.
        if self.position > len(self.text) + 4 :
                self.position = 0

        return scrolledText

    def setNewText(self, newText):
        self.text = newText
        self.position = 0


# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()
lcd.begin(16,2)
lcd.clear()
lcd.backlight(lcd.ON)

# Poll buttons
btn = (lcd.LEFT, lcd.UP, lcd.DOWN, lcd.RIGHT, lcd.SELECT)

lastArtistSong = ''
scroller = TextScroller('', 16)

while True:
    # Get current status and playtime
    process = subprocess.Popen('mpc', shell=True, stdout=subprocess.PIPE)
    status = process.communicate()[0]
    statusLines = status.split('\n')
    statusLines = map(_utf8_to_lcd, statusLines)

    # Check if mpc returns more that one line plus an extra,
    # in that case we dont have stopped the music and can parse
    # additional information
    if len(statusLines) > 2:
        # Extract the songName (first line)
        # songName = statusLines[0]
        # Aubrey - Stripped the Station Name and slowed the scrolling down.
        songN = statusLines[0]
        if ":" in songN:
           songName = statusLines[0].split(':',1)[1].strip()
        if ":" not in songN:
           songName = statusLines[0]

        # Extract play status
        playStatus = statusLines[1].split(' ',1)[0].strip()

        # Aubrey added: Strip it properly:
        times = statusLines[1].split(']',1)[1].strip()
        times = times.split(' ',1)[1].strip()
        times = times.split(' ',1)[0].strip()
        times = times.split('/',1)[0].strip()

        # Aubrey - Changed the Statusline with VOL/TM:
        infoLine = statusLines[2].split(':',1)[1].strip()
        infoLine = infoLine.split('%',1)[0].strip()
        times = ('TM=' + times + ' Vol=' + infoLine + '%')
    else:
        songName = ''
        playStatus = '[stopped]'
        times = '0:00/0:00 (0%)'

    lcd.setCursor(0,0)

    artistSong = (songName)
    if artistSong != lastArtistSong:
        scroller.setNewText(artistSong)
        lastArtistSong = artistSong

    # Aubrey - If the songname is shorter than 16, just display it,
    # else, scroll it...
    if songName != '':
        if len(songName) < 16:
            lcd.message(artistSong + '                            \n' + \
            (times + '     ')[0:16])
        else:
            lcd.message(scroller.scroll()[0:16] + '\n' + \
            (times + '     ')[0:16])
    else:
        lcd.message((playStatus + '             ')[0:16] + '\n' + \
        (times + '     ')[0:16])

    # Poll the buttons most of the sleep time, to make them responsive the plan is to
    # poll the buttons for 400ms and then update the status on the display
    # If we sleep for 40ms between each poll time and have five buttons that equals to 200 ms
    # Two iterations of this gives us 400 ms.
    # for i in range (0, 10):
    for i in range (0, 5):
        for b in btn:
            if lcd.buttonPressed(b):
                if b is lcd.RIGHT:
                    subprocess.Popen('mpc next', shell=True)
                    sleep(0.2) # Sleep a little extra to avoid dubble registrations
                if b is lcd.LEFT:
                    subprocess.Popen('mpc prev', shell=True)
                    sleep(0.2) # Sleep a little extra to avoid dubble registrations
                if b is lcd.UP:
                    # subprocess.Popen('mpc play', shell=True)
                    subprocess.Popen('mpc volume +1', shell=True)
                    # sleep(0.2) # Sleep a little extra to avoid dubble registrations
                if b is lcd.DOWN:
                    # subprocess.Popen('mpc stop', shell=True)
                    subprocess.Popen('mpc volume -1', shell=True)
                    sleep(0.2) # Sleep a little extra to avoid dubble registrations
                if b is lcd.SELECT:
                    subprocess.Popen('mpc toggle', shell=True)
                    sleep(0.2) # Sleep a little extra to avoid dubble registrations
                break
        sleep(0.04)
