"""
Pocket Options Bot - beta: Strats Reference File (strats.py)
Author: Skippy Flatrock
Date of Creation: 4/9/2022
Version 1.9:
"""

import datetime # To get current Date/Time
import pyautogui #module to press keyboard keys
def stratTags():
    return ['SCAN''THREE','NINE','FIFTEEN','THIRTY','FORTYFIVE','SIXTY','SEVENTYFIVE','NINTY','SixtyAverage',]
def stratInfo():
    return ['0. Scan',
           '1. SMAs in order place trade in that direction',
           '2. SMAs 1 cross over 2 while in direction of SMA 3 trend']
def strat1(priceHistory,stratSettings):
    if max(stratSettings)<len(priceHistory):
        temp = [0]
        count = 0
        SMACount = 0
        SMAIntervals = [0]
        for set in stratSettings:
            if count == 0:
                SMACount = set
                count = count + 1
            elif SMAIntervals[0]==0:
                SMAIntervals[0]=set
            else:
                SMAIntervals.append(set)
        for interval in SMAIntervals:
            tempSMA = movingAverageMostRecent(priceHistory,interval)
            if temp[0]==0:
                temp[0]=tempSMA   
            else:
                temp.append(tempSMA)
        triggerdirection=False # True is up false is down
        downTrigger = True
        upTrigger = True
        if temp[0]>temp[1]:#if first sma is on top then check for down
            triggerdirection = False
            downTrigger = True
            upTrigger = False
        elif temp[0]<temp[1]:
            triggerdirection = True
            downTrigger = False
            upTrigger = True
        else:
            downTrigger = False
            upTrigger = False
        count = 0
        temp1 = 0
        for avrgPrice in temp:
            if count ==0:
                temp1 = avrgPrice
                count = count +1
            else:
                if triggerdirection:
                    if upTrigger:
                        if temp1<avrgPrice:
                            upTrigger = True # pointless but helps afirm what it is doing
                            temp1 = avrgPrice # check to see if next sma is lower thus shift the temp to the next iteration.
                        else:
                            upTrigger = False    
                else:
                    if downTrigger:
                        if temp1>avrgPrice:
                            downTrigger = True # pointless but helps afirm what it is doing
                            temp1 = avrgPrice # check to see if next sma is lower thus shift the temp to the next iteration.
                        else:
                            downTrigger = False
        why = "Strat1 (SMAs in order) [SMA Multiplires,values]:," + str(SMAIntervals)+"," +str(temp)                  
        if downTrigger:
            #placeTrade("down",why)
            why = "Down trade triggered : " + why
        elif upTrigger:
            #placeTrade("up",why)
            why = "Up trade triggered : " + why
        else:
            why = ""
    else:
        t=1
        del(t)
        why=""
    return why

