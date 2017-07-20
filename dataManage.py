import pymongo
from datetime import datetime
from dbco import *
from pprint import pprint

# Precondition: stocks is a collection of dictionaries containing stock data.
def insertStocks(stocks):
    bulk = db.stocks.initialize_unordered_bulk_op()

    for s in stocks:
        # bulk.insert(s.to_dict())
        bulk.insert(s)

    result = bulk.execute()
    return result

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateSMA(stocks):
    # Get ticker of this batch of stocks
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get("sma12") == None or mostRecent[0].get("sma200") == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { "sma12": s["sma12"], "sma20": s["sma20"], "sma26": s["sma26"], "sma50": s["sma50"], "sma200": s["sma200"] } } )
    #     print "SMA values for %s were just updated" % ticker
    # else:
    #     print "SMA values for %s already updated" % ticker

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateEMA(stocks):
    # Get ticker of this batch of stocks
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get("ema12") == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { "ema12": s["ema12"], "ema20": s["ema20"], "ema26": s["ema26"], "ema50": s["ema50"], "ema200": s["ema200"] } } )
    #     print "EMA values for %s were just updated" % ticker
    # else:
    #     print "EMA values for %s already updated" % ticker

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateROC(stocks, rocStr):
    # Get ticker of this batch of stocks
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get(rocStr) == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { rocStr : s[rocStr] } } )
    #     print "%s values for %s were just updated" % (rocStr, ticker)
    # else:
    #     print "%s values for %s already updated" % (rocStr, ticker)

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateMACD(stocks):
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get("macd") == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { "macd" : s["macd"] } } )
    #     print "MACD values for %s were just updated" % ticker
    # else:
    #     print "MACD values for %s already updated" % ticker

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateStochastic(stocks, stockStrK, stockStrD):
    # Get ticker of this batch of stocks
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get(stockStrK) == None or mostRecent[0].get(stockStrD):
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { stockStrK : s[stockStrK], stockStrD : s[stockStrD] } } )
    #     print "%s and %s values for %s were just updated" % (stockStrK, stockStrD, ticker)
    # else:
    #     print "%s and %s values for %s already updated" % (stockStrK, stockStrD, ticker)

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateMACDavg(stocks, MACDavgStr):
    # Get ticker of this batch of stocks
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get(MACDavgStr) == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { MACDavgStr : s[MACDavgStr] } } )
    #     print "%s values for %s were just updated" % (MACDavgStr, ticker)
    # else:
    #     print "%s values for %s already updated" % (MACDavgStr, ticker)

# Precondition: stocks contains stock data for a single ticker of stocks only.
def updateStdev(stocks, stdevStr):
    ticker = stocks[0]["abbreviation"]

    # Test if most recent stock in database already has SMA data. If so, all SMA values are already updated, so don't bother.
    mostRecent = getSingleMostRecentByTicker(ticker)
    if mostRecent[0].get(stdevStr) == None:
        for s in stocks:
            r = db.stocks.update( { "_id": s["_id"] }, { "$set": { stdevStr : s[stdevStr] } } )
    #     print "%s values for %s were just updated" % (stdevStr, ticker)
    # else:
    #     print "%s values for %s already updated" % (stdevStr, ticker)

def clearStocks():
    db.stocks.remove({})

def getAll():
    return db.stocks.find()

# Ordered first by ticker alphabetically (A first), then by date (earliest date first)
def getAllInOrder():
    return db.stocks.find().sort( [ ("abbreviation", 1), ("date", 1) ] )

# Stocks of only the given ticker, sorted by date (oldest date first)
def getByTickerInOrder(ticker, limit = 0):
    return db.stocks.find ( { "abbreviation": ticker} ).limit(limit).sort( [ ("date", 1) ] )

def getSingleMostRecentByTicker(ticker):
    return db.stocks.find( { "abbreviation": ticker} ).sort( [ ("date", -1) ] ).limit(1)