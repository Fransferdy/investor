#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include "json.hpp"

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
        std::cout << year << "/" << month << "/" << day << std::endl;
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
        day =0;
        money = 0;
        assets = 0;
        buySellAmount =0;
    }
    float getWorth()
    {
        if (worth < 0)
            calculateWorth();
        return worth;
    }
    std::string formattedDay()
    {
        std::string month0 = "";
        std::string day0 = "";
        if (dayData->month<10)
            month0 = "0";
        if (dayData->day<10)
            day0 = "0";    
        return ""+std::to_string(dayData->year)+"-"+month0+std::to_string(dayData->month)+"-"+day0+std::to_string(dayData->day);
    }
    private:
        void calculateWorth()
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
        std::cout << state.dayData->year << "/" << state.dayData->month << "/" << state.dayData->day << std::endl;
        std::cout << "Generator: " << Node::generatorMoveNames[generatorMove] << std::endl;
        std::cout << "Cost: " << summedCost << std::endl;
        std::cout << "Day: " << state.day << std::endl;
        std::cout << "Final Money: " << state.money << std::endl;
        std::cout << "Assets: " << state.assets << std::endl;
        std::cout << "Worth: " << state.getWorth() << std::endl;
        std::cout << "#############" << std::endl;
    }

    Node *cloneSelf(); 
};
std::string Node::generatorMoveNames[MOVES_AMOUNT];


Node *Node::cloneSelf()
{
    Node * ret = new Node();
    ret->father = this;
    ret->waitCount = this->waitCount;
    ret->costSoFar = this->costSoFar;
    ret->state.buySellAmount = this->state.buySellAmount;
    ret->state.money = this->state.money;
    ret->state.assets = this->state.assets;
    ret->state.day = this->state.day;

    return ret;
}



struct compareNode {
    bool operator() (const Node* lhs, const Node* rhs) const {
        return lhs->summedCost < rhs->summedCost;
    }
};

class Problem
{
public:

    virtual bool goal(Node *node){return false;};
    virtual void printPath(Node *node){};
    virtual StockDay * getDayData(int day){return NULL;};
    virtual Node* buyMove(Node *node){return NULL;};
    virtual Node* sellMove(Node *node){return NULL;};
    virtual Node * waitMove(Node *node){return NULL;};
    virtual bool stopCondition(std::vector<Node*> newNodes){return false;};
    virtual std::vector<Node*> move(Node *actual){std::vector<Node*> a; return a;};
};

#define MAX_UNFRUITFUL_ITERATIONS 3000000
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
        std::map<std::string, int> *dayResults;

    SellBuyProblem(float startMoneyarg, float expectedGainarg, int maxDayarg, float transactionCostarg,std::vector<StockDay> *stockDataarg, std::map<std::string, int> *dayResultsarg)
    {
        reset(startMoneyarg,expectedGainarg,maxDayarg,transactionCostarg,stockDataarg,dayResultsarg);
    }

    void reset(float startMoneyarg, float expectedGainarg, int maxDayarg, float transactionCostarg,std::vector<StockDay> *stockDataarg, std::map<std::string, int> *dayResultsarg)
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
        highestNode=NULL;
        highestCount=0;
        dayResults = dayResultsarg;
    }

    bool goal(Node *node)
    {
        if (node->state.getWorth() >= startingMoney*expectedMoneyGain )
        {
            float worth = node->state.getWorth();
            if (highestValueSoFar <= worth && node->state.day == maxDay-1)
            {
                node->printData(); 
                expectedMoneyGain+=0.1;

                highestValueSoFar = worth;
                highestDay = node->state.day;
                highestNode=node;
                return true;
            }
            //addDays(node);

            return false;
        }
        else
            return false;
    }

    void addDays(Node *node)
    {
        if (node->father!=NULL)
        {
            auto ret = dayResults->insert(std::pair<std::string,int>(node->state.formattedDay(),node->generatorMove));
            if (ret.second==false)
            {
                if (ret.first->second==M_WAIT && ret.first->second!=node->generatorMove)
                {
                    ret.first->second = node->generatorMove;
                    std::cout << ret.first->first << " => " << ret.first->second << std::endl;
                }
            }
            addDays(node->father);
        }
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
            return newNodes;
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
        amountIterations++;
        for (std::vector<Node*>::iterator it = newNodes.begin() ; it != newNodes.end(); ++it)
        {
            worth = (*it)->state.getWorth();
            if (highestValueSoFar <= worth && (*it)->state.day == maxDay-1)
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
                //addDays(highestNode);
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
                return true;
            }
            std::cout << "val " << highestValueSoFar << std::endl;
            std::cout << "day " << highestValueSoFar << std::endl;

            return false;
        }
        return false;
    }

};


