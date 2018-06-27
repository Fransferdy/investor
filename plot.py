import numpy
import datetime
import json
import matplotlib.pyplot as plt
import sys

M_BUY = 0
M_SELL = 1
M_WAIT = 2

# fix random seed for reproducibility
numpy.random.seed(7)

def getSinceEpochDay(dateString):
    year = int(dateString[0:4])
    month = int(dateString[5:7])
    day = int(dateString[8:10])
    sinceEpochDay = ((datetime.datetime(year,month,day) - datetime.datetime(1970,1,1)).days)
    return sinceEpochDay

def relativeDay(minusPos,myDay,daysList):
    ret = []
    ret.append(daysList[myDay-minusPos]["1. open"]/daysList[myDay]["4. close"])
    ret.append(daysList[myDay-minusPos]["2. high"]/daysList[myDay]["4. close"])
    ret.append(daysList[myDay-minusPos]["3. low"]/daysList[myDay]["4. close"])
    ret.append(daysList[myDay-minusPos]["4. close"]/daysList[myDay]["4. close"])
    ret.append(daysList[myDay-minusPos]["5. volume"]/daysList[myDay]["5. volume"])
    return ret

def dayToFeature(dateString,daysList):
    daySinceEpoch = getSinceEpochDay(dateString)
    daysSize = len(daysList)
    myDay = 0
    retFeatures = []
    retLabel = 0
    for i in range(0,daysSize):
        if (daysList[i]["sinceEpochDay"]==daySinceEpoch):
            myDay = i
            break
    for i in range(1,80):
        retFeatures.extend(relativeDay(i,myDay,daysList))


    return retFeatures

def addSamples(option, labeledSet,stockDays,samples,labels,offset,amount):
    labeled = labeledSet
    labeledSize = len(labeled) * amount
    start = int(labeledSize * offset)
    finish = int(start+labeledSize)
    if (finish>=len(labeled)):
        finish = len(labeled)

    for i in range(start,finish):
        samples.append(dayToFeature(labeled[i],stockDays))
        labels.append(option)

def stockDataToList(data):
    days = []

    for stockDay in data:
        data[stockDay]["sinceEpochDay"] = getSinceEpochDay(stockDay)
        data[stockDay]["date"] = stockDay
        data[stockDay]["1. open"] = float(data[stockDay]["1. open"])
        data[stockDay]["2. high"] = float(data[stockDay]["2. high"])
        data[stockDay]["3. low"] = float(data[stockDay]["3. low"])
        data[stockDay]["4. close"] = float(data[stockDay]["4. close"] )
        data[stockDay]["5. volume"] = float(data[stockDay]["5. volume"])
        days.append(data[stockDay])

    days = sorted(days, key=lambda x: x["sinceEpochDay"], reverse=False)
    return days

def yearOfstockDataToList(data,year):
    days = []

    for stockDay in data:
        if (year in data[stockDay]["date"]):
            data[stockDay]["sinceEpochDay"] = getSinceEpochDay(stockDay)
            data[stockDay]["date"] = stockDay
            data[stockDay]["1. open"] = float(data[stockDay]["1. open"])
            data[stockDay]["2. high"] = float(data[stockDay]["2. high"])
            data[stockDay]["3. low"] = float(data[stockDay]["3. low"])
            data[stockDay]["4. close"] = float(data[stockDay]["4. close"] )
            data[stockDay]["5. volume"] = float(data[stockDay]["5. volume"])
            days.append(data[stockDay])

    days = sorted(days, key=lambda x: x["sinceEpochDay"], reverse=False)
    return days



def main():
    if (len(sys.argv)<2):
        print "Invalid Number of Arguments, call python plot.py year"
    yeartoplot = str(sys.argv[1])
    with open('labeledDays.json') as f: 
        labeledData = json.load(f)

    with open('stocksbr.json') as f: 
        data = json.load(f)

    data = data["Time Series (Daily)"]
    days = stockDataToList(data)

    testYear =  yearOfstockDataToList(data,yeartoplot)
    testYearSize = len(testYear)
    x = []
    y = []
    z = []
    for i in range(0,testYearSize):
        if (testYear[i]["date"] in labeledData["buy"]):
            x.append(i)
            y.append(39)
            z.append(testYear[i]["4. close"])
        if (testYear[i]["date"] in labeledData["sell"]):
            x.append(i)
            y.append(37)
            z.append(testYear[i]["4. close"])
        if (testYear[i]["date"] in labeledData["wait"]):
            x.append(i)
            y.append(38)
            z.append(testYear[i]["4. close"])

    x = numpy.array(x)
    y = numpy.array(y)
    z = numpy.array(z)
    
    print x.shape
    print y.shape
    plt.plot(x, y)
    plt.plot(x, z)
    plt.show()




main()


'''
# load the dataset but only keep the top n words, zero the rest
top_words = 5000
(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=top_words)
# truncate and pad input sequences
max_review_length = 500
X_train = sequence.pad_sequences(X_train, maxlen=max_review_length)
X_test = sequence.pad_sequences(X_test, maxlen=max_review_length)
# create the model
embedding_vecor_length = 32
model = Sequential()
model.add(Embedding(top_words, embedding_vecor_length, input_length=max_review_length))
model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(LSTM(100))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(X_train, y_train, epochs=3, batch_size=64)
# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))
'''