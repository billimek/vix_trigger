# Purpose
The purpose of this script is to provide a daily 'report' on the VIX index for possible buy & sell triggers based on the `Larry Connors 'CVR' reversal indicators`.

This particular implementation examines the recent 15-period VIX daily high & low values and applies the following rules:

* When the VIX index makes a NEW 15 day low AND closes ABOVE its open, it signals a sell in the market
* When the VIX index makes a NEW 15 high low AND closes BELOW its open, it signals a buy in the market

It makes use of the yahoo stock quotes python library to scrape the necessary data from the Yahoo Finance information (is intended to be run at 4:15pm ET in order to ensure close-of-market data is collected)

The script will create a URL for the specific chart from stockcharts.com linked to an in-line image of the same chart and sent in an email.

The script is intended to be every weekday at 4:!5pm ET


## Example output