std::pair<float,float> search(Node *startNode, Problem * problem)
{
    std::set<Node*,compareNode> nodeList;
    std::vector<Node*> pastNodes;
    std::vector<Node*> newNodes;
    Node * actualNode;
    Node * deleteNode;
    nodeList.insert(startNode);
    
    
    while(!nodeList.empty())
    {
        actualNode = *nodeList.begin();
        
        if ( problem->goal( actualNode ) )
            std::cout << "########Reached a Goal, Raising Stake########" <<std::endl;
        

        newNodes = problem->move(actualNode);
        nodeList.erase(actualNode);

        for (std::vector<Node*>::iterator it = newNodes.begin() ; it != newNodes.end(); ++it)
        {
            nodeList.insert(*it);
            pastNodes.push_back(*it);
        }
        if (problem->stopCondition(newNodes))
            break;  
    }

    ((SellBuyProblem*)problem)->printPath(((SellBuyProblem*)problem)->highestNode);
    ((SellBuyProblem*)problem)->addDays(((SellBuyProblem*)problem)->highestNode);

    if (((SellBuyProblem*)problem)->highestNode==NULL)
        std::cout << "No Highest" << std::endl;

    auto ret1 = ((SellBuyProblem*)problem)->highestNode->state.assets;
    auto ret2 = ((SellBuyProblem*)problem)->highestNode->state.money;
    
    for (auto it = pastNodes.begin() ; it != pastNodes.end(); ++it)
    {
        deleteNode = *it;
        //std::cout << "deleted " << deleteNode->state.day << std::endl;
        delete deleteNode;  
    }
    return std::pair<float,float>(ret1,ret2); 
}

    void dumpObjectConst( const json::JSON &object ) {
    for( auto &j : object.ObjectRange() )
        std::cout << "potato" << "Object[ " << j.first << " ] = " << j.second << "\n";
}

std::vector<StockDay> loadStocksFromJson(std::string fileName,std::string yeararg)
{
    std::vector<StockDay> stocks;
    json::JSON obj;
    std::ifstream t(fileName);
    std::string stocksJson((std::istreambuf_iterator<char>(t)),
                    std::istreambuf_iterator<char>());
    obj = json::JSON::Load(stocksJson);
    std::cout << obj["Meta Data"] << std::endl;
    std::string year,month,day;
    StockDay stockDay;
    tm timeinfo = {};

    for( auto &j : obj["Time Series (Daily)"].ObjectRange() )
    {
        //std::cout << "Object[ " << j.first << " ] = " << j.second << "\n";
        year = j.first.substr(0,4);
        if (j.first.find(yeararg)==std::string::npos)
            continue;

        month = j.first.substr(5,2);
        day = j.first.substr(8,2);
        //std::cout << year << '-' << month << '-' << day << std::endl;
        stockDay.year = std::stoi(year);
        stockDay.month = std::stoi(month);
        stockDay.day = std::stoi(day);

        timeinfo.tm_year = stockDay.year - 1900;
        timeinfo.tm_mon = stockDay.month - 1;
        timeinfo.tm_mday = stockDay.day;
        mktime(&timeinfo);
        stockDay.dayOfYear = timeinfo.tm_yday;
        //std::cout << j.second["1. open"] << std::endl;
        stockDay.vopen = std::atof(j.second["1. open"].ToString().c_str());
        stockDay.vclose = std::atof(j.second["4. close"].ToString().c_str());
        stockDay.vhigh = std::atof(j.second["2. high"].ToString().c_str());
        stockDay.vlow = std::atof(j.second["3. low"].ToString().c_str());
        stockDay.volume = std::atof(j.second["5. volume"].ToString().c_str());
        //stockDay.selfPrint();
        stocks.push_back(stockDay);
    }
    //std::cout << stocks.size() <<std::endl;
    return stocks;
}