def strat2(priceHistory,stratSettings):
    triggerdirection=False
    if max(stratSettings)<len(priceHistory):
        temp = [0]
        count = 0
        SMACount = 0
        SMAIntervals = [0]
        # first grab all of the moving averages [SMAcount ,...,crossover=0 or 1 true or false(if 1 then following 2 will be a left trade direction when over the following)]
        for set in stratSettings:
            if count == 0:
                SMACount = set
            elif count >SMACount:
                break
            elif SMAIntervals[0]==0:
                SMAIntervals[0]=set
            else:
                SMAIntervals.append(set)
            count = count + 1
        #print ("Strat2 SMAIntervals:",SMAIntervals)
        #SMAIntervalse should have only the SMA intervals in them now
        smaCorssover = False
        smaPathMod = 0 # mod stands for modifier. It is used as the sma interval for the average
        smaCrossMod = 0
        if SMACount<len(stratSettings)-1:
            if stratSettings[SMACount+1]==1:
                smaCorssover = True
                smaCrossMod = stratSettings[SMACount+2]
                smaPathMod = stratSettings[SMACount+3]
        #print ("smaCorssover:",smaCorssover,"| smaCrossMod",smaCrossMod,"| smaPathMod",smaPathMod)
        for interval in SMAIntervals:
            tempSMA = movingAverage(priceHistory,interval)
            if temp[0]==0:
                temp[0]=tempSMA[0]   
            else:
                temp.append(tempSMA[0])
        #print("temp:",temp)
        triggerdirection=False # True is up false is down
        downTrigger = True
        upTrigger = True
        if temp[0]>temp[1]:#if first sma is on top then check for down
            triggerdirection = False
            downTrigger = True
            upTrigger = False
        elif temp[0]<temp[1]:
            triggerdirection = True
            downTrigger = False
            upTrigger = True
        else:
            downTrigger = False
            upTrigger = False
        count = 0
        temp1 = 0
        for avrgPrice in temp:
            if count ==0:
                temp1 = avrgPrice
                count = count +1
            else:
                if triggerdirection:
                    if upTrigger:
                        if temp1<avrgPrice:
                            upTrigger = True # pointless but helps afirm what it is doing
                            #print("UP Trend:",temp1,"<", avrgPrice)
                            temp1 = avrgPrice # check to see if next sma is lower thus shift the temp to the next iteration.
                        else:
                            upTrigger = False    
                else:
                    if downTrigger:
                        if temp1>avrgPrice:
                            downTrigger = True # pointless but helps afirm what it is doing
                            #print("UP Trend:",temp1,">", avrgPrice)
                            temp1 = avrgPrice # check to see if next sma is lower thus shift the temp to the next iteration.
                        else:
                            downTrigger = False
        #print ("upTrigger:",upTrigger,"| downTrigger",downTrigger)
        if smaCorssover:
            smaPath = movingAverage(priceHistory,smaPathMod)
            smaCross = movingAverage(priceHistory,smaCrossMod)
            why = "Strat2 (SMA tred + sma cross over) [SMA Multiplires,values,reason]:," + str(SMAIntervals)+"," +str(temp)+","
            if downTrigger and smaCross[1]>=smaPath[1]and smaCross[0]<smaPath[0]: # SMAs show momentum down desired (and) previous cross sma is = or greater than path sma (and) current cross has crossed below path sma
                why = "Down trade triggered : " + why + str(smaCross[1]) + ",>=," + str(smaPath[1]) + ",and," + str(smaCross[0]) + ",<," + str(smaPath[0])
                placeTrade("down",why)
                triggerdirection = False
            elif upTrigger and smaCross[1]<=smaPath[1]and smaCross[0]>smaPath[0]:
                why = "Up trade triggered : " + why + str(smaCross[1]) + ",<=," + str(smaPath[1]) + ",and," + str(smaCross[0]) + ",>," + str(smaPath[0])
                placeTrade("up",why)
                triggerdirection = True
            else:
                why = ""
    else:
        t=1
        del(t)
        why=""
    return why,triggerdirection

def placeTrade(upDown,why):#,invert):# places trade via keyboard shortcuts
    if upDown.lower() == "up":
        pyautogui.keyDown("shift")# Holds down key
        pyautogui.press("w")# Presses the key once
        pyautogui.keyUp("shift")# Lets go of the key
        print ("Up Trade Trigger:",why)
    elif upDown.lower() == "down":
        pyautogui.keyDown("shift")# Holds down key
        pyautogui.press("s")# Presses the key once  
        print ("Down Trade Trigger:",why)      
        pyautogui.keyUp("shift")# Lets go of the key

#indicators
def movingAverage(priceList,interval):
    tempList=[]
    count =0
    average=[]
    for price in priceList:
        count = count + 1
        if count >= interval:
            tempList.insert(0, price)
            if interval>0:
                average.insert(0,sum(tempList)/interval)
            else:
                average.insert(0,0)
            tempList.pop(len(tempList)-1)
        else:
            tempList.insert(0, price)
    average.reverse()
    return average # to make newest price index 0
def movingAverageMostRecent(priceList,interval):
    tempList=[]
    count =0
    #average=[]
    if interval>0:
        for price in priceList:
            count = count + 1
            if count >= interval:
                tempList.insert(0, price)
                return sum(tempList)/interval
                #tempList.pop(len(tempList)-1)
            else:
                tempList.insert(0, price)
    return 0 # to make newest price index 0