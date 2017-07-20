import boto
s3 = boto.connect_s3()
bucket = s3.create_bucket('stocksolver')  # bucket names must be unique

key = bucket.new_key('main.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/main.py')
key.set_acl('public-read')

key = bucket.new_key('dataFetch.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/dataFetch.py')
key.set_acl('public-read')

key = bucket.new_key('dataManage.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/dataManage.py')
key.set_acl('public-read')

key = bucket.new_key('dbco.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/dbco.py')
key.set_acl('public-read')

key = bucket.new_key('formulae.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/formulae.py')
key.set_acl('public-read')

key = bucket.new_key('myLib.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/myLib.py')
key.set_acl('public-read')

key = bucket.new_key('stocks.txt')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/stocks.txt')
key.set_acl('public-read')

key = bucket.new_key('strategies.txt')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/strategies.txt')
key.set_acl('public-read')

key = bucket.new_key('strategyParser.py')
key.set_contents_from_filename('/Users/joshuakoh/Desktop/Workspace/StockSolver/strategyParser.py')
key.set_acl('public-read')

