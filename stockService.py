import urllib, json
#G4EN9UNQ4IZ15ZSW
import datetime as dt

class StockDay:
    dayOfYear=0
    year=0
    month=0
    day=0
    vopen=0
    vclose=0
    vhigh=0
    vlow=0
    volume=0
    def getStockDayOfYear(self):
       self.dayOfYear = (dt.date(self.year, self.month, self.day) - dt.date(self.year,1,1)).days + 1
    def selfPrint(self):
        print "Year Day:", str(self.dayOfYear)
        print str(self.year), '-',str(self.month), '-', str(self.day)
        print "open", str(self.vopen), "close",str(self.vclose)
        print "high", str(self.vhigh), "low", str(self.vlow)
        print "volume", str(self.volume)
        print "#######################"

class StockService:
    lastSymbol=""
    workingStockJson=[]

    def getYearOfStocks(self,symbol,year):
        if (self.lastSymbol!=symbol):
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+symbol+"&outputsize=full&apikey=G4EN9UNQ4IZ15ZSW"
            response = urllib.urlopen(url)
            self.workingStockJson = json.loads(response.read())
            with open('stocks.json', 'w') as outfile:
                json.dump(self.workingStockJson, outfile)
        retStocks = []
        #print self.workingStockJson
        for i in self.workingStockJson['Time Series (Daily)']:
            if (year in i):
                st = self.workingStockJson['Time Series (Daily)'].get(i)
                stock = StockDay()
                stock.year = int(i[0:4])
                stock.month = int(i[5:7])
                stock.day = int(i[8:10])
                stock.getStockDayOfYear()
                stock.vopen = float(st.get('1. open'))
                stock.vclose = float(st.get('4. close'))
                stock.vhigh = float(st.get('2. high'))
                stock.vlow = float(st.get('3. low'))
                stock.volume = float(st.get('5. volume'))
                retStocks.append(stock)
        retStocks = sorted(retStocks,key= lambda x: x.dayOfYear)
        return retStocks

        #for i in retStocks:
        #    i.selfPrint()
        #print "amountDays",len(retStocks)

                





