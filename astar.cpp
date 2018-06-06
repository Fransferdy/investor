#include <iostream>
#include <ofstream>
#include <string>
#include <vector>
#include <set>

#define MOVES_AMOUNT 12
enum MOVES{
    M_BUY,
    M_SELL,
    M_WAIT,
    M_SET20,
    M_SET30,
    M_SET40,
    M_SET50,
    M_SET60,
    M_SET70,
    M_SET80,
    M_SET90,
    M_SET100
};




class StockDay
{
    public:
        int dayOfYear;
        int year;
        int month;
        int day;
        float vopen;
        float vclose;
        float vhigh;
        float vlow;
        float volume;
    void selfPrint()
    {
        //std::cout << "#############" << std::endl;
        std::cout << year << "/" << month << "/" << "day" << std::endl;
        std::cout << "Open: " << vopen << std::endl;
        std::cout << "Close: " << vclose << std::endl;
        std::cout << "High: " << vhigh << std::endl;
        std::cout << "Low: " << vlow << std::endl;
        std::cout << "Volume: " << volume << std::endl;
        std::cout << "#############" << std::endl;
    }
};

class State
{
    public:
        int day;
        float money;
        float assets;
        float buySellAmount;
        StockDay *dayData;
        float worth;
    State()
    {
        worth = -1;
    }
    float getWorth()
    {
        if (worth < 0)
            calculateWorth();
        return worth;
    }
    private:
        float calculateWorth()
        {
            worth = (assets*dayData->vclose) + money;
        }
};




class Node
{
    public:
        int generatorMove;
        State state;
        Node *father;
        float costSoFar;
        float heuristicFutureCost;
        float summedCost;
        int waitCount;
        static std::string generatorMoveNames[MOVES_AMOUNT];

    static void setupMoveNames()
    {
        generatorMoveNames[M_BUY] = "Buy";
        generatorMoveNames[M_SELL] = "Sell";
        generatorMoveNames[M_WAIT] = "Wait";
        generatorMoveNames[M_SET20] = "Set 20%";
        generatorMoveNames[M_SET30] = "Set 30%";
        generatorMoveNames[M_SET40] = "Set 40%";
        generatorMoveNames[M_SET50] = "Set 50%";
        generatorMoveNames[M_SET60] = "Set 60%";
        generatorMoveNames[M_SET70] = "Set 70%";
        generatorMoveNames[M_SET80] = "Set 80%";
        generatorMoveNames[M_SET90] = "Set 90%";
        generatorMoveNames[M_SET100] = "Set 100%";
    }
    Node()
    {
        
        father = NULL;
    }
    
    
    void printData()
    {
        std::cout << "Generator: " << generatorMoveNames[generatorMove] << std::endl;
        std::cout << "Cost: " << summedCost << std::endl;
        std::cout << "Day: " << state.day << std::endl;
        std::cout << "Final Money: " << state.money << std::endl;
        std::cout << "Assets: " << state.assets << std::endl;
        std::cout << "Worth: " << state.getWorth() << std::endl;
        std::cout << "#############" << std::endl;
    }

    Node *cloneSelf();

    
};

Node *Node::cloneSelf()
{
    Node * ret = new Node();
    ret->father = this;
    ret->waitCount = this->waitCount;
    ret->costSoFar = this->costSoFar;
    ret->state.buySellAmount = this->state.buySellAmount;
    ret->state.money = this->state.money;
    ret->state.assets = this->state.assets;

    return ret;
}

struct compareNode 
{
    bool operator()(const Node& x, const Node& y) const 
    {
        return x.summedCost < y.summedCost;
    }
};

class Problem
{
public:

    virtual bool goal(Node *node){};
    virtual void printPath(Node *node){};
    virtual StockDay * getDayData(int day){};
    virtual Node* buyMove(Node *node){};
    virtual Node* sellMove(Node *node){};
    virtual Node * waitMove(Node *node){};
    virtual bool stopCondition(std::vector<Node*> newNodes);
    virtual std::vector<Node*> move(Node *actual){};
};

#define MAX_UNFRUITFUL_ITERATIONS 8000
#define MAX_CONSECUTIVE_UNFRUITFUL_TRIES 3
class SellBuyProblem : public Problem
{
    public:
        float startingMoney;
        float expectedMoneyGain;
        int maxDay;
        float transactionCost;
        std::vector<StockDay> *stockData;

        int amountIterations;
        float highestValueSoFar;
        int highestDay;
        float lastHighest;
        Node* highestNode;
        int highestCount;

    SellBuyProblem(float startMoneyarg, float expectedGainarg, int maxDayarg, float transactionCostarg,std::vector<StockDay> *stockDataarg)
    {
        startingMoney = startMoneyarg;
        expectedMoneyGain = expectedGainarg;
        maxDay = maxDayarg;
        transactionCost = transactionCostarg;
        stockData = stockDataarg;

        amountIterations = 0;
        highestValueSoFar=0;
        highestDay=0;
        lastHighest=0;
        highestNode;
        highestCount=0;
    }

    bool goal(Node *node)
    {
        if (node->state.getWorth() >= startingMoney*expectedMoneyGain )
        {
            expectedMoneyGain+=0.1;

            float worth = node->state.getWorth();
            if (highestValueSoFar <= worth)
            {
                highestValueSoFar = worth;
                highestDay = node->state.day;
                highestNode=node;
            }

            return true;
        }
        else
            return false;
    }

