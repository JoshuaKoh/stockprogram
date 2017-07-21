from datetime import datetime
from dateutil.relativedelta import relativedelta
from dataManage import insertStocks, getSingleMostRecentByTicker
from jnius import autoclass
import urllib
import csv
import io
import json
from pprint import pprint

dateFormat = "%Y-%m-%d %H:%M:%S"
abbrvDateFormat = "%Y-%m-%d"
SATURDAY = 5
SUNDAY = 6

DateFormat = autoclass('java.text.DateFormat')
SimpleDateFormat = autoclass('java.text.SimpleDateFormat')
String = autoclass('java.lang.String')
Date = autoclass('java.util.Date')

# Given a valid stock ticker string, and digits for years, months, and days ago, returns a URL for the Yahoo stock data from the range of years, months, and days ago until the most recent data (most recent market day).
def _makeUrl(ticker, yearsAgo, monthsAgo, daysAgo):
    start = datetime.now() - relativedelta(years = yearsAgo, months = monthsAgo, days = daysAgo)
    end = datetime.now()

    month = start.month - 1
    if (month <= 9):
        monthStart = str(month).zfill(1)
    else:
        monthStart = str(month)
    day = start.day - 1
    if (day <= 9):
        dayStart = str(day).zfill(1)
    else:
        dayStart = str(day)

    month = end.month - 1
    if (month <= 9):
        monthEnd = str(month).zfill(1)
    else:
        monthEnd = str(month)
    day = end.day - 1
    if (day <= 9):
        dayEnd = str(day).zfill(1)
    else:
        dayEnd = str(day)

    yearStart = str(start.year)
    yearEnd = str(end.year)

    # url = "http://real-chart.finance.yahoo.com/table.csv?s=" + ticker + "&a=" + monthStart + "&b=" + dayStart + "&c=" + yearStart + "&d=" + monthEnd + "&e=" + dayEnd + "&f=" + yearEnd + "&g=d&ignore=.csv"

    dateStart = "%s-%s-%s" % (yearStart, monthStart, dayStart)
    dateEnd = "%s-%s-%s" % (yearEnd, monthEnd, dayEnd)
    sdf = SimpleDateFormat('yyyy-MM-dd')

    dateStartObj = sdf.parse(dateStart)
    msStart = dateStartObj.getTime()
    startCode = msStart/1000

    dateEndObj = sdf.parse(dateEnd)
    msEnd = dateEndObj.getTime()
    endCode = msEnd/1000

    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?formatted=true&lang=en-US&region=US&period1=%s&period2=%s&interval=1d&events=div%%7Csplit&corsDomain=finance.yahoo.com" % (ticker, startCode, endCode)
    return url


# Returns an array of comma separated rows of the stock data off the url
def _getDataFromUrl(url):
    response = urllib.urlopen(url).read()
    jsonDict = json.loads(response)
    raw = jsonDict["chart"]["result"][0]["indicators"]["quote"][0]
    dates = jsonDict["chart"]["result"][0]["timestamp"]

    data = []
    total = len(dates)
    for i in range(0, total):
        row = []
        date = SimpleDateFormat("yyyy-MM-dd").format(Date(dates[i]*1000))
        openData = raw["open"][i]
        closeData = raw["close"][i]
        highData = raw["high"][i]
        lowData = raw["low"][i]
        volumeData = raw["volume"][i]

        row.append(date)
        row.append(openData)
        row.append(highData)
        row.append(lowData)
        row.append(closeData)
        row.append(volumeData)
        data.append(row)
    return data

# Single function to perform all actions in dataFetch. Returns an array of all stock data.
def updateStocks(db):
    f = open('stocks.txt', 'r')
    bulk = db.stocks.initialize_unordered_bulk_op()
    bulkCounter = 0

    for line in f:
        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in line):
            line = line[:-1]
        if (line[:2] == "//"):
            break

        mostRecent = getSingleMostRecentByTicker(line)
        # Ticker has not been added, get URL three years of data
        if mostRecent.count() == 0:
            u = _makeUrl(line, 3, 0, 0)
        # Ticker has been added, at least some data exists, get URL for missing data
        else:
            dtNow = datetime.now()
            if dtNow.weekday() == SATURDAY:
                dtNow -= timedelta(days=1)
            elif dtNow.weekday() == SUNDAY:
                dtNow -= timedelta(days=2)
            nowDate = dtNow.strftime(dateFormat)[:10]
            print nowDate
            print abbrvDateFormat
            print mostRecent[0]["date"]
            datesMissing = relativedelta(datetime.strptime(nowDate, abbrvDateFormat), datetime.strptime(mostRecent[0]["date"], abbrvDateFormat))
            # Test if last update was yesterday. If so, there is no need to update again
            if datesMissing.years == 0 and datesMissing.months == 0 and datesMissing.days <= 1:
                print "updateStocks: %s is already fully updated with base data." % line
                continue

            u = _makeUrl(line, datesMissing.years, datesMissing.months, datesMissing.days)

        dFromU = _getDataFromUrl(u)
        if dFromU[0][0].startswith("<"):
            print "updateStocks: Received bad ticker %s. Skipping!" % line
            continue
        else:
            print "updateStocks: New data for %s." % line
        for d in dFromU:
            if d[0] != "Date":
                # Handle relevant stock info here
                today = datetime.now().strftime(dateFormat)
                # newStock = Stock(u, line, d[0], today, d[1], d[2], d[3], d[4], d[5], d[6])
                #bulk.insert({"url": u, "abbreviation": line, "date": d[0], "download_date": today, "open": d[1], "high": d[2], "low": d[3], "close": d[4], "volume": d[5], "adjClose": d[6]})
                bulk.insert({"url": u, "abbreviation": line, "date": d[0], "download_date": today, "open": d[1], "high": d[2], "low": d[3], "close": d[4], "volume": d[5]})
                bulkCounter += 1
            if (bulkCounter / 500 > 0):
                bulk.execute()
                bulk = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

        # print "Updated %s with %s" % (line, result)

    f.close()

def getMostRecentUpdateDate():
    f = open('config.txt', 'r')
    test = f.readline()
    f.close()
    try:
        ret = datetime.strptime(test, abbrvDateFormat)
    except ValueError:
        ret = datetime.strptime('1970-11-2', abbrvDateFormat)

    return ret

def setMostRecentUpdateDate():
    f = open('config.txt', 'w')
    f.write(datetime.now().strftime(abbrvDateFormat))
    f.close()
