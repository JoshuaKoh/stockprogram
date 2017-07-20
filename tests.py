from formulae import *
from strategyParser import *

# Data based on http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
def _smaTester():
    print "=== SMA TESTER ==="
    s = [dict([("close", x)]) for x in range(11, 18)]
    i = [3, 4, 5]
    a = calcSMA(s, i)
    print "Day 5, expected SMA: 13, actual SMA: %.1f" % a[4]["sma5"]
    print "Day 6, expected SMA: 14, actual SMA: %.1f" % a[5]["sma5"]
    print "Day 7, expected SMA: 15, actual SMA: %.1f" % a[6]["sma5"]
    print "\n\n"

# Data based on http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
def _emaTester():
    print "=== EMA TESTER ==="
    s = [ {"close": 22.27}, {"close": 22.19}, {"close": 22.08}, {"close": 22.17}, {"close": 22.18}, {"close": 22.13}, {"close": 22.23}, {"close": 22.43}, {"close": 22.24}, {"close": 22.29}, {"close": 22.15}, {"close": 22.39}, {"close": 22.38} ]
    smas = calcSMA(s, [10])
    emas = calcEMA(s, [10])
    print "Day 10, expected EMA = SMA = 22.22, actual EMA: %.2f, actual SMA: %.2f" % (emas[9]["ema10"], smas[9]["ema10"])
    print "Day 11, expected EMA = 22.21, actual EMA: %.2f" % emas[10]["ema10"]
    print "Day 12, expected EMA = 22.24, actual EMA: %.2f" % emas[11]["ema10"]
    print "Day 13, expected EMA = 22.27, actual EMA: %.2f" % emas[12]["ema10"]

    print "\n\n"

# Data based on http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochastic_oscillator_fast_slow_and_full, abbreviated to 5 days instead of 14.
def _stochasticTester():
    print "=== STOCHASTIC TESTER ==="
    s = [ { "high": 128.43, "low": 124.56, "close": 100 },  # highest high and lowest low in 5 days
    { "high": 127.9, "low": 126.1, "close": 100},
    { "high": 127.9, "low": 126.1, "close": 100 },
    { "high": 127.9, "low": 126.1, "close": 100 },
    { "high": 127.9, "low": 126.1, "close": 127.29 },
    { "high": 128.43, "low": 124.56, "close": 127.18 },
    { "high": 128.43, "low": 124.56, "close": 128.01 },
    { "high": 128.43, "low": 124.56, "close": 127.11 },
    { "high": 128.43, "low": 124.56, "close": 127.73 }]
    a = calcStochastic(s)[0]
    print "Day 6, expected K: 67.61, actual K: %.2f" % a[5]["stochastic5K"]
    print "Day 7, expected K: 89.20, actual K: %.2f" % a[6]["stochastic5K"]
    print "Day 8, expected K: 65.81, actual K: %.2f" % a[7]["stochastic5K"]
    print "Day 9, expected K: 81.75, actual K: %.2f" % a[8]["stochastic5K"]
    print "Day 9 actual D: %f" % a[8]["stochastic3D"]
    print "\n\n"

def _macdAvgTester():
    print "=== MACD AVERAGE TESTER ==="
    s = [dict([("macd", x)]) for x in range(1, 26)]
    a = calcMACDavg(s)[0] # Get just the numerical results, not the string
    print "Day 21, expected MACD average: 10.5, actual average: %.2f" % a[20]["macdAVG20"]
    print "Day 22, expected MACD average: 11.5, actual average: %.2f" % a[21]["macdAVG20"]
    print "Day 23, expected MACD average: 12.5, actual average: %.2f" % a[22]["macdAVG20"]
    print "Day 24, expected MACD average: 13.5, actual average: %.2f" % a[23]["macdAVG20"]
    print "Day 25, expected MACD average: 14.5, actual average: %.2f" % a[24]["macdAVG20"]
    print "\n\n"

