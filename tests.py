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