import pymongo
from pprint import pprint
import sys
import pdb

# By default, we need SMA of intervals 12, 20, 26, 50, 200
# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given.
def calcSMA(stocks, intervals = [12, 20, 26, 50, 200], smaOf = "close"):
    ret = []
    index = 0
    maxInterval = max(intervals)
    prevVals = [0] * maxInterval
    firstLoop = True  # Set and kept to true after first loop

    for stock in stocks:

        prevVals[index] = stock.get(smaOf)
        # Test to see if we have filled prevVals with "maxInterval" count worth of data.
        if firstLoop and index == maxInterval - 1:
            firstLoop = False
        for interval in intervals:
            smaStr = u"sma" + str(interval)
            if stock.get(smaStr) == None:
                # If it is not the first loop, then we have enough data for sure. Additionally, if it is the first loop and index is larger than interval, we have enough data (this allows us to calculate smas over an interval smaller than maxInterval)
                if not firstLoop or index >= interval - 1:
                    smaData = _SMAcalculator(interval, index, prevVals)
                    stock[smaStr] = smaData
                # We don't have enough data.
                else:
                    stock[smaStr] = None

        # Increment to next index value for prevVals, looping around maxInterval
        index = (index + 1) % maxInterval
        # Put updated stock in array to be returned and repushed to db
        ret.append(stock)
    return ret

# | 5 | 6 | 7 | 8 | 9 | 10 | -> arr[]
# days would be the number of elements to take the average over, say 3. Will never be greater than len(arr)
# index would be the last place in the array to take the average of, say 2. It is the point in the array called arr where the average will be taken. Will never be greater than len(arr)
# The sample values would take the average of arr[2], arr[1], arr[0] -> 6.
def _SMAcalculator(days, index, arr):
    sum = 0
    for num in range(index, index - days, -1):
        num = (len(arr) + num) % len(arr) # Index which wraps around to front of array after encountering the end
        sum = float(sum + float(arr[num]))
    avg = float(sum / float(days))
    return avg


# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given.
def calcEMA(stocks, intervals = [12, 20, 26, 50, 200]):
    ret = []
    prevEMAs = [None] * len(intervals)
    for stock in stocks:
    # We need an SMA first, to calculate the first EMA. So find the first SMA and store it.
        for x in range(len(intervals)):
            smaStr = u"sma" + str(intervals[x])
            emaStr = u"ema" + str(intervals[x])
            # If we find the first ocurrence of a stock's SMA, we can use it to start calculating EMAs.
            if prevEMAs[x] == None and stock.get(smaStr) != None:
                prevEMAs[x] = stock.get(smaStr)
                stock[emaStr] = prevEMAs[x] # Sets the first EMA to be the SMA
            # If the first SMA has already been found, we can use it to calculate future EMAs.
            elif prevEMAs[x] != None:
                stock[emaStr] = _EMAcalculator(stock, prevEMAs[x], intervals[x])
                prevEMAs[x] = stock[emaStr]
            # If the first SMA was never found, EMA cannot be calculated. Note that this will occur in the case that EMA calculation over an interval is attempted for a stock whose SMA over the same interval has not been calculated.
            else:
                stock[emaStr] = None
        ret.append(stock)
    return ret

# Stock is the stock dictionary to have EMA values added to. emaVal is the previous day's EMA (if no EMAs have been calculated yet, this is the SMA instead). Time period is the time over which the SMA was calculated and the EMA will also be calculated.
def _EMAcalculator(stock, emaVal, timePeriod):
    multiplier = float(2 / float(timePeriod + 1))
    newEMA = float((float(stock["close"]) - emaVal) * multiplier + emaVal)
    return newEMA

# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given.
def calcMACD(stocks):
    ret = []
    for stock in stocks:
        # The two values we need are present, so we can calculate MACD.
        if stock.get("ema12") != None and stock.get("ema26") != None:
            macdVal = stock.get("ema12") - stock.get("ema26")
            stock[u"macd"] = macdVal
        else:
            stock[u"macd"] = None
        ret.append(stock)
    return ret


# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given.
def calcROC(stocks, timeInterval):
    ret = []
    index = 0
    count = 0
    pastXClose = [0] * timeInterval
    for stock in stocks:
        rocStr = u"roc" + str(timeInterval)
        if count < timeInterval:
            count += 1
            stock[rocStr] = None
        else:
            pastClose = float(pastXClose[index])
            roc = float((float(stock["close"]) - pastClose) / pastClose)
            stock[rocStr] = roc
        pastXClose[index] = stock["close"]
        index = (index + 1) % timeInterval
        ret.append(stock)
    return ret

# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given. Time interval is the number of days in the %K stochastic's range (defaulted to 5). dInterval is the number of days of SMA of %K to take to get %D
def calcStochastic(stocks, timeInterval = 5, dInterval = 3):
    ret = []
    pastXLows = [float(0)] * timeInterval
    pastXHighs = [float(0)] * timeInterval
    pastXKs = [float(0)] * dInterval
    count = 0
    countD = 0
    index = 0
    indexD = 0
    stockStrK = ""
    stockStrD = ""
    for stock in stocks:
        stockStrK = u"stochastic" + str(timeInterval) + u"K"
        stockStrD = u"stochastic" + str(dInterval) + u"D"
        pastXLows[index] = stock["low"]
        pastXHighs[index] = stock["high"]
        if count < timeInterval - 1:
            count += 1
            stock[stockStrK] = None
            stock[stockStrD] = None
        else:
            lowestLow = min(pastXLows)
            highestHigh = max(pastXHighs)
            # Handle the rare case where low volume stocks don't change. Avoids divide by 0 error.
            if float(highestHigh) - float(lowestLow) == 0:
                return None
            else:
                K = float((float(stock["close"]) - float(lowestLow)) / (float(highestHigh) - float(lowestLow)) * 100)
            stock[stockStrK] = K
            if countD < dInterval:
                countD += 1
                stock[stockStrD] = None
            else:
                smaVal = _SMAcalculator(3, 3, pastXKs)
                stock[stockStrD] = smaVal
            pastXKs[indexD] = stock[stockStrK]
            indexD = (indexD + 1) % dInterval
        index = (index + 1) % timeInterval
        ret.append(stock)
    return (ret, stockStrK, stockStrD)

# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given. Interval is the number of days over which the average of the MACD will be taken.
def calcMACDavg(stocks, interval = 200):
    ret = []
    count = 0
    index = 0
    avgmacdStr = u"macdAVG" + str(interval)
    pastXMACD = [0] * interval
    for stock in stocks:
        # Skip the first few stocks which do not have a macd
        if (stock.get("macd") != None):
            if count < interval - 1:
                count += 1
                stock[avgmacdStr] = None
            else:
                avg = sum(pastXMACD) / float(interval)
                stock[avgmacdStr] = avg
            pastXMACD[index] = stock["macd"]
            index = (index + 1) % interval
        else:
            stock[avgmacdStr] = None
        ret.append(stock)
    return (ret, avgmacdStr)

# Precondition: stocks is a collection of stocks of a single ticker ordered by date (oldest first) is given.
# ASSUMES THAT A VALID deviationOf STRING IS GIVEN!!! DOES NOT ERROR HANDLE FOR BAD STRINGS
# Interval is the number of days over which the standard deviation of the key "deviationOf" will be taken.
def calcStandardDeviation(stocks, interval = 200, deviationOf = "macd"):
    ret = []
    index = 0
    count = 0
    SDStr = u"stdevof" + deviationOf + str(interval)
    pastSD = [0] * interval
    for stock in stocks:
        # Skip the first few stocks which do not have a {"deviationOf"}
        if (stock.get(deviationOf) != None):
            pastSD[index] = stock[deviationOf]
            if count < interval - 1:
                count += 1
                stock[SDStr] = None
            else:
                avg = sum(pastSD) / float(interval)
                pastSDCpy = list(pastSD) # Make a copy of ret
                for x in range(len(pastSDCpy)):
                    pastSDCpy[x] = (pastSDCpy[x] - avg)**2
                newAvg = sum(pastSDCpy) / float(interval)
                sdev = newAvg**0.5
                stock[SDStr] = sdev
            index = (index + 1) % interval
        else:
            stock[SDStr] = None
        ret.append(stock)
    return (ret, SDStr)
