import mraa
import time
import smtplib
from email.mime.text import MIMEText

led = mraa.Gpio(23)
beeper = mraa.Gpio(31)
beeper.dir(mraa.DIR_OUT)
beeper.write(0)
led.dir(mraa.DIR_OUT)
led.write(0)
soundoff = mraa.Gpio(29)
soundoff.dir(mraa.DIR_IN)
snooze = mraa.Gpio(33)
snooze.dir(mraa.DIR_IN)
ledstate = 0
blinktime = time.time()
alarmtime = time.time()
countsnoozes = 0
led.write(0)
beeper.write(0)
