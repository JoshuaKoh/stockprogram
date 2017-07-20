#!/user/bin/evn python

from dataFetch import *
from dataManage import *
import pymongo
from pprint import pprint
from dbco import *
from formulae import *
from strategyParser import *
import pdb
from os import remove
from os import path
import time
import sys
from datetime import datetime, timedelta



''' TODO
- When printing to datelog, also print today's close, tomorrow's open
'''
# EDIT-ABLE CONSTANTS FOR EQUATIONS
SMA_INTERVAL = [12, 20, 26, 50, 200] # Default [12, 20, 26, 50, 200]
EMA_INTERVAL = [12, 20, 26, 50, 200] # Default [12, 20, 26, 50, 200]
ROC_INTERVAL = [5, 9, 10, 13] # Default [5, 9, 10, 13]
PRICE_SOURCE = "open"
# validateStocks = False

dateFormat = "%Y-%m-%d %H:%M:%S"
buyDateFormat = "%Y-%m-%d"
MONDAY = 0
SATURDAY = 5
SUNDAY = 6
'''
IN UPDATE: Used to determine stocks with not enough entries. Calculations for these are skipped.
IN TODAY TEST: Used to identify number of days to go back in time to start testing for today. Should be large enough to accomodate a full cycle of the testing strategy, and smaller than the total number of stocks available.
'''
TEST_START_COUNT = 365

mostRecentUpdateDate = getMostRecentUpdateDate()


