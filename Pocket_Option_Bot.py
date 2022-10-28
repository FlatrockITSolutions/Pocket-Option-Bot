"""
Pocket Options Bot - beta
Author: Skippy Flatrock
Date of creation 4/9/2022
Version 5.0.7:

What was Added:
    Strips it down to start the price Updater
    and be a logger for other events such as price triggers. 
    terminate queue passed from main program to terminate the price logger.
    reduced price lag to .02 so 10 minutes to the program is really 10.2 minutes of history
    negative time delay catch
"""

from queue import Queue
from threading import Thread
import datetime
import os
import time

import source as source
import strats as strats

#used to return recorded price data to main program
def getPriceHistoryList():
    return priceHistoryList
#used to send a "False" trigger to terminate the price scan thread
def putTerminate(TF):
    terminate.put(TF)
# Log Functions (Folder creation, creation of new log files, and log file fillers)
def createLogFolder(folderPath):
    try:
        os.mkdir(folderPath)
    except:
        t=1#print("Folder already exists:",folderPath)
    return folderPath+'/' 
def createLogFile(folderPath,fileName):
    folderPath = createLogFolder(folderPath)
    logFileName = str(datetime.datetime.now())
    logFileName = logFileName.replace(':',';')
    filePath=folderPath+fileName+logFileName+".txt"
    logEntry=filePath
    log = open(filePath, 'a')
    log.write(logEntry)
    log.close()
    return filePath

def newLogEntry(logEntry): #Default Bot Log
    log = open(filePath, 'a')
    log.write("\n"+logEntry)
    log.close()
def newMarketLogEntry(logEntry): # Market Price Entries only
    log = open(filePath2, 'a')
    log.write("\n"+logEntry)
    log.close()
def newTradeLogEntry(logEntry): # Trade Trigger Entries only
    log = open(filePath3, 'a')
    log.write("\n"+logEntry)
    log.close()

#Thread 1: Collects Price (Could be in a sub module)
def priceCollector(marketTicker,priceHistoryList,delaySec):
    scanCount =0
    delayOffSet =0
    while (True):
        scanCount=scanCount + 1
        market_price = source.getPrice(marketTicker)
        if priceHistoryList[0] == 0:#checks to see if the program has replaced the place holder at index 0 with an accurate market price. 
            priceHistoryList[0] = market_price
        else:
            priceHistoryList.insert(0,market_price)# shifts the list of data to the right one index leaving room for the new price.
            newLogEntry(str(marketTicker)+": "+str(market_price)+" : "+str(datetime.datetime.now())) #adds price to master log
            newMarketLogEntry(str(marketTicker)+" ~ "+str(market_price)+" ~ "+str(datetime.datetime.now())) # adds same log entry to Market Price Log File
        print(str(scanCount)+'.', marketTicker,' Market Price: ', market_price)#,"                                                            ") # 60 spaces to remove the progress bar
        
        delayTimerEnd=round(time.time())
        try:
            delayOffSet=delayTimerEnd-delayTimerStart
        except:
            delayOffSet=0
        try:
            time.sleep(delaySec-delayOffSet)
        except:
            print("previous took more than",delaySec,"seconds. Skipped delay.")
        delayTimerStart=round(time.time())
        if terminate.get():
            putTerminate(False)
            print ("Scan Terminated")
            break
        else:
            putTerminate(False)
             #break is used to break out of a while loop. in this instance it is the only way to break out of the loop since the loop will always be true. could use a for loop for this.   

def bootStrapper(marketTicker,delaySec):
    print ("Starting market scan for",marketTicker)
    t1 = Thread(target = priceCollector, args =(marketTicker,priceHistoryList,delaySec))
    t1.start()

terminate = Queue() 
putTerminate(False)
priceHistoryList=[0]    
# Create Log
filePath= createLogFile("PocketOptionBotLogs","PocketOptionLog - ")
filePath2= createLogFile("PocketOptionBotLogs","MarketPriceLog - ")
filePath3= createLogFile("PocketOptionBotLogs","TradeTriggerLog - ")
