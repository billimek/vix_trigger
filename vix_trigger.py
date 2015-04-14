#!/opt/local/bin/python2.7


###/usr/bin/env python

import sys
import datetime
import time
import smtplib
import urllib2
import StringIO
import ystockquote

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from PIL import Image

COMMASPACE = ', '

# SYMBOL
SYMBOL = 'VIX'

# number of days of historical data to fetch (not counting today)
days_back = 15

email_from = 'email_address'
email_to = ['email_address', 'email_address2']

# current datetime
current_datetime = datetime.datetime.now()

# URL to use for both image and link itself. TODO: need to clean this up
# so it doesn't need to be defined twice.
chart_image_url = 'http://stockcharts.com/c-sc/sc?s=' + '$' + SYMBOL + '&p=D&yr=0&mn=0&dy=' + str(days_back) + '&id=p87197006241'
chart_url = 'http://stockcharts.com/h-sc/ui?s=' + '$' + SYMBOL + '&p=D&yr=0&mn=0&dy=' + str(days_back) + '&id=p87197006241'

# initialize the buy & sell indicators
buy = False
sell = False


def isNewHigh(high, data):
    """
    Returns True if the 'high' is higher than any of the highs in the data
    array passed in. Otherwise returns False
    """
    for i in range(1, days_back):
        if float(data[i][2]) >= float(high):
            return False
    return True

def isNewLow(low, data):
    """
    Returns True if the 'low' is lower than any of the lows in the data
    array passed in. Otherwise returns False
    """
    for i in range(1, days_back):
        if (float(data[i][3]) <= float(low)):
            return False
    return True

def isCurrentHigherThanOpen(current, open):
    """
    Simple check to see if the current price is greater than the open price
    """
    return float(current) > float(open)

def isCurrentLowerThanOpen(current, open):
    """
    Simple check to see if the current price is lower than the open price
    """
    return float(current) < float(open)

def sendEmail():
    """
    Send out an email (if necessary)
    """
    # Set-up the chart email
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = email_from
    msgRoot['To'] = COMMASPACE.join(email_to)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(body)
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(body_html, 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    msgImage = MIMEImage(chart_image)

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    s = smtplib.SMTP('localhost')
    s.sendmail(email_from, email_to, msgRoot.as_string())
    s.quit()


"""
Fetch data (from yahoo) and determine if this is a reversal indicator
"""
# yesterday's date
end = current_datetime - datetime.timedelta(days=1)
# 30 days ago from today
start = current_datetime - datetime.timedelta(days=30)

# fetch the historical data from yahoo
data = ystockquote.get_historical_prices('^' + SYMBOL, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))

# validate that we have enough historical data to continue
if len(data) < days_back:
    print 'Not enough historical data available to continue (need at least 15 days of market data)'
    sys.exit(1)

current = ystockquote.get_price('^' + SYMBOL)
open = ystockquote.get_open('^' + SYMBOL)
high = ystockquote.get_high('^' + SYMBOL)
low = ystockquote.get_low('^' + SYMBOL)

# if the current price is higher than the open and today is a new 15-day low,
# then this is a SELL indicator
if (isCurrentHigherThanOpen(current, open) & isNewLow(low, data)):
    #print 'today is a 15-day low (' + str(low) + ') & the current price (' + str(current) + ') is higher than the open (' + str(open) + ')'
    sell = True

# if the current price is lower than the open and today is a new 15-day high,
# then this is a BUY indicator
if (isCurrentLowerThanOpen(current, open) & isNewHigh(high, data)):
    #print 'today is a 15-day high (' + str(high) + ') & the current price (' + str(current) + ') is lower than the open (' + str(open) + ')'
    buy = True

# For testing
#buy = True
#current_datetime = (current_datetime - datetime.timedelta(hours=3))

if (buy | sell):
    # reversal indicator is true.
    if buy:
        subject = SYMBOL + ' BUY indicator triggered!'
        body = 'Today (' + current_datetime.strftime('%Y-%m-%d') + ') ' + SYMBOL + ' has a new 15-day high ($' + str(high) + ') & the current price ($' + str(current) + ') is lower than the open ($' + str(open) + ')\n\n====>This is a ' + SYMBOL + ' BUY indicator!'
        body_html = 'Today (' + current_datetime.strftime('%Y-%m-%d') + ') ' + SYMBOL + ' has a new 15-day high ($' + str(high) + ') & the current price ($' + str(current) + ') is lower than the open ($' + str(open) + ')<br><br><b>===>This is a ' + SYMBOL + ' BUY indicator!</b><br><br><a href="' + chart_url + '"> <img src="cid:image1" border="0"></a>'
    if sell:
        subject = SYMBOL + ' SELL indicator triggered!'
        body = 'Today (' + current_datetime.strftime('%Y-%m-%d') + ') ' + SYMBOL + ' has a new 15-day low ($' + str(low) + ') & the current price ($' + str(current) + ') is higher than the open ($' + str(open) + ')\n\n====>This is a ' + SYMBOL + ' SELL indicator!'
        body_html = 'Today (' + current_datetime.strftime('%Y-%m-%d') + ') ' + SYMBOL + ' has a new 15-day low ($' + str(low) + ') & the current price ($' + str(current) + ') is higher than the open ($' + str(open) + ')<br><br><b>===>This is a ' + SYMBOL + ' SELL indicator!</b><br><br><a href="' + chart_url + '"> <img src="cid:image1" border="0"></a>'
# this is not a reversal trigger
else:
    subject = 'Daily ' + SYMBOL+ ' for ' + current_datetime.strftime('%Y-%m-%d')
    body = ''
    body_html = '<a href="' + chart_url + '"> <img src="cid:image1" border="0"></a><br>'
# is current time between 16:00 and 16:15 or is this a reversal indicator?
#if ((buy | sell) | (datetime.time(16,00) < current_datetime.time() < datetime.time(16,15))):
# Fetch the chart from stockcharts.com
# fetch the chart image


headers={'User-agent' : 'Mozilla/5.0'}
chart_image = urllib2.urlopen(urllib2.Request(chart_image_url, None, headers)).read()
try:
    im = Image.open(StringIO.StringIO(chart_image))
    im.verify()
except Exception, e:
    print 'The image is not valid'
sendEmail()

'''
print 'start date is: ' + str(start)
print 'end date is: ' + str(end)
print 'current time is: ' + str(current_datetime)
print 'current hour is: ' + str(current_datetime.hour)
print 'current minute is: ' + str(current_datetime.minute)
print 'current second is: ' + str(current_datetime.second)
print 'number of days of actual market data retrieved is: ' + str((len(data) - 1))
print 'Current price: ' + str(current)
print 'Open price: ' + str(open)
print 'High price: ' + str(high)
print 'Low price: ' + str(low)

# Loop through the previous 14-days of data (the first item in the data array
# is omitted because it is just header information
print 'the previous 14-day of historical data:'
for i in range(1, days_back):
    print data[i][0] + ': High:' + data[i][2] + ' Low:' + data[i][3]
print subject
print body
'''