def _standardDeviationTester():
    print "=== STANDARD DEVIATION TESTER ==="
    vals = [9, 2, 5, 4, 12, 7, 8, 11, 9, 3, 7, 4, 12, 5, 4, 10, 9, 6, 9, 4]
    s = [dict([("macd", x)]) for x in vals]
    a = calcStandardDeviation(s, 20, "macd")[0] # Get just the numerical results, not the string
    print "Day 20, expected standard deviation: 2.983, actual stdev: %.3f" % a[19]["stdevofmacd20"]
    print "\n\n"

def _strategyParserTester():
    print "=== STRATEGY PARSER TESTER ==="
    stocks1 = []
    macd1 = [5, 5, 5, 5, 5]
    for m in macd1:
        stockDict = { "macd": m }
        stocks1.append(stockDict)
    compr = "macd >2 4"
    day = 1
    passed = []
    yesterday = None
    for stock in stocks1:
        if comprWithStock(stock, compr, yesterday, "WAIT"):
            passed.append(day)
        yesterday = stock
        day += 1
    print "Expected days passed: 2, 3, 4, 5. Actual days passed: %s" % str(passed)

    # RESET STATE
    comprWithStock({"nothing": 0}, "nothing = 0", {"nothing": 0}, "BUY")

    compr = "macd >2 4"
    day = 1
    passed = []
    yesterday = None
    for stock in stocks1:
        if comprWithStock(stock, compr, yesterday, "WAIT"):
            print "WAIT why?", stock, yesterday
            passed.append(day)
        if comprWithStock(stock, compr, yesterday, "WATCH"):
            print "WATCH why?", stock, yesterday
            passed.append(day)
        yesterday = stock
        day += 1
    print "Expected days passed: None. Actual days passed: %s" % str(passed)

    # RESET STATE
    comprWithStock({"nothing": 0}, "nothing = 0", {"nothing": 0}, "BUY")

    stocks2 = []
    macd2 = [1, 2, 3, 4, 5, 1, 5, 1, 5, 6, 7, 3, 2, 1]
    for m in macd2:
        stockDict = { "macd": m }
        stocks2.append(stockDict)
    compr = "macd / +"
    day = 1
    passed = []
    yesterday = None
    for stock in stocks2:
        if comprWithStock(stock, compr, yesterday, "WAIT"):
            passed.append(day)
        yesterday = stock
        day += 1
    print "Expected days passed: 2, 3, 4, 5, 7, 9, 10, 11. Actual days passed: %s" % str(passed)

    # RESET STATE
    comprWithStock({"nothing": 0}, "nothing = 0", {"nothing": 0}, "BUY")

    day = 1
    compr = "macd /2 +"
    passed = []
    yesterday = None
    for stock in stocks2:
        if comprWithStock(stock, compr, yesterday, "WAIT"):
            passed.append(day)
        yesterday = stock
        day += 1
    print "Expected days passed: 3, 4, 5, 10, 11. Actual days passed: %s" % str(passed)

    # RESET STATE
    comprWithStock({"nothing": 0}, "nothing = 0", {"nothing": 0}, "BUY")

    vals = [9, 2, 5, 4, 12, 7, 8, 11, 9, 3, 7, 4, 12, 5, 4, 10, 9, 6, 9, -100]
    stocks3 = [dict([("macd", x)]) for x in vals]
    stocks3 = calcStandardDeviation(stocks3, 20, "macd")[0]
    stocks3 = calcMACDavg(stocks3, 20)[0]
    compr = "stdevofmacd20 < -1.0"
    day = 1
    passed = []
    yesterday = None
    for stock in stocks3:
        if comprWithStock(stock, compr, yesterday, "WAIT"):
            passed.append(day)
        yesterday = stock
        day += 1
    print "Expected days passed: 20. Actual days passed: %s" % str(passed)

    print "\n\n"

_smaTester()
# _emaTester()
# _stochasticTester()
# _macdAvgTester()
#_standardDeviationTester()
# _strategyParserTester()
