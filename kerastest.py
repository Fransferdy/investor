import numpy
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
import datetime
import json
from keras.utils import np_utils
from keras import regularizers
from keras.layers import Dropout
from keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt

M_BUY = 0
M_SELL = 1
M_WAIT = 2

# fix random seed for reproducibility
numpy.random.seed(7)




def getSinceEpochDay(dateString):
    year = int(dateString[0:4])
    month = int(dateString[5:7])
    day = int(dateString[8:10])
    #print dateString
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
    for i in range(1,60):
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

    with open('labeledDays.json') as f: 
        labeledData = json.load(f)

    with open('stocksbr.json') as f: 
        data = json.load(f)

    data = data["Time Series (Daily)"]
    days = stockDataToList(data)

    samples = []
    labels = []
    for i in range(0,10):
        addSamples(M_BUY, labeledData["buy"],days,samples,labels,i/10,0.1)
        addSamples(M_SELL, labeledData["sell"],days,samples,labels,i/10,0.1)
        addSamples(M_WAIT, labeledData["wait"],days,samples,labels,i/10,0.1)
    #print (samples)
    #print (labels)
    samples = numpy.array(samples)
    labels = numpy.array(labels)

    labels = np_utils.to_categorical(labels, 3)
    print labels

    model = Sequential()
    model.add(Dense(units=33, activation='relu', input_dim=len(samples[0]) ))
    model.add(Dropout(0.2))
    model.add(Dense(units=15, activation='relu'))
    #model.add(Dropout(0.1))
    model.add(Dense(units=7, activation='relu'))
    #model.add(Dense(units=8, activation='relu'))
    model.add(Dense(units=3, activation='softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['binary_accuracy', 'categorical_accuracy'])
    print(model.summary())

    filepath="weights.best.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    model.fit(samples, labels, epochs=600,validation_split=0.3, batch_size=1900,callbacks=callbacks_list)
    print model.metrics_names
    print model.evaluate(samples, y=labels,verbose=1,batch_size=1900)
    #result = model.predict(samples)
    #print result


    testYear =  yearOfstockDataToList(data,'2011')
    testYearSize = len(testYear)

    print testYearSize
    myMoney = 5000
    myAssets = 0
    buys = 0
    sells = 0
    waits = 0
    for i in range(0,testYearSize):
        dayFeature = [dayToFeature(testYear[i]["date"],testYear)]
        dayFeature = numpy.array(dayFeature)
        result = model.predict(dayFeature)
        
        maxopt = 0
        for k in range(0,2):
            if (result[0][k] > maxopt):
                #print result[i]
                opt = k
                maxopt  = result[0][k]
        
        if (opt==0): #buy
            amountToBuy = (myMoney-17)/testYear[i]["4. close"]
            if (amountToBuy>0):
                myMoney -= ( (amountToBuy*testYear[i]["4. close"]) + 17)
                myAssets+= amountToBuy
                waitCounter=0
                buys+= 1
                testYear[i]["opt"] = 44
            else:
                waits+=1
                testYear[i]["opt"] = 43
        if (opt==1): #sell
            if (myAssets>0):
                myMoney -= 17
                myMoney += testYear[i]["4. close"]*myAssets
                myAssets= 0
                waitCounter=0
                sells+= 1
                testYear[i]["opt"] = 42
            else:
                waits+=1
                testYear[i]["opt"] = 43
        if (opt==2): #wait
            waitCounter+= 1
            if (waitCounter>=30):
                waitCounter = 0
                myMoney -= 17
            waits+=1
            testYear[i]["opt"] = 43

    worth = (myAssets * testYear[len(testYear)-1]["4. close"]) + myMoney
    print "money ", myMoney
    print "assets ", myAssets
    print "worth ",worth
    print "buys ",buys
    print "sells ",sells
    print "waits ",waits

    #testYear =  days#yearOfstockDataToList(data,'2013')
    #testYearSize = len(testYear)
    x = []
    y = []
    z = []
    k = []
    for i in range(0,testYearSize):
        k.append(testYear[i]["opt"])
        if (testYear[i]["date"] in labeledData["buy"]):
            x.append(i)
            y.append(39)
            z.append(testYear[i]["4. close"])
        else:
            if (testYear[i]["date"] in labeledData["sell"]):
                x.append(i)
                y.append(37)
                z.append(testYear[i]["4. close"])
            else:
                x.append(i)
                y.append(38)
                z.append(testYear[i]["4. close"])


    x = numpy.array(x)
    y = numpy.array(y)
    z = numpy.array(z)
    k = numpy.array(k)
    
    print x.shape
    print y.shape

    plt.plot(x, y)
    plt.plot(x, z)
    plt.plot(x, k)
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