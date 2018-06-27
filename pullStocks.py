import sys
import requests
import zipfile
import io
import csv
import json

def main():
    # start year and end year
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    chosenSymbol = sys.argv[3]

    # series description and registers
    desc = [
        "tipreg", "datprg", "codbdi", "codneg", "tpmerc", "nomres", "especi", 
        "prazot", "modref", "preabe", "premax", "premin", "premed", "preult", 
        "preofc", "preofv", "totneg", "quatot", "voltot", "preexe", "indopc", 
        "datven", "fatcot", "ptoexe", "codisi", "dismes"]
    registers = []

    for year in range(start, end + 1):
        print(year)

        # download
        f = download_file(year)
        
        # interpret
        r = interpret(f)
        registers += r

    print("mongo")

    jsonf = {}
    jsonf["Meta Data"] = {}
    jsonf["Meta Data"]["1. Information"] = "Daily Prices (open, high, low, close) and Volumes"
    jsonf["Meta Data"]["2. Symbol"] = chosenSymbol
    jsonf["Time Series (Daily)"] = {}

    for row in registers:
        if (row[3]==chosenSymbol):
            date = row[1][:4] + '-' + row[1][4:6] + '-' + row[1][6:8]
            jsonf["Time Series (Daily)"][date] = {}
            jsonf["Time Series (Daily)"][date]["1. open"] = str(row[9])
            jsonf["Time Series (Daily)"][date]["2. high"] = str(row[10])
            jsonf["Time Series (Daily)"][date]["3. low"] = str(row[11])
            jsonf["Time Series (Daily)"][date]["4. close"] = str(row[13])
            jsonf["Time Series (Daily)"][date]["5. volume"] = str(row[16])
            print jsonf["Time Series (Daily)"][date]
    
    with open("stocksbr.json", "w") as write_file:
        json.dump(jsonf, write_file)

    # covert to csv
    #f = open("mongo.csv", "w")
    #writer = csv.writer(f)
    #writer.writerow(desc)
    #writer.writerows(registers)
    #f.close()

def download_file(year):
    while True:
        try:
            # download zip
            url = ("http://bvmf.bmfbovespa.com.br/InstDados/SerHist/"
                    "COTAHIST_A" + str(year) + ".ZIP")
            r = requests.get(url)

            # open zip and file
            z = zipfile.ZipFile(io.BytesIO(r.content))
            f = z.open(z.namelist()[0], "r")

            # read file
            series = f.read().decode("latin1")

            f.close()
            z.close()

            return series
        except Exception as e:
            print(e)
            continue
        break

def interpret(f):
    lines = f.split("\n")

    '''
    header = []
    line = lines[0]
    header.append(line[0:2])
    header.append(line[2:15])
    header.append(line[15:23])
    header.append(line[23:31])

    trailer = []
    line = lines[-2]
    trailer.append(line[0:2])
    trailer.append(line[2:15])
    trailer.append(line[15:23])
    trailer.append(line[23:31])
    trailer.append(line[31:42])
    '''

    registers = []
    for line in lines[1:-2]:
        tipreg = line[0:2]
        datprg = line[2:10]
        codbdi = line[10:12]
        codneg = line[12:24]
        tpmerc = line[24:27]
        nomres = line[27:39]
        especi = line[39:49]
        prazot = line[49:52]
        modref = line[52:56]
        preabe = line[56:69]
        premax = line[69:82]
        premin = line[82:95]
        premed = line[95:108]
        preult = line[108:121]
        preofc = line[121:134]
        preofv = line[134:147]
        totneg = line[147:152]
        quatot = line[152:170]
        voltot = line[170:188]
        preexe = line[188:201]
        indopc = line[201:202]
        datven = line[202:210]
        fatcot = line[210:217]
        ptoexe = line[217:230]
        codisi = line[230:242]
        dismes = line[242:245]
        
        codneg = codneg.strip()
        preabe = round(float(preabe[:11]) + float(preabe[11:])/100, 2)
        premax = round(float(premax[:11]) + float(premax[11:])/100, 2)
        premin = round(float(premin[:11]) + float(premin[11:])/100, 2)
        premed = round(float(premed[:11]) + float(premed[11:])/100, 2)
        preult = round(float(preult[:11]) + float(preult[11:])/100, 2)
        preofc = round(float(preofc[:11]) + float(preofc[11:])/100, 2)
        preofv = round(float(preofv[:11]) + float(preofv[11:])/100, 2)
        totneg = int(totneg)
        quatot = int(quatot)
        voltot = round(float(voltot[:16]) + float(voltot[16:])/100, 2)
        preexe = round(float(preexe[:11]) + float(preexe[11:])/100, 2)
        fatcot = int(fatcot)
        ptoexe = round(float(ptoexe[:7]) + float(ptoexe[7:])/100, 2)
        dismes = int(dismes)

        register = [
            tipreg, datprg, codbdi, codneg, tpmerc, nomres, especi,
            prazot, modref, preabe, premax, premin, premed, preult,
            preofc, preofv, totneg, quatot, voltot, preexe, indopc,
            datven, fatcot, ptoexe, codisi, dismes]
        registers.append(register)

    return registers

if __name__ == "__main__":
    main()