    void printPath(Node *node)
    {
        if (node->father!=NULL)
        {
            node->printData();
            printPath(node->father);
        }
    }

    StockDay * getDayData(int day)
    {
        return &(*stockData)[day];
    }

    Node* buyMove(Node *node)
    {
        if (node->state.money < transactionCost)
            return NULL;
        Node * retNode = node->cloneSelf();
        retNode->state.day++;
        retNode->state.dayData = getDayData(retNode->state.day);
        float spendAmount = retNode->state.buySellAmount * retNode->state.money;
        float stockValue = retNode->state.dayData->vclose;
        float amountToBuy = spendAmount / stockValue;
        retNode->state.money -= amountToBuy * stockValue;
        retNode->state.money -= transactionCost;
        retNode->state.assets += amountToBuy;
        retNode->costSoFar += transactionCost;
        retNode->heuristicFutureCost= (startingMoney*expectedMoneyGain)-retNode->state.getWorth();
        if (retNode->heuristicFutureCost<0)
            retNode->heuristicFutureCost=0;
        retNode->summedCost = retNode->heuristicFutureCost + retNode->costSoFar;
        retNode->generatorMove = M_BUY;
        retNode->waitCount = 0;
        return retNode;
    }

    Node* sellMove(Node *node)
    {
        if (node->state.assets <=0)
            return NULL;
        Node * retNode = node->cloneSelf();
        retNode->state.day++;
        retNode->state.dayData = getDayData(retNode->state.day);
        float amountToSell = retNode->state.buySellAmount * retNode->state.assets;
        float stockValue = retNode->state.dayData->vclose;
        retNode->state.money += amountToSell * stockValue;
        retNode->state.money -= transactionCost;
        retNode->costSoFar += transactionCost;
        retNode->state.assets -= amountToSell; 
        retNode->heuristicFutureCost= (startingMoney*expectedMoneyGain)-retNode->state.getWorth();
        if (retNode->heuristicFutureCost<0)
            retNode->heuristicFutureCost=0;
        retNode->summedCost = retNode->heuristicFutureCost + retNode->costSoFar;
        retNode->generatorMove = M_SELL;
        retNode->waitCount = 0;
        return retNode;
    }

    Node * waitMove(Node *node)
    {
        Node * retNode = node->cloneSelf();
        retNode->state.day++;
        retNode->state.dayData = getDayData(retNode->state.day);
        retNode->state.money = node->state.money;
        retNode->costSoFar =node->costSoFar;
        retNode->state.assets = node->state.assets;
        retNode->heuristicFutureCost = node->heuristicFutureCost;
        retNode->summedCost = node->summedCost;
        retNode->generatorMove = M_WAIT;
        retNode->waitCount+=1;
        if (retNode->waitCount>30)
        {
            retNode->waitCount=0;
            retNode->state.money -=transactionCost;
            retNode->costSoFar = transactionCost;
            retNode->summedCost = retNode->costSoFar + retNode->heuristicFutureCost; 
        }
        return retNode;
    }
    std::vector<Node*> move(Node* actual)
    {
        std::vector <Node*> newNodes;
        if (actual->state.day>=maxDay)
            return;
        Node* newNode;
        newNode = buyMove(actual);
        if (newNode!=NULL)
            newNodes.push_back(newNode);
        newNode = sellMove(actual);
        if (newNode!=NULL)
            newNodes.push_back(newNode);
        newNode = waitMove(actual);
        if (newNode!=NULL)
            newNodes.push_back(newNode);
        return newNodes;
    }

    bool stopCondition(std::vector<Node*> newNodes)
    {
        float worth;
        for (std::vector<Node*>::iterator it = newNodes.begin() ; it != newNodes.end(); ++it)
        {
            worth = (*it)->state.getWorth();
            if (highestValueSoFar <= worth)
            {
                highestValueSoFar = worth;
                highestDay = (*it)->state.day;
                highestNode=(*it);
            }
        }
        if (amountIterations==MAX_UNFRUITFUL_ITERATIONS)
        {
            amountIterations=0;
            if (lastHighest!=highestValueSoFar)
            {
                highestCount=0;
                lastHighest=highestValueSoFar;
            }
            else
                highestCount+=1;
            if (highestCount==MAX_CONSECUTIVE_UNFRUITFUL_TRIES)
            {
                std::streambuf *coutbuf = std::cout.rdbuf();
                std::ofstream out("out.txt");
                std::cout.rdbuf(out.rdbuf());
                printPath(highestNode);
                out.close();
                std::cout.rdbuf(coutbuf);
                printPath(highestNode);
                return true;
            }
            std::cout << "val " << highestValueSoFar << std::endl;
            std::cout << "day " << highestValueSoFar << std::endl;

            return false;
        }
    }

};


void search(Node *startNode, Problem * problem)
{
    std::set<Node*,compareNode> nodeList;
    std::set<Node*,compareNode> pastNodes;
    std::vector<Node*> newNodes;
    Node * actualNode;
    nodeList.insert(startNode);
    
    while(!nodeList.empty())
    {
        actualNode = *nodeList.begin();
        if ( problem->goal( actualNode ) )
            std::cout << "########Reached a Goal, Raising Stake########" <<std::endl;
        
        newNodes = problem->move(actualNode);
        pastNodes.insert(actualNode);
        nodeList.erase(actualNode);

        for (std::vector<Node*>::iterator it = newNodes.begin() ; it != newNodes.end(); ++it)
            nodeList.insert(*it);

        if (problem->stopCondition(newNodes))
            break;   
    }

}