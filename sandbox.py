from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from dataManage import getSingleMostRecentByTicker
import re
import pdb

watchStrats = []
buyStrats = []
sellStrats = []
sellStopStrats = []

# Breaks one strategy per line into a dictionary and returns the first strategy encountered, or None if no strategies are found.
def parseStrategies():
    f = open('strategies.txt', 'r')
    lineNum = 1
    for line in f:
        components = line.split(",")
        if line[0] ==  "\n" or line[0] == "#":
            lineNum += 1
            continue
        if (len(components) != 5):
            print "Parse error! Incorrect number of parameters on line %i [strategyParser.py]. Expected 5, found %i. Skipping." % (lineNum, len(components))
            lineNum += 1
            continue
        watchs = components[0]
        watch = watchs.split("&")
        buys = components[1]
        buy = buys.split("&")
        sells = components[2]
        sell = sells.split("&")
        sellStops = components[3]
        sellStop = sellStops.split("&")
        expireTime = components[4]

        for x in watch:
            watchStrats.append(_parseComponent(x.strip(), lineNum))
        for x in buy:
            buyStrats.append(_parseComponent(x.strip(), lineNum))
        for x in sell:
            sellStrats.append(_parseComponent(x.strip(), lineNum))
        for x in sellStop:
            sellStopStrats.append(_parseComponent(x.strip(), lineNum))
        return expireTime
        lineNum += 1
    print "Parse error! No valid strategy was found in strategies.txt! Exiting."
    return None

# Takes a single component from a strategy (a single buy, sell, or watch strategy) and separates it into data name, data val, and comparison operator.
def _parseComponent(component, line = -1):
    parts = component.split(" ")
    if (len(parts) != 3):
        if (line == -1):
            print "Parse error! Incorrect number of parameters on unknown line [strategies.txt]. Expected 3, found %i. Skipping." % (lineNum, len(parts))
        else:
            print "Parse error! Incorrect number of parameters on line %i [strategyParser.py]. Expected 3, found %i. Skipping." % (line, len(parts))
    data = parts[0]
    comparator = parts[1]
    val = parts[2]

    # Special handling for case where test is over multiple days
    # Gets the index where the number in the comparator exists.
    numberIndex = re.search("\d", comparator)
    # If there is a number return the dictionary with a day count (which is incremented) and day total (which is constant)
    if (numberIndex != None):
        return { "data": data, "compr": comparator, "val": val, "DAY_TOTAL": int(comparator[numberIndex.start():]), "dayCounter": int(comparator[numberIndex.start():]) }
    # Otherwise, return the dictionary with a day total set to -1. No dayCounter is necessary since day total is the value used to see if counting days is necessary.
    else:
        return { "data": data, "compr": comparator, "val": val, "DAY_TOTAL": -1 }

def comprWithStock(stock, yesterday, state):
    if state == "WAIT":
        for strat in watchStrats:
            # If a strategy does not pass, return false.
            if not _comprWithStock(stock, strat, yesterday):
                return False
        # Otherwise, stock passed al strategies, so return true. Since state is changing, also reset all counting days for the next time the strat is used.
        _resetStratCountdowns(watchStrats)
        return True
    if state == "WATCH":
        for strat in buyStrats:
            if not _comprWithStock(stock, strat, yesterday):
                return False
        _resetStratCountdowns(buyStrats)
        return True
    if state == "BUY":
        doSell = True
        doSellOnStop = True
        for strat in sellStrats:
            if not _comprWithStock(stock, strat, yesterday):
                doSell = False
                break
        # If any sell strategy does not pass, we are not selling based on these strategies (doSell set to False and thus this conditional is not met), but we may still want to sell based on the sellStop strategy.
        if doSell:
            _resetStratCountdowns(sellStrats)
            _resetStratCountdowns(sellStopStrats)
            return True
        else:
            for strat in sellStopStrats:
                # If any sell stop strategy does not pass, we are not selling based on these strategies, so we can safely return False.
                if not _comprWithStock(stock, strat, yesterday):
                    return False
            # Otherwise, all sellStop strategies were passed even though the sell strategy was not passed. Return true as a result.
            _resetStratCountdowns(sellStrats)
            _resetStratCountdowns(sellStopStrats)
            return True


