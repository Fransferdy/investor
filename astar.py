
#dataStockTable[self.state.day].closeValue


import math

url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=G4EN9UNQ4IZ15ZSW"
response = urllib.urlopen(url)
data = json.loads(response.read())
print data['Meta Data']
exit

def getStockDayValue(day):
    if (day % 2 ==0):
        return 6 
    else:
        return 5

class State:
    day=0
    money=0
    assets=0
    buySellAmount=1

class Node:
    generatorMove=0
    state=State()
    father=0
    costSoFar=0
    heuristicFutureCost=0
    summedCost=0
    generatorMoveNames=[]
    waitCount = 0
    def __init__(self):
        state=State()
        self.generatorMoveNames.append("Buy")
        self.generatorMoveNames.append("Sell")
        self.generatorMoveNames.append("Wait")
        self.generatorMoveNames.append("Set 20%")
        self.generatorMoveNames.append("Set 30%")
        self.generatorMoveNames.append("Set 40%")
        self.generatorMoveNames.append("Set 50%")
        self.generatorMoveNames.append("Set 60%")
        self.generatorMoveNames.append("Set 70%")
        self.generatorMoveNames.append("Set 80%")
        self.generatorMoveNames.append("Set 90%")        
        self.generatorMoveNames.append("Set 100%")
    def calculateWorth(self):
        return ( (self.state.assets * getStockDayValue(self.state.day)) + self.state.money )
    def printData(self):
        print "Generator:" + str(self.generatorMoveNames[self.generatorMove])
        print "Cost:" + str(self.summedCost)
        print "Day: " + str(self.state.day)
        print "Final Money: " + str(self.state.money)
        print "Assets: " + str(self.state.assets)
        print "Worth: " + str(self.calculateWorth())
        print "######################"


class Problem:
    def goal(self,node):
        return True

    def move(self,node):
        return list()

    def printPath(self):
        print "empty"
        return True


class SellBuyProblem(Problem):
    startingMoney=0
    expectedMoneyGain=0
    maxDay = 0
    transactionCost = 0

    def __init__(self,startMoneyArg,expectedMoneyGainArg,maxDayArg,transactionCostArg):
        self.startingMoney=startMoneyArg
        self.expectedMoneyGain=expectedMoneyGainArg
        self.maxDay = maxDayArg
        self.transactionCost = transactionCostArg

    def goal(self,node):
        if (node.calculateWorth() >= self.startingMoney*self.expectedMoneyGain):
            return True
        else:
            return False

    def printPath(self,node):
        if (node.father!=0):
            node.printData()
            self.printPath(node.father)

    def cloneNode(self,node):
        newNode = Node()
        newNode.state = State()
        newNode.father = node
        newNode.waitCount = node.waitCount
        newNode.costSoFar = node.costSoFar
        newNode.state.day = node.state.day
        newNode.state.buySellAmount = node.state.buySellAmount
        newNode.state.money =node.state.money
        newNode.state.assets =node.state.assets
        #node.printData()
        return newNode
        
    def buyMove(self,node):
        if (node.state.money < self.transactionCost):
            return False
        retNode = self.cloneNode(node)
        retNode.state.day += 1
        spendAmount = retNode.state.buySellAmount * retNode.state.money
        amountToBuy = math.floor( spendAmount / getStockDayValue(retNode.state.day) )
        retNode.state.money -= amountToBuy * getStockDayValue(retNode.state.day) 
        retNode.state.money -= self.transactionCost
        retNode.costSoFar += self.transactionCost
        retNode.state.assets += amountToBuy
        retNode.heuristicFutureCost = (self.startingMoney*self.expectedMoneyGain) - retNode.calculateWorth()
        if (retNode.heuristicFutureCost<0):
            retNode.heuristicFutureCost = 0
        retNode.summedCost = retNode.heuristicFutureCost + retNode.costSoFar
        retNode.generatorMove = 0
        retNode.waitCount = 0
        #retNode.printData()
        #wait = input("PRESS ENTER TO CONTINUE.")
        #node.printData()
        #print "END POTATO"
        return retNode
    
    def sellMove(self,node):
        #if (node.state.money < self.transactionCost):
        #    return False
        if (node.state.assets <= 0):
            return False
        retNode = self.cloneNode(node)
        retNode.state.day += 1
        amountTosell = retNode.state.buySellAmount * retNode.state.assets
        retNode.state.money += amountTosell * getStockDayValue(retNode.state.day) 
        retNode.state.money -= self.transactionCost
        retNode.costSoFar += self.transactionCost
        retNode.state.assets -= amountTosell
        retNode.heuristicFutureCost = (self.startingMoney*self.expectedMoneyGain) - retNode.calculateWorth()
        if (retNode.heuristicFutureCost<0):
            retNode.heuristicFutureCost = 0
        retNode.summedCost = retNode.heuristicFutureCost + retNode.costSoFar
        retNode.generatorMove = 1
        retNode.waitCount = 0
        return retNode

    def waitMove(self,node):
        retNode = self.cloneNode(node)
        retNode.state.day += 1
        retNode.state.money = node.state.money 
        retNode.costSoFar = node.costSoFar
        retNode.state.assets = node.state.assets
        retNode.heuristicFutureCost = node.heuristicFutureCost
        retNode.summedCost = node.summedCost
        retNode.generatorMove = 2
        retNode.waitCount += 1
        if (retNode.waitCount>30):
            retNode.waitCount=0
            retNode.state.money -= self.transactionCost
            retNode.costSoFar+= self.transactionCost
            retNode.summedCost = retNode.costSoFar + retNode.heuristicFutureCost
        return retNode
    
    def move(self,node):
        if (node.state.day>=self.maxDay):
            return list()
        retList = []
        rnode = self.buyMove(node)
        if (rnode!=False):
            retList.append(rnode)
        rnode = self.sellMove(node)
        if (rnode!=False):
            retList.append(rnode)
        rnode = self.waitMove(node)
        if (rnode!=False):
            retList.append(rnode)
        return sorted(retList,key= lambda x: x.summedCost)


def search(startNode,problem):
    nodeList = []
    nodeList.append(startNode)
    while (len(nodeList)>0):
        if (problem.goal(nodeList[0])):
            problem.printPath(nodeList[0])
            return True
        newNodes = problem.move(nodeList[0])

        #if (nodeList[0].state.day==361):
         
         #   problem.printPath(nodeList[0])
          #  return False
        
        nodeList += newNodes
        nodeList.pop(0)
        nodeList = sorted(nodeList,key= lambda x: x.summedCost)
        
    return False

initialMoney = 1000
newProblem = SellBuyProblem(initialMoney,15,365,17)
startNode = Node()
startNode.father=0
startNode.state.money = initialMoney
startNode.heuristicFutureCost = initialMoney*2 - initialMoney





search(startNode,newProblem)
print "Hello World"