def updateStockVals():
    startTime = datetime.now()
    # TODO Currently, we pass around the entirety of a stock's data (based on its ticker). Make it so that old records are deleted, or only sections of the data are passed (after the first pass. The first pass must use all the data to label as much as possible.). -> Temporary solution to this is to run clearStocks() every run to use only 3 years (default) of data, rather than the entire collection.
    f = open('stocks.txt', 'r')

    doNotUpdate = []

    # # # # # # # #
    #   PASS 1    #
    # # # # # # # #

    bulk = db.stocks.initialize_unordered_bulk_op()
    bulkCounter = 0 # Can't do more than 1000 bulk ops at a time.
    doBulkExecute = False
    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        # Most recent ticker from last update does not have data. Do a full update. This test only occurs on PASS 1.
        mostRecent = getSingleMostRecentByTicker(ticker)
        global mostRecentUpdateDate
        if mostRecentUpdateDate.weekday() == SATURDAY:
            mostRecentUpdateDate = mostRecentUpdateDate - timedelta(days=1)
        elif mostRecentUpdateDate.weekday() == SUNDAY:
            mostRecentUpdateDate = mostRecentUpdateDate - timedelta(days=2)

        # Test if most recent stock has all data updated. If so, skipped.
        # TODO Test if stock from two days ago has all data updated. If so, update only one day.
        if mostRecent.count() == 0 or \
          (datetime.strptime(mostRecent[0].get("date"), buyDateFormat) == mostRecentUpdateDate and \
          mostRecent[0].get("sma200") != None and \
          mostRecent[0].get("ema200") != None and \
          mostRecent[0].get("roc13") != None and \
          mostRecent[0].get("stochastic3D") != None and \
          mostRecent[0].get("macdAVG200") != None and \
          mostRecent[0].get("stdevofmacd200") != None):
            print "updateStockVals: %s fully updated, skipping." %ticker
            doNotUpdate.append(ticker)
            continue
        # Test if stock has not enough elements to even bother with. If so, skipped.
        elif getByTickerInOrder(ticker).count() < TEST_START_COUNT:
            print "updateStockVals: %s is low volume, skipping." %ticker
            doNotUpdate.append(ticker)
            continue
        # Otherwise, at least one stock is getting updated, so make sure data write is executed.
        doBulkExecute = True

        print "updateStockVals: pass 1:\t%s <- SMA, EMA, ROC, STOCHASTIC." %ticker

        stockHolder = []
        stockHolder = calcSMA(getByTickerInOrder(ticker), SMA_INTERVAL)
        # if mostRecent[0].get("sma12") == None or mostRecent[0].get("sma200") == None:
        for s in stockHolder:
            bulk.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { "sma12": s["sma12"], "sma20": s["sma20"], "sma26": s["sma26"], "sma50": s["sma50"], "sma200": s["sma200"] }})
            bulkCounter += 1
            if (bulkCounter % 500 == 0 and doBulkExecute):
                bulk.execute()
                bulk = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

        stockHolder = []
        for interval in ROC_INTERVAL:
            stockHolder = calcROC(getByTickerInOrder(ticker), interval)
            rocStr = u"roc" + str(interval)
            # if mostRecent[0].get(rocStr) == None:
            for s in stockHolder:
                bulk.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { rocStr : s[rocStr] }})
                bulkCounter += 1
                if (bulkCounter % 500 == 0 and doBulkExecute):
                    bulk.execute()
                    bulk = db.stocks.initialize_unordered_bulk_op()
                    bulkCounter = 0

        stockHolder = []
        stochasticResults = calcStochastic(getByTickerInOrder(ticker))
        if stochasticResults == None:
            print "updateStockVals: %s is a low volume stock!" % ticker
        else:
            stockHolder = stochasticResults[0]
            stockStrK = stochasticResults[1]
            stockStrD = stochasticResults[2]
            # if mostRecent[0].get(stockStrK) == None or mostRecent[0].get(stockStrD):
            for s in stockHolder:
                bulk.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { stockStrK : s[stockStrK], stockStrD : s[stockStrD] }})
                bulkCounter += 1
                if (bulkCounter % 500 == 0 and doBulkExecute):
                    bulk.execute()
                    bulk = db.stocks.initialize_unordered_bulk_op()
                    bulkCounter = 0

    if doBulkExecute and bulkCounter != 0:
        bulk.execute()

    # # # # # # # #
    #   PASS 2    #
    # # # # # # # #

    bulk2 = db.stocks.initialize_unordered_bulk_op()
    bulkCounter = 0
    doBulkExecute = False
    f.seek(0)
    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        # If we decided ticker is updated or low volume in PASS 1, skip.
        if ticker in doNotUpdate:
            continue
        # Otherwise, at least one stock is being updated, so be sure write executes.
        doBulkExecute = True

        print "updateStockVals: pass 2:\t%s <- EMA." %ticker

        # mostRecent = getSingleMostRecentByTicker(ticker)

        stockHolder = []
        stockHolder = calcEMA(getByTickerInOrder(ticker), EMA_INTERVAL)
        # if mostRecent[0].get("ema12") == None:
        for s in stockHolder:
            bulk2.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { "ema12": s["ema12"], "ema20": s["ema20"], "ema26": s["ema26"], "ema50": s["ema50"], "ema200": s["ema200"] }})
            bulkCounter += 1
            if (bulkCounter % 500 == 0 and doBulkExecute):
                bulk2.execute()
                bulk2 = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

    if doBulkExecute and bulkCounter != 0:
        bulk2.execute()

    # # # # # # # #
    #   PASS 3    #
    # # # # # # # #

    bulk3 = db.stocks.initialize_unordered_bulk_op()
    bulkCounter = 0
    doBulkExecute = False
    f.seek(0)
    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        if ticker in doNotUpdate:
            continue
        doBulkExecute = True

        print "updateStockVals: pass 3:\t%s <- MACD." %ticker

        # mostRecent = getSingleMostRecentByTicker(ticker)

        stockHolder = []
        stockHolder = calcMACD(getByTickerInOrder(ticker))
        macdStr = "macd"
        # if mostRecent[0].get("macd") == None:
        for s in stockHolder:
            bulk3.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { macdStr : s[macdStr] }})
            bulkCounter += 1
            if (bulkCounter % 500 == 0 and doBulkExecute):
                bulk3.execute()
                bulk3 = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

    if doBulkExecute and bulkCounter != 0:
        bulk3.execute()


    # # # # # # # #
    #   PASS 4    #
    # # # # # # # #

    bulk4 = db.stocks.initialize_unordered_bulk_op()
    bulkCounter = 0
    doBulkExecute = False
    f.seek(0)
    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        if ticker in doNotUpdate:
            continue
        doBulkExecute = True

        print "updateStockVals: pass 4:\t%s <- macdAvg, stdev." %ticker

        stockHolder = []
        MACDavgResults = calcMACDavg(getByTickerInOrder(ticker))
        # if mostRecent[0].get(MACDavgStr) == None:
        stockHolder = MACDavgResults[0]
        MACDavgStr = MACDavgResults[1]
        for s in stockHolder:
            bulk4.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { MACDavgStr : s[MACDavgStr] }})
            bulkCounter += 1
            if (bulkCounter % 500 == 0 and doBulkExecute):
                bulk4.execute()
                bulk4 = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

        stockHolder = []
        stdevResults = calcStandardDeviation(getByTickerInOrder(ticker))
        # if mostRecent[0].get(stdevStr) == None:
        stockHolder = stdevResults[0]
        stdevStr = stdevResults[1]
        for s in stockHolder:
            bulk4.find({"_id": s["_id"]}).upsert().update_one( { '$set' : { stdevStr : s[stdevStr] }})
            bulkCounter += 1
            if (bulkCounter % 500 == 0 and doBulkExecute):
                bulk4.execute()
                bulk4 = db.stocks.initialize_unordered_bulk_op()
                bulkCounter = 0

    if doBulkExecute and bulkCounter != 0:
        bulk4.execute()

        # # Most recent ticker from last update has data. Do a smaller update.
        # else:
        #     print "skipping"
        #     lastDate = (mostRecentUpdateDate - timedelta(days=max(SMA_INTERVAL))).strftime(buyDateFormat)

        #     stockHolder = []
        #     stockHolder = calcSMA(getByTickerInOrder(ticker), SMA_INTERVAL, lastDate)
        #     if mostRecent[0].get("sma12") == None or mostRecent[0].get("sma200") == None:
        #         for s in stockHolder:
        #             bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { "sma12": s["sma12"], "sma20": s["sma20"], "sma26": s["sma26"], "sma50": s["sma50"], "sma200": s["sma200"] }})

        #     stockHolder = []
        #     lastDate = (mostRecentUpdateDate - timedelta(days=4)).strftime(buyDateFormat)
        #     stockHolder = calcEMA(getByTickerInOrder(ticker), EMA_INTERVAL, lastDate)
        #     if mostRecent[0].get("ema12") == None:
        #         for s in stockHolder:
        #             bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { "ema12": s["ema12"], "ema20": s["ema20"], "ema26": s["ema26"], "ema50": s["ema50"], "ema200": s["ema200"] }})

        #     stockHolder = []
        #     for interval in ROC_INTERVAL:
        #         stockHolder = calcROC(getByTickerInOrder(ticker), interval)
        #         rocStr = u"roc" + str(interval)
        #         if mostRecent[0].get(rocStr) == None:
        #             for s in stockHolder:
        #                 bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { rocStr : s[rocStr] }})

        #     stockHolder = []
        #     stockHolder = calcMACD(getByTickerInOrder(ticker))
        #     if mostRecent[0].get("macd") == None:
        #         for s in stockHolder:
        #             bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { "macd" : s["macd"] }})


        #     stockHolder = []
        #     stochasticResults = calcStochastic(getByTickerInOrder(ticker))
        #     if stochasticResults == None:
        #         print "%s is a low volume stock!" % ticker
        #     else:
        #         stockHolder = stochasticResults[0]
        #         stockStrK = stochasticResults[1]
        #         stockStrD = stochasticResults[2]
        #         if mostRecent[0].get(stockStrK) == None or mostRecent[0].get(stockStrD):
        #             for s in stockHolder:
        #                 bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { stockStrK : s[stockStrK], stockStrD : s[stockStrD] }})

        #     stockHolder = []
        #     MACDavgResults = calcMACDavg(getByTickerInOrder(ticker), 200)
        #     if mostRecent[0].get(MACDavgStr) == None:
        #         stockHolder = MACDavgResults[0]
        #         MACDavgStr = MACDavgResults[1]
        #         for s in stockHolder:
        #             bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { MACDavgStr : s[MACDavgStr] }})


        #     stockHolder = []
        #     stdevResults = calcStandardDeviation(getByTickerInOrder(ticker))
        #     if mostRecent[0].get(stdevStr) == None:
        #         stockHolder = stdevResults[0]
        #         stdevStr = stdevResults[1]
        #         for s in stockHolder:
        #             bulk.find({"_id": s["_id"]}).upsert().update( { '$set' : { stdevStr : s[stdevStr] }})

        # if not bulk.execute():
        #     print "FATAL ERROR, COULD NOT WRITE STOCK DATA TO DB.\nClear DB before re-running."

    f.close()
    setMostRecentUpdateDate()
    endTime = datetime.now()
    print "updateStockVals: Update took %.3f seconds" % ((endTime - startTime).total_seconds())

