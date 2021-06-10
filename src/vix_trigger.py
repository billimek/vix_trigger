#!/usr/bin/env python
import datetime
import json
import smtplib
import sys
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import yfinance as yf
from pandas.core.internals.construction import to_arrays

COMMASPACE = ", "

# SYMBOL
SYMBOL = "VIX"

# number of days of historical data to fetch (not counting today)
days_back = 15

email_from = "Insert EMAIL HERE"
email_to = ["INSERT EMAIL here"]

# current datetime
current_datetime = datetime.datetime.now()

# URL to use for both image and link itself. TODO: need to clean this up
# so it doesn't need to be defined twice.
chart_image_url = (
    "http://stockcharts.com/c-sc/sc?s="
    + "$"
    + SYMBOL
    + "&p=D&yr=0&mn=0&dy="
    + str(days_back)
    + "&id=p87197006241"
)
chart_url = (
    "http://stockcharts.com/h-sc/ui?s="
    + "$"
    + SYMBOL
    + "&p=D&yr=0&mn=0&dy="
    + str(days_back)
    + "&id=p87197006241"
)

# initialize the buy & sell indicators
buy, sell = False, False


def isNewHigh(high, data):

    """
    Returns True if the 'high' is higher than any of the highs in the data
    array passed in. Otherwise returns False
    """
    highs = data.get("High")
    for i in highs:
        try:
            if (float(i)) >= float(high):
                return False
        except ValueError:
            return False
    return True


def isNewLow(low, data):
    """
    Returns True if the 'low' is lower than any of the lows in the data
    array passed in. Otherwise returns False
    """
    lows = data.get("Low")
    print(low)
    for i in lows:
        try:
            if float(i) <= float(low):
                return False
        except ValueError:
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
    msgRoot = MIMEMultipart("related")
    msgRoot["Subject"] = subject
    msgRoot["From"] = email_from
    msgRoot["To"] = COMMASPACE.join(email_to)
    msgRoot.preamble = "This is a multi-part message in MIME format."

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart("alternative")
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(body)
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(body_html, "html")
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    msgImage = MIMEImage(chart_image)

    # Define the image's ID as referenced above
    msgImage.add_header("Content-ID", "<image1>")
    msgRoot.attach(msgImage)

    s = smtplib.SMTP("localhost")
    s.sendmail(email_from, email_to, msgRoot.as_string())
    s.quit()


"""
Fetch data (from yahoo) and determine if this is a reversal indicator
"""
# yesterday's date
end = current_datetime - datetime.timedelta(days=1)
# 30 days ago from today
start = current_datetime - datetime.timedelta(days=30)

vix = yf.Ticker(f"^{SYMBOL}")
data = vix.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
data.drop(labels=["Volume", "Dividends", "Stock Splits"], axis=1, inplace=True)
index = data.columns
data = data.reset_index().drop("Date", axis=1)
data = data.to_dict("list")
print(data)
# parsed_json = json.loads(data)


all_data = vix.history(period="1mo", interval="1d")
# validate that we have enough historical data to continue

if len(data) < days_back:
    print(
        "Not enough historical data available to continue (need at least 15 days of market data)"
    )
    # sys.exit(1)


current = vix.info
current = current.get("regularMarketPrice")

opens = all_data["Open"]
open_list = opens.to_list()
newest_open = open_list[-1]

high = all_data["High"]
high_list = high.to_list()
newest_high = high_list[-1]

low = all_data["Low"]
low_list = low.to_list()
newest_low = low[-1]


# if the current price is higher than the open and today is a new 15-day low,
# then this is a SELL indicator
if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, data):
    # print 'today is a 15-day low (' + str(low) + ') & the current price (' + str(current) + ') is higher than the open (' + str(open) + ')'
    sell = True

# if the current price is lower than the open and today is a new 15-day high,
# then this is a BUY indicator
if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, data):
    # print 'today is a 15-day high (' + str(high) + ') & the current price (' + str(current) + ') is lower than the open (' + str(open) + ')'
    buy = True
# For testing
# buy = True
# current_datetime = (current_datetime - datetime.timedelta(hours=3))
if buy | sell:
    # reversal indicator is true.
    if buy:
        subject = SYMBOL + " BUY indicator triggered!"
        body = (
            "Today ("
            + current_datetime.strftime("%Y-%m-%d")
            + ") "
            + SYMBOL
            + " has a new 15-day high ($"
            + str(high)
            + ") & the current price ($"
            + str(current)
            + ") is lower than the open ($"
            + str(open)
            + ")\n\n====>This is a "
            + SYMBOL
            + " BUY indicator!"
        )
        body_html = (
            "Today ("
            + current_datetime.strftime("%Y-%m-%d")
            + ") "
            + SYMBOL
            + " has a new 15-day high ($"
            + str(high)
            + ") & the current price ($"
            + str(current)
            + ") is lower than the open ($"
            + str(open)
            + ")<br><br><b>===>This is a "
            + SYMBOL
            + ' BUY indicator!</b><br><br><a href="'
            + chart_url
            + '"> <img src="cid:image1" border="0"></a>'
        )
    if sell:
        subject = SYMBOL + " SELL indicator triggered!"
        body = (
            "Today ("
            + current_datetime.strftime("%Y-%m-%d")
            + ") "
            + SYMBOL
            + " has a new 15-day low ($"
            + str(low)
            + ") & the current price ($"
            + str(current)
            + ") is higher than the open ($"
            + str(open)
            + ")\n\n====>This is a "
            + SYMBOL
            + " SELL indicator!"
        )
        body_html = (
            "Today ("
            + current_datetime.strftime("%Y-%m-%d")
            + ") "
            + SYMBOL
            + " has a new 15-day low ($"
            + str(low)
            + ") & the current price ($"
            + str(current)
            + ") is higher than the open ($"
            + str(open)
            + ")<br><br><b>===>This is a "
            + SYMBOL
            + ' SELL indicator!</b><br><br><a href="'
            + chart_url
            + '"> <img src="cid:image1" border="0"></a>'
        )
# this is not a reversal trigger
else:
    subject = "Daily " + SYMBOL + " for " + current_datetime.strftime("%Y-%m-%d")
    body = ""
    body_html = '<a href="' + chart_url + '"> <img src="cid:image1" border="0"></a><br>'
# is current time between 16:00 and 16:15 or is this a reversal indicator?
# if ((buy | sell) | (datetime.time(16,00) < current_datetime.time() < datetime.time(16,15))):
# Fetch the chart from stockcharts.com
# fetch the chart image

payload = {}
headers = {"redirect_uri": "google.com", "User-Agent": "Mozilla/5.0"}

r = requests.request("GET", chart_image_url, headers=headers, data=payload)
print(r.status_code)
file = open("image.png", "wb")
file.write(r.content)
file.close()
chart_image = r.content
sendEmail()


def print_data_summary():
    print("start date is: " + str(start))
    print("end date is: " + str(end))
    print("current time is: " + str(current_datetime))
    print("current hour is: " + str(current_datetime.hour))
    print("current minute is: " + str(current_datetime.minute))
    print("current second is: " + str(current_datetime.second))
    print("number of days of actual market data retrieved is: " + str((len(data) - 1)))
    print("Current price: " + str(current))
    print("Open price: " + str(open))
    print("High price: " + str(high))
    print("Low price: " + str(low))


# Loop through the previous 14-days of data (the first item in the data array
# is omitted because it is just header information
# print('the previous 14-day of historical data:')
# for i in range(1, days_back):
#    print(data[i][0] + ': High:' + data[i][2] + ' Low:' + data[i][3])
print(subject)
print(body)