void searchYear(std::vector<StockDay> stocks, float initialMoney,float expectedGain,std::map<std::string,int> &dayResults)
{
    size_t halfsize = stocks.size()/2;
    
    std::vector<StockDay> stocksFirst(stocks.begin(), stocks.begin() + halfsize);
    std::vector<StockDay> stocksLast(stocks.begin() + halfsize, stocks.end() );

/*
    std::cout << stocks.size() << std::endl;
    std::cout << stocksFirst.size() << std::endl;
    std::cout << stocksLast.size() << std::endl;

    Node *start = new Node();
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stocksFirst[0];
    SellBuyProblem problem(initialMoney,expectedGain,stocksFirst.size(),17,&stocksFirst,&dayResults);
    auto output = search(start,&problem);

    initialMoney = output.second;  
    start = new Node();
    start->state.assets = output.first;
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stocksLast[0];
    problem.reset(initialMoney,expectedGain,stocksLast.size(),17,&stocksLast,&dayResults);
    search(start,&problem);

  */  
    
    halfsize = stocksFirst.size()/2;
    std::vector<StockDay> stockspt1(stocksFirst.begin(), stocksFirst.begin() + halfsize);
    std::vector<StockDay> stockspt2(stocksFirst.begin() + halfsize, stocksFirst.end() );

    halfsize = stocksLast.size()/2;
    std::vector<StockDay> stockspt3(stocksLast.begin(), stocksLast.begin() + halfsize);
    std::vector<StockDay> stockspt4(stocksLast.begin() + halfsize, stocksLast.end() );

    Node *start = new Node();
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stocks[0];
    SellBuyProblem problem(initialMoney,expectedGain,stockspt1.size(),17,&stockspt1,&dayResults);
    auto output = search(start,&problem);

    initialMoney = output.second;  
    start = new Node();
    start->state.assets = output.first;
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stockspt2[0];
    problem.reset(initialMoney,expectedGain,stockspt2.size(),17,&stockspt2,&dayResults);
    output = search(start,&problem);

    initialMoney = output.second;  
    start = new Node();
    start->state.assets = output.first;
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stockspt3[0];
    problem.reset(initialMoney,expectedGain,stockspt3.size(),17,&stockspt3,&dayResults);
    output = search(start,&problem);

    initialMoney = output.second;  
    start = new Node();
    start->state.assets = output.first;
    start->state.buySellAmount = 1;
    start->state.day=0;
    start->father = NULL;
    start->state.money =initialMoney;
    start->heuristicFutureCost = initialMoney*expectedGain - initialMoney;
    start->state.dayData = &stockspt4[0];
    problem.reset(initialMoney,expectedGain,stockspt4.size(),17,&stockspt4,&dayResults);
    search(start,&problem);
    

}


int main()
{
    Node::setupMoveNames();
    std::vector<StockDay> stocks;
    float initialMoney = 10000;
    float expectedGain = 1.1;
    std::map<std::string,int> dayResults;
    json::JSON out;

    
    /*
    for (auto it = stocks.begin() ; it != stocks.end(); ++it)
        (*it).selfPrint();
    */

    //stocks = loadStocksFromJson("stocksbr.json","2009");
    //searchYear(stocks,10000,1.1,dayResults);
    

    stocks = loadStocksFromJson("stocksbr.json","2010");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2011");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2012");
    searchYear(stocks,5000,1.1,dayResults);
    
    stocks = loadStocksFromJson("stocksbr.json","2013");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2014");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2015");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2016");
    searchYear(stocks,5000,1.1,dayResults);

    stocks = loadStocksFromJson("stocksbr.json","2017");
    searchYear(stocks,5000,1.1,dayResults);

    

    out["buy"] = json::Array();
    out["sell"] = json::Array();
    out["wait"] = json::Array();
    std::map<std::string,int>::iterator it = dayResults.begin();
    for (it=dayResults.begin(); it!=dayResults.end(); ++it)
    {
        if (it->second==M_BUY)
            out["buy"][out["buy"].size()] = it->first;
        if (it->second==M_SELL)
            out["sell"][out["sell"].size()] = it->first;
        if (it->second==M_WAIT)
            out["wait"][out["wait"].size()] = it->first;
        std::cout << it->first << " => " << it->second << std::endl;
    }

    std::cout << "Buy Size " << out["buy"].size() <<std::endl;
    std::cout << "Sell Size " << out["sell"].size() <<std::endl;
    std::cout << "Wait Size " << out["wait"].size() <<std::endl;
    std::ofstream myfile;
    myfile.open ("labeledDays.json");
    myfile << out;
    myfile.close();

        //std::cout << it->first << " => " << it->second << std::endl;
    
    //std::cout << problem.out << std::endl;

    
}