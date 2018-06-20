from astar import *
from stockService import *


ss = StockService()



stockData = ss.getYearOfStocks("FB","2016")
initialMoney = 10000
newProblem = SellBuyProblem(initialMoney,1.5,len(stockData)-1,17,stockData)
startNode = Node()
startNode.father=0
startNode.state.money = initialMoney
stockData[0].selfPrint()
startNode.state.dayData = stockData[0]
startNode.heuristicFutureCost = initialMoney*1.5 - initialMoney





search(startNode,newProblem)
print "Hello World"


{"5. volume": "25520599", "4. close": "106.2600", "2. high": "107.7300", "1. open": "107.3600", "3. low": "105.9500"}
{"5. volume": 24904, "4. close": 30.26, "2. high": 31.53, "1. open": 31.11, "3. low": 30.25}