'''
stock is the stock being evaluated from "today"
yesterday is the stock being evaluated from "yesterday", necessary if we need to compare today's values to yesterday's.
'''
def _comprWithStock(stock, c, yesterday):
    if (stock.get(c["data"]) == None):
        # print "Error! Unparseable strategy %s %s %s! Returning false." % (c["data"], c["compr"], c["val"])
        return False

    # Initial values for "data", which relates to data from the stock, and "val", which relates to the test value.
    data = stock.get(c["data"])
    if c["val"] == "+":
        val = "+"
    elif (c["val"] == "-"):
        val = "-"
    else:
        val = float(c["val"])

    # TODO Handle the day count resetting if the state changes

    # Special handling for case where standard deviation is part of the calculation
    if ("stdevofmacd" in c["data"]):
        substr = c["data"][11:]
        macdavgStr = "macdAVG" + substr
        stdevStr = "stdevofmacd" + substr
        if (stock.get(macdavgStr) == None or stock.get(stdevStr) == None):
            return False
        # stdevofmacd200 < -1.0 converts to
        # val = macdavg + (-1.0) * stdevofmacd200
        val = float(stock.get(macdavgStr)) + (float(c["val"]) * stock.get(stdevStr))
        data = stock.get("macd")
        # compares macd < val

    if (c["compr"][:1] == ">"):
        if (data > val):
            # If we are not counting days, or if we are counting days all days for the duration have consecutively proven true, return true.
            if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                return True
            # We are counting days and we need to see another day's information. Return false meanwhile.
            else:
                c["dayCounter"] -= 1
                return False
        # Reset the day count if we are counting days. In either case, return false.
        else:
            if c["DAY_TOTAL"] != -1:
                c["dayCounter"] = c["DAY_TOTAL"]
            return False
    if (c["compr"][:1] == "<"):
        if (data < val):
            if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                return True
            else:
                c["dayCounter"] -= 1
                return False
        else:
            c["dayCounter"] = c["DAY_TOTAL"]
            return False
    if (c["compr"][:2] == ">="):
        if (data >= val):
            if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                return True
            else:
                c["dayCounter"] -= 1
                return False
        else:
            c["dayCounter"] = c["DAY_TOTAL"]
            return False
    if (c["compr"][:2] == "<="):
        if (data <= val):
            if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                return True
            else:
                c["dayCounter"] -= 1
                return False
        else:
            c["dayCounter"] = c["DAY_TOTAL"]
            return False
    if (c["compr"][:1] == "="):
        if (data == val):
            if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                return True
            else:
                c["dayCounter"] -= 1
                return False
        else:
            c["dayCounter"] = c["DAY_TOTAL"]
            return False
    # Handles the / symbol, which indicates a change in slope from yesterday to today
    if (c["compr"][:1] == "/"):
        # There is no yesterday (first stock in list)
        if (yesterday == None):
            return False
        # Today's value is greater than yesterday's
        if (c["val"] == "+"):
            if (data > yesterday.get(c["data"])):
                if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                    return True
                else:
                    c["dayCounter"] -= 1
                    return False
            else:
                c["dayCounter"] = c["DAY_TOTAL"]
                return False
        # Today's value is less than yesterday's
        elif (c["val"] == "-"):
            if (data < yesterday.get(c["data"])):
                if c["DAY_TOTAL"] == -1 or c["dayCounter"] <= 1:
                    return True
                else:
                    c["dayCounter"] -= 1
                    return False
            else:
                c["dayCounter"] = c["DAY_TOTAL"]
                return False
        else:
            print "Parse error! Found unexpected symbol %s from %s stock (%s). Was not + or -." % (c["val"], stock["abbreviation"], stock["date"])
    print "Error! Unparseable strategy %s %s %s! Returning false." % (c["data"], c["compr"], c["val"])
    return False

def _resetStratCountdowns(strats):
    for strat in strats:
        if (strat["DAY_TOTAL"] != -1):
            strat["dayCounter"] = strat["DAY_TOTAL"]