def runStrategies():
    startTime = datetime.now()

    fwName = "results.txt"
    flName = "datelog.txt"
    # fvName = "validForToday.txt"
    f = open('stocks.txt', 'r')
    fw = open(fwName, 'w')
    fl = open(flName, 'w')
    # fv = open(fvName, 'a')
    fw.write("Test done on %s\n" % datetime.now().strftime(dateFormat))
    fl.write("Test done on %s\n" % datetime.now().strftime(dateFormat))

    # validStocks = fv.read().split('\n')
    # Twofold command which stores strategies and also gives the time that a stock may on the watch list without being bought before being relegated to the waitlist.
    expireTimeConstant = parseStrategies()
    # Check if strategy parsing had an error. parseStrageties() prints an error, so no need to do so here.
    if expireTimeConstant == None:
        return
    else:
        expireTimeConstant = int(expireTimeConstant)

    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        print "strategies: Now running strategy tests on %s" %ticker

        stocks = getByTickerInOrder(ticker)

        fl.write("=== %s ===" % ticker)

        buy = {}
        yesterday = None
        if (expireTimeConstant == -1):
            ENABLE_EXPIRE_TIME = False
        else:
            ENABLE_EXPIRE_TIME = True
            expireTime = expireTimeConstant
        wins = 0
        winVals = []
        losses = 0
        lossVals = []
        daysBetweenBuyAndSellWin = []
        daysBetweenBuyAndSellLoss = []
        combinedDays = []
        state = "WAIT"
        for stock in stocks:
            # WAIT means that the stock is on the WAIT LIST
            # If comprWithStock is true, stock goes on WATCH LIST
            # If comprWithStock is false, stock stays in WAIT LIST
            if state == "WAIT":
                if comprWithStock(stock, yesterday, state):
                    state = "WATCH"
                    if ENABLE_EXPIRE_TIME:
                        expireTime = expireTimeConstant

            # WATCH means the stock is on the WATCH LIST
            # If comprWithStock is false, stock stays on WATCH LIST until time expires, after which it is returned to WAIT LIST
            elif state == "WATCH":
                # If comprWithStock is true, stock goes on BUY LIST
                if comprWithStock(stock, yesterday, state):
                    # print "BOUGHT. State: %s. Macd: %.3f. Yesterday Macd: %.3f." % (state, float(stock["macd"]), float(yesterday["macd"]))
                    buy = stock
                    state = "BUY"
                # Getting here means that the watchlisted stock did not pass the strategy. Return stock to WAIT LIST if time has expired, otherwise do nothing.
                if ENABLE_EXPIRE_TIME:
                    if expireTime < 0:
                        state = "WAIT"
                    # Getting here means the watchlisted stock's time has not yet expired. Decrement expire time.
                    else:
                        expireTime -= 1

            # BUY means the stock is on the BUY LIST
            # If comprWithStock is false, stock stays on the BUY LIST.
            elif state == "BUY":
                # If comprWithStock is true, stock is sold and returns to waiting
                if comprWithStock(stock, yesterday, state):
                    # print "SOLD. State: %s. Macd: %.3f. Yesterday Macd: %.3f." % (state, float(stock["macd"]), float(yesterday["macd"]))

                    delta = float(stock[PRICE_SOURCE]) - float(buy[PRICE_SOURCE])
                    # Used to determine the number of days between buy and sell
                    dateDelta = datetime.strptime(stock["date"], buyDateFormat) - datetime.strptime(buy["date"], buyDateFormat)
                    # If price change is positive, we made some profit
                    if (delta > 0):
                        wins += 1
                        winVals.append(delta / float(buy[PRICE_SOURCE]))
                        daysBetweenBuyAndSellWin.append(dateDelta.days)
                        combinedDays.append(dateDelta.days)
                    # If price change is 0 or negative, we lost something.
                    else:
                        losses += 1
                        lossVals.append(delta / float(buy[PRICE_SOURCE]))
                        daysBetweenBuyAndSellLoss.append(dateDelta.days)
                        combinedDays.append(dateDelta.days)
                    # print "Days between buy and sell: %i" % dateDelta.days
                    state = "WAIT"

                    # Write dates of buy and sell to datelog text file
                    fl.write("\nBought stock:\t %s\t\tPrice:\t%.2f" % (buy["date"][:10], float(buy[PRICE_SOURCE])))
                    buy20 = buy.get("sma20")
                    buy50 = buy.get("sma50")
                    buy200 = buy.get("sma200")
                    if buy20 == None:
                        buy20 = "N/A"
                    if buy50 == None:
                        buy50 = "N/A"
                    if buy200 == None:
                        buy200 = "N/A"
                    fl.write("\nSMA20:\t%s\t\tSMA50:\t%s\t\tSMA200:\t%s" % (buy20, buy50, buy200))
                    fl.write("\nSold stock:\t %s\t\tPrice:\t%.2f" % (stock["date"][:10], float(stock[PRICE_SOURCE])))
                    stock20 = stock.get("sma20")
                    stock50 = stock.get("sma50")
                    stock200 = stock.get("sma200")
                    if stock20 == None:
                        stock20 = "N/A"
                    if stock50 == None:
                        stock50 = "N/A"
                    if stock200 == None:
                        stock200 = "N/A"
                    fl.write("\nSMA20:\t%s\t\tSMA50:\t%s\t\tSMA200:\t%s" % (stock20, stock50, stock200))
                    fl.write("\n")
            else:
                print "strategies: BIG ERROR! Stock was in state %s, which the strategy tester does not recognize!!" % state

            yesterday = stock

        daysBetweenBuyAndSellWin.sort()
        daysBetweenBuyAndSellLoss.sort()
        combinedDays.sort()

        # Write results to results text file
        fw.write("=== %s ===" % ticker)
        # Print win count and gain percentage
        if (wins == 0):
            fw.write("\n# wins:\t\t%i\t\tAvg %% gain/trade:\tN/A" % wins)
        else:
            fw.write("\n# wins:\t\t%i\t\tAvg %% gain/trade:\t%.3f%%" % (wins, (sum(winVals) / float(len(winVals)) * 100)))

        # Print loss count and percentage
        if (losses == 0):
            fw.write("\n# losses:\t%i\t\tAvg %% loss/trade:\tN/A" % losses)
        else:
            fw.write("\n# losses:\t%i\t\tAvg %% loss/trade:\t%.3f%%" % (losses, sum(lossVals) / float(len(lossVals)) * 100))

        # Print aggregate gains and losses
        if wins > 0 and losses > 0:
            aggregate = wins * (sum(winVals) / float(len(winVals)) * 100) + losses * (sum(lossVals) / float(len(lossVals)) * 100)
            fw.write("\nAggregate gain:\n%.3f" % aggregate)
        # Warn user in case no trades occurred
        elif (losses == 0 and wins == 0):
            fw.write("\nAggregate gain:\nN/A (You made no trades. Bad strategy?)")
        # Add statement in case only wins or only losses were made.
        else:
            fw.write("\nAggregate gain:\nN/A")

        # Print distribution of days between buy and sell
        if (wins > 0):
            min = daysBetweenBuyAndSellWin[0]
            med = daysBetweenBuyAndSellWin[(len(daysBetweenBuyAndSellWin) - 1) / 2]
            max = daysBetweenBuyAndSellWin[(len(daysBetweenBuyAndSellWin) - 1)]
            average = sum(daysBetweenBuyAndSellWin) / float(len(daysBetweenBuyAndSellWin))
            # Print wins distribution with quartiles
            if (wins > 20):
                quarter = len(daysBetweenBuyAndSellWin) / 4
                q1 = daysBetweenBuyAndSellWin[quarter]
                q3 = daysBetweenBuyAndSellWin[quarter * 3]
                fw.write("\nDays between buy and sell where WON: \nMin: %i\t\tQ1: %i\t\tMedian: %i\t\tQ3: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, q1, med, q3, max, average))
            # Print wins distribution w/0 quartiles
            else:
                fw.write("\nDays between buy and sell where WON:\nMin: %i\t\tMedian: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, med, max, average))
        else:
            fw.write("\nNo winning trades were made.")
        if losses > 0:
            min = daysBetweenBuyAndSellLoss[0]
            med = daysBetweenBuyAndSellLoss[(len(daysBetweenBuyAndSellLoss) - 1) / 2]
            max = daysBetweenBuyAndSellLoss[(len(daysBetweenBuyAndSellLoss) - 1)]
            average = sum(daysBetweenBuyAndSellLoss) / float(len(daysBetweenBuyAndSellLoss))
            # Print loss distribution with quartiles
            if losses > 20:
                quarter = len(daysBetweenBuyAndSellLoss) / 4
                q1 = daysBetweenBuyAndSellLoss[quarter]
                q3 = daysBetweenBuyAndSellLoss[quarter * 3]
                fw.write("\nDays between buy and sell where LOST: \nMin: %i\t\tQ1: %i\t\tMedian: %i\t\tQ3: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, q1, med, q3, max, average))
            # Print loss distribution w/o quartiles
            else:
                fw.write("\nDays between buy and sell where LOST:\nMin: %i\t\tMedian: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, med, max, average))
        else:
            fw.write("\nNo losing trades were made.")
        if len(combinedDays) > 0 and wins > 0 and losses > 0:
            min = combinedDays[0]
            med = combinedDays[(len(combinedDays) - 1) / 2]
            max = combinedDays[(len(combinedDays) - 1)]
            average = sum(combinedDays) / float(len(combinedDays))
            # Print win and loss distribution with quartiles
            if wins + losses > 20:
                quarter = len(combinedDays) / 4
                q1 = combinedDays[quarter]
                q3 = combinedDays[quarter * 3]
                fw.write("\nDays between buy and sell where WON and LOST: \nMin: %i\t\tQ1: %i\t\tMedian: %i\t\tQ3: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, q1, med, q3, max, average))
            # Print win and combined distribution w/o quartiles
            else:
                fw.write("\nDays between buy and sell where WON and LOST:\nMin: %i\t\tMedian: %i\t\tMax: %i\t\t||\tAverage: %i" % (min, med, max, average))
        fw.write("\n\n\n")
        fl.write("\n\n\n")

        # # For the validateStocks call. Make sure stocks written today have historic trades and 80% win rate
        # if (wins > 0 and losses > 0):
        #     fv.write(ticker + "\n")

    f.close()
    fw.close()
    fl.close()
    # fv.close()
    endTime = datetime.now()
    # if (validateStocks):
    #     global validateStocks
    #     validateStocks = False
    #     print "Stock validation for today took %.3f seconds" % ((endTime - startTime).total_seconds())
    # else:
    print "strategy: Testing took %.3f seconds" % ((endTime - startTime).total_seconds())

def runToday():
    startTime = datetime.now()

    # fvName = "validForToday.txt"
    # fv = open(fvName, 'r')

    # validStocks = fv.read().split('\n')

    f = open('stocks.txt', 'r')
    ftName = "today.txt"
    ft = open(ftName, 'w')
    ft.write("Stock Activities For Today\nTest done on %s\n" % datetime.now().strftime(dateFormat))

    actionMade = False
    reportBuyData = False

    # Twofold command which stores strategies and also gives the time that a stock may on the watch list without being bought before being relegated to the waitlist.
    expireTimeConstant = parseStrategies()

    # Check if strategy parsing had an error. parseStrageties() prints an error, so no need to do so here.
    if expireTimeConstant == None:
        return
    else:
        expireTimeConstant = int(expireTimeConstant)


    for ticker in f:

        ''' Prerequisite check for using tickers from stocks.txt.
        Without this, tickers include the end of line "\n" character in them. This breaks the ticker's formatting when used to form URLs or report to the user.
        '''
        if ("\n" in ticker):
            ticker = ticker[:-1]
        if (ticker[:2] == "//"):
            break

        print "today: Testing %s" %ticker

        # Gets over a year's worth of stock data, which should be enough to historically identify wait, buy, and sell conditions for any test.
        stocks = getByTickerInOrder(ticker)

        buy = {}
        yesterday = None
        totalRecords = stocks.count()
        if (TEST_START_COUNT >= totalRecords):
            print "\t%s is low volume, consider removing. Only has %i/%i records." % (ticker, totalRecords, TEST_START_COUNT)
        bulkCounter = 1
        if (expireTimeConstant == -1):
            ENABLE_EXPIRE_TIME = False
        else:
            ENABLE_EXPIRE_TIME = True
            expireTime = expireTimeConstant
        state = "WAIT"
        for stock in stocks:
            if bulkCounter < totalRecords - TEST_START_COUNT:
                bulkCounter += 1
                continue
            # WAIT means that the stock is on the WAIT LIST
            # If comprWithStock is true, stock goes on WATCH LIST
            # If comprWithStock is false, stock stays in WAIT LIST
            if state == "WAIT":
                if comprWithStock(stock, yesterday, state):
                    state = "WATCH"
                    if ENABLE_EXPIRE_TIME:
                        expireTime = expireTimeConstant

            # WATCH means the stock is on the WATCH LIST
            # If comprWithStock is false, stock stays on WATCH LIST until time expires, after which it is returned to WAIT LIST
            elif state == "WATCH":
                # If comprWithStock is true, stock goes on BUY LIST
                if comprWithStock(stock, yesterday, state):
                    # bulkCounter counts by 1 for every stock seen, so testing this against TOTAL_STOCKS tells if the current stock is the last stock in the collection.
                    # NEW - Also test that stock is a valid stock (has historcal trades with 80% win rate)
                    if bulkCounter == totalRecords:
                        ft.write("\n\nBuy %s" % ticker)
                        actionMade = True
                        reportBuyData = True
                    state = "BUY"
                # If comprWithStock is false but this is the last stock in the collection, it means the stock is sitting on the watchlist.
                elif bulkCounter == totalRecords:
                    ft.write("\n%s is on the watchlist today." % ticker)
                    actionMade = True
                # Getting here means that the watchlisted stock did not pass the strategy. Return stock to WAIT LIST if time has expired, otherwise do nothing.
                if ENABLE_EXPIRE_TIME:
                    if expireTime < 0:
                        state = "WAIT"
                    # Getting here means the watchlisted stock's time has not yet expired. Decrement expire time.
                    else:
                        expireTime -= 1

            # BUY means the stock is on the BUY LIST
            # If comprWithStock is false, stock stays on the BUY LIST.
            elif state == "BUY":
                # If comprWithStock is true, stock is sold and returns to waiting
                if comprWithStock(stock, yesterday, state):
                    if bulkCounter == totalRecords:
                        ft.write("\nSell %s" % ticker)
                        actionMade = True
                    state = "WAIT"
            else:
                print "today: BIG ERROR! Stock was in state %s, which the strategy tester does not recognize!!" % state

            # If the stock needs to be bought today, report SMA data.
            if reportBuyData:
                ft.write("\nSMA20: %s\t\t| SMA50: %s\t\t| SMA200: %s\n" % (stock["sma20"], stock["sma50"], stock["sma200"]))
                reportBuyData = False

            yesterday = stock
            bulkCounter += 1

    # Notify via txt file if no actions ought to be taken today.
    if not actionMade:
       ft.write("\nNo actions to be made today.")

    ft.close()
    # fv.close()
    endTime = datetime.now()
    print "today: Testing took %.3f seconds" % ((endTime - startTime).total_seconds())

# def validateStocks_func():
#     global validateStocks
#     validateStocks = True
#     runStrategies()

if datetime.now().weekday() == SUNDAY or datetime.now().weekday() == SATURDAY:
    sys.exit()

# clearStocks()
updateStocks(db)

logFile = open('logFile.txt', 'a')
logFile.write(datetime.now().strftime(dateFormat) + " updated stocks")
logFile.close()

updateStockVals()

# configFile = open('config.txt', 'w')
# configFile.write(datetime.now().strftime(buyDateFormat))
# configFile.close()

logFile = open('logFile.txt', 'a')
logFile.write(datetime.now().strftime(dateFormat) +  " updated stock vals")
logFile.close()

runStrategies()

# validateStocks_func()

# logFile = open('logFile.txt', 'a')
# logFile.write(datetime.now().strftime(dateFormat)+ " validated stocks")
# logFile.close()

# UNCOMMENT THIS V
runToday()

# logFile = open('logFile.txt', 'a')
# logFile.write(datetime.now().strftime(dateFormat) + " ran today")
# logFile.close()

# # Trigger the Folder Action script to send email.
file_path = path.relpath("/Users/joshuakoh/Desktop/Workspace/StockSolver/IGNORE_ME.txt")

if path.exists(file_path):
    remove(file_path)
time.sleep(5)
with open(file_path, 'w+') as ft:
    ft.write("disregard this file")