#!/usr/bin/env python
import datetime
import yfinance as yf
import streamlit as st
import requests

st.write(" Welcome to the VIX buy or sell trigger ")

COMMASPACE = ", "

# The VIX ticker
SYMBOL = "VIX"

# Number of days of historical data to fetch (not counting today)
days_back = 15

# Current datetime
current_datetime = datetime.datetime.now()

# URL to VIX chart image
chart_image_url = (
        "http://stockcharts.com/c-sc/sc?s="
        + "$"
        + SYMBOL
        + "&p=D&yr=0&mn=0&dy="
        + str(days_back)
        + "&id=p87197006241"
)


def isNewHigh(high, data):
    """
    Returns True if the 'high' is higher than any of the highs in the data
    array passed in. Otherwise returns False
    Parameters:
    high (float): Today's highest price for the VIX index
    data (list): All price data for the VIX index 15 days back
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
    Parameters:
    low (float): Today's lowest price for the VIX index
    data (list): All price data for the VIX index 15 days back
    """
    lows = data.get("Low")
    for i in lows:
        try:
            if float(i) <= float(low):
                return False
        except ValueError:
            return False
    return True


def isCurrentHigherThanOpen(current, today_open):
    """
    Simple check to see if the current price is greater than the open price
    Parameters:
    current (float): The current price for the VIX index
    open (float): Today's opening price
    """
    return float(current) > float(today_open)


def isCurrentLowerThanOpen(current, today_open):
    """
    Simple check to see if the current price is lower than the open price
    Parameters:
    current (float): The current price for the VIX index
    open (float): Today's opening price
    """
    return float(current) < float(today_open)


# Yesterday's date
end = current_datetime - datetime.timedelta(days=1)
# 30 days ago from today
start = current_datetime - datetime.timedelta(days=30)

# Retrieve historical data from the VIX index via Yahoo's API
vix = yf.Ticker(f"^{SYMBOL}")
data = vix.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
data.drop(labels=["Volume", "Dividends", "Stock Splits"], axis=1, inplace=True)
index = data.columns
data = data.reset_index().drop("Date", axis=1)
data = data.to_dict("list")

# Collect all data ones more for one month
all_data = vix.history(period="1mo", interval="1d")

# Validate that we have enough historical data to continue
if len(data['Open']) < days_back:
    print(
        "Not enough historical data available to continue (need at least 15 days of market data)"
    )

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


def run_code():
    buy, sell = False, False

    # if the current price is higher than the open and today is a new 15-day low, then this is a SELL indicator
    if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, data):
        sell = True

    # if the current price is lower than the open and today is a new 15-day high, then this is a BUY indicator
    if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, data):
        buy = True

    if buy | sell:
        if buy:
            st.write("BUY indicator triggered!\n",
                     f"The VIX has a new 15-day high (${newest_high})\n",
                     f"& the current price (${current}) is lower\n",
                     f"than the open (${newest_open})\n",
                     "This is a BUY indicator")
        if sell:
            st.write("SELL indicator triggered!\n"
                     f"The VIX has a new 15-day low (${newest_low})\n"
                     f"& the current price (${current}) is higher\n"
                     f"than the open (${open})\n"
                     "This is a SELL indicator")

    else:
        st.write("No trigger was activated.\n",
                 f"The current VIX index price is (${current})")

    payload = {}
    headers = {"redirect_uri": "google.com", "User-Agent": "Mozilla/5.0"}
    r = requests.request("GET", chart_image_url, headers=headers, data=payload)
    file = open("./images/daily_vix_normal.png", "wb")
    file.write(r.content)
    file.close()
    chart_image = r.content
    st.image(chart_image)


result_1 = st.button("Click here to see if you should buy or sell today")
if result_1:
    run_code()


def print_data_summary():
    st.write("Start date is: ", str(start.date()))
    st.write("End date is: ", str(end.date()))
    st.write("Current time is: ", str(current_datetime))
    st.write("Current hour is: ", str(current_datetime.hour))
    st.write("Current minute is: ", str(current_datetime.minute))
    st.write("Current second is: ", str(current_datetime.second))
    st.write("Number of days of actual market data retrieved is: ", str((len(data['Open']) - 1)))
    st.write("Current price: $", str(current))
    st.write("Open price: ", str(newest_open))
    st.write("High price: ", str(newest_high))
    st.write("Low price: ", str(newest_low))


result_2 = st.button("Click here to get data used in the VIX trigger")
if result_2:
    print_data_summary()
