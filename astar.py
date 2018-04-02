
#dataStockTable[self.state.day].closeValue
import time

import math
from stockService import StockDay

def getStockDayValue(dayData):
    return dayData.vclose

class State:
    day=0
    money=0
    assets=0
    buySellAmount=1
    dayData=0

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
        return ( (self.state.assets * getStockDayValue(self.state.dayData) + self.state.money ) )
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
    stockData= 0
    initialExpectedGain=0

    def __init__(self,startMoneyArg,expectedMoneyGainArg,maxDayArg,transactionCostArg,stockDataArg):
        self.startingMoney=startMoneyArg
        self.expectedMoneyGain=expectedMoneyGainArg
        self.initialExpectedGain = expectedMoneyGainArg
        self.maxDay = maxDayArg
        self.transactionCost = transactionCostArg
        self.stockData = stockDataArg
        

    def goal(self,node):
        if (node.calculateWorth() >= self.startingMoney*self.expectedMoneyGain):
            self.expectedMoneyGain+=0.1
            return True
        else:
            return False

    def printPath(self,node):
        if (node.father!=0):
            node.printData()
            self.printPath(node.father)

    def getDayData(self, day):
        return self.stockData[day]

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
        retNode.state.dayData = self.getDayData(retNode.state.day)
        spendAmount = retNode.state.buySellAmount * retNode.state.money
        amountToBuy = spendAmount / getStockDayValue(retNode.state.dayData)
        retNode.state.money -= amountToBuy * getStockDayValue(retNode.state.dayData) 
        retNode.state.money -= self.transactionCost
        retNode.costSoFar += self.transactionCost
        retNode.state.assets += amountToBuy
        retNode.heuristicFutureCost = (self.startingMoney*self.expectedMoneyGain) - retNode.calculateWorth()
        if (retNode.heuristicFutureCost<0):
            retNode.heuristicFutureCost = 0
        retNode.summedCost = retNode.heuristicFutureCost + retNode.costSoFar
        retNode.generatorMove = 0
        retNode.waitCount = 0
        return retNode
    
    def sellMove(self,node):
        #if (node.state.money < self.transactionCost):
        #    return False
        if (node.state.assets <= 0):
            return False
        retNode = self.cloneNode(node)
        retNode.state.day += 1
        retNode.state.dayData = self.getDayData(retNode.state.day)
        amountTosell = retNode.state.buySellAmount * retNode.state.assets
        retNode.state.money += amountTosell * getStockDayValue(retNode.state.dayData) 
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
        retNode.state.dayData = self.getDayData(retNode.state.day)
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


def insertSorted(nodeList, newNodes):
    for k in newNodes:
        size = len(nodeList)
        if (size==0):
            nodeList += newNodes
            return nodeList
        if (k.summedCost >= nodeList[size-1].summedCost):
            nodeList.append(k)
            continue
        if (k.summedCost <= nodeList[0].summedCost):
            newList = [k]
            nodeList = newList + nodeList
            continue
        pivot = int(size/2)
        rate = int(pivot/2)
        while(nodeList[pivot+1].summedCost < k.summedCost or nodeList[pivot-1].summedCost > k.summedCost):
            right = pivot + rate
            left = pivot - rate
            if (k.summedCost<nodeList[pivot].summedCost):
                pivot = left
            else:
                pivot = right
            rate = int(rate/2)
            if (rate==0):
                break
            #print rate,left,pivot,right, size,nodeList[pivot-1].summedCost,k.summedCost, nodeList[pivot+1].summedCost 
            
        newList = [k]
        nodeList = nodeList[0:pivot] + newList + nodeList[pivot:size]
        #print pivot
        continue
        '''
        for i in range(0,size):
            if (i==size-1):
                nodeList.append(k)
                break
            if (k.summedCost < nodeList[i].summedCost):
                newNodeList = nodeList[0:i]
                newNodeList.append(k)
                nodeList = newNodeList + nodeList[i:size]
                break
        '''
    return nodeList

def search(startNode,problem):
    nodeList = []
    nodeList.append(startNode)
    amountIterations=0
    highestValueSoFar=0
    highestDay = 0
    startingTime = time.time()
    lastEpoch = time.time()
    lastHighest=0
    highestNode=0
    highestCount=0
    
    while (len(nodeList)>0):
        if (problem.goal(nodeList[0])):
            print "########Reached a Goal, Raising Stake########"
            #problem.printPath(nodeList[0])
            #return True
        newNodes = problem.move(nodeList[0])
        nodeList.pop(0)
        nodeList = insertSorted(nodeList,newNodes)
        amountIterations+=1

        for k in newNodes:
            worth = k.calculateWorth()
            if (highestValueSoFar <= worth):
                highestValueSoFar = worth
                highestDay = k.state.day
                highestNode=k

        if (amountIterations==8000):
            amountIterations=0
            if (lastHighest!=highestValueSoFar):
                highestCount=0
                lastHighest=highestValueSoFar
            else:
                highestCount+=1
            if (highestCount==3):
                problem.printPath(highestNode)
                return False
            #print "it", amountIterations
            print "val", highestValueSoFar
            print "day", highestDay
            print "timeFromLast", time.time() -lastEpoch
            lastEpoch = time.time()
        
        #nodeList += newNodes
        
        #nodeList = sorted(nodeList,key= lambda x: x.summedCost)
        
    return False



            





