import datetime
import urllib.request as r #YahooFinance.com json Source: used to read Websites
import time
import json

#need to add check for which url is active. isOnline(Ticker)?
def getDataDic(Ticker):
    #urll='https://query1.finance.yahoo.com/v8/finance/chart/CADJPY=X'
    #https://query2.finance.yahoo.com/v7/finance/quote?symbols=CADJPY=X
    #https://query2.finance.yahoo.com/v7/finance/quote?symbols=ETH-USD
    #urll='https://query2.finance.yahoo.com/v7/finance/chart/'+Ticker+'=X'
    urll='https://query2.finance.yahoo.com/v7/finance/chart/'+Ticker
    priceData=[]
    count = 0
    count= count+1
    try:
        page = str(r.urlopen(urll).readlines()) # downloads all Text and Variables from URL 
    except:
        print("404")
        return "404 Error"
    #print (page)
    #input ()
    
    page = page.replace('"',"").replace('{',"").replace('}',"").replace('[',"").replace(']',"")
    '''
    page = page.replace('"',"")
    page = page.replace('{',"")
    page = page.replace('}',"")
    page = page.replace('[',"")
    page = page.replace(']',"")'''
    data = page.split(",")
    dataDic ={"key":"var"}
    for dat in data:
        temp = dat.split(":")
        #print (temp)
        #input()
        if len(temp)>=2:# could add if key exists do key+"1"
            dataDic [temp[len(temp)-2]] = temp[len(temp)-1]
    
    
    '''rawData = page.split(",") # variables are seperated by comma.
    price=str(rawData[9]).replace('"regularMarketPrice":',"") # index 9 is where the current price is in the json file
    price = price.replace(" ","")
    return float(price)'''
    return dataDic
def timeConvert(dataDic,key):
    timeZoneShift = 0
    if dataDic["timezone"] == "BST":
        timeZoneShift = 8*60*60
    #print ("key:",key)
    return datetime.datetime.fromtimestamp(int(dataDic[key])+timeZoneShift)
def isOpen(Ticker):
    dataDic = getDataDic(Ticker)
    closeTime = timeConvert(dataDic,"end")
    #print (closeTime)
    #print (datetime.datetime.now())
    if closeTime < datetime.datetime.now():
        return False
    else:
        return True
def getPrice(Ticker):
    #print (Ticker)
    dataDic = getDataDic(Ticker)
    #print (dataDic)
    if isOpen(Ticker):
        return float(dataDic["regularMarketPrice"])
    return 0

if __name__ == "__main__":  
    print("source.py has been run")  
    Ticker = "AUDCHF=X"
    dataDic =getDataDic(Ticker)
    print ("dataDic:\n",dataDic)
    print ("Regular market price\n",dataDic["regularMarketPrice"])
    print ("start\n",timeConvert(dataDic,"start"))
    print ("end\n",timeConvert(dataDic,"end"))
    print (isOpen(Ticker))
else:
   print("source.py has been imported")
