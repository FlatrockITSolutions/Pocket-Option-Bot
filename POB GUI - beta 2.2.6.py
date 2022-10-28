'''
Pocket Option Bot GUI - beta
Author: Skippy Flatrock
Date of creation 4/15/2022
Version 2.2.4:

What was Added:
    2.2.4 added:
        chart update every placed trade (when trade count changes chart updates)
        continually checks to place a trade till trade has been placed then waits a period of time and repeat
    2.2.3 added strat 2
    2.2.2 removed auto chart update
        The old chart data is still being stored somehwere thus the trash collector never cleares the used ram.
    2.2.0 added:
        setting changer which allws user to change thier who trading strategy while still scanning the same market in the back ground
        allowed for the market scan thread to start when user enters a ticker
        fixed bugs with trading strat 1
        caused the start button to check to see if anything needs to be started before it starts the update switch or the market loop.
            if the market loop is already running then it will not start a duplicate one like in the past
            also the start button checks to see if the chart update loop is turned on if not it turns it on when clicked. 
        setting changer button stops the chart from updating but allows user to see old settings for easy re entry. 
    2.1.3 added a static price delay however if the strat has to wait a period of time to start 
        placing trades it will continually place trades till the quota is reached since program start.
            need ot add if count = 0 then count = len(priceHistory)/delay to it is caught up to speed.
    2.1.1 added Scan strat 0
    Multiwindows
    3 sub windows to gather strat settings and market ticker information.
    2.0.7 added dynamic SMAs
    uses this infomration to place trades.
'''

#from ensurepip import bootstrap
import datetime
from turtle import color
import Pocket_Option_Bot as bot # imports terminl bot module
import strats
import PySimpleGUI as sg # imports window libraies
import matplotlib.pyplot as plt # used to plot the chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # used to plot the chart


def draw_figure(canvas, figure): # draws the place holder or figure inside the canvase to hold the chart. 
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    del(canvas,figure)
    return figure_canvas_agg

def makeData(stratIndex,moving_average_intervals,price_history_buffer): # used to update the chart data
    priceHistoryListCopy = bot.getPriceHistoryList() 
    yDatas=[[0]]
    xDatas=[[0]]
    if stratIndex==0:
        del(stratIndex)
        yData = []
        xData = []
        count = 0
        for price in priceHistoryListCopy:
            if count<price_history_buffer:#only charts the 600 most recent price changes
                count = count +1
                xData.insert(0,count)  #[n,...,2,1]
                yData.append(price)    #[new,...,old]
            else:
                break
        del(count,priceHistoryListCopy)
        yDatas[0] = yData# records price y
        xDatas[0] = xData# for each interval of time
        del(yData,xData)
    elif stratIndex==1 or stratIndex==2:
        yData = []
        xData = []
        count = 0
        for price in priceHistoryListCopy:
            if count<price_history_buffer:#only charts the 600 most recent price changes
                count = count +1
                xData.insert(0,count)  #[n,...,2,1]
                yData.append(price)    #[new,...,old]
            else:
                break
        yDatas[0] = yData# records price y
        xDatas[0] = xData# for each interval of time
        for interval in moving_average_intervals:
            if interval<=len(priceHistoryListCopy):
                tempMA = []
                tempMA = strats.movingAverage(priceHistoryListCopy,interval)  #[new,...,old]
                if tempMA == None:
                    t=1
                    del(t)
                else:
                    yDataTemp=tempMA[:price_history_buffer]
                    xDataTemp = xData[:len(yDataTemp)] # for if the yDataTemp is smaller than the price list probably wont happen 
                    yDatas.append(yDataTemp)
                    xDatas.append(xDataTemp)
        del(yData,xData,count,priceHistoryListCopy,stratIndex)    
    else:
        yData = []
        xData = []
        yDatas[0] = yData# records price y
        xDatas[0] = xData# for each interval of time
        del(yData,xData,priceHistoryListCopy,stratIndex)
    #print("MakeData() returns [",yDatas,",",xDatas,"]")
    #print ()
    return [yDatas,xDatas]

def drawChart(moving_average_intervals,price_history_buffer): # used to draw the data for the first time
    _VARS['pltFig'] = plt.figure()
    plt.ioff()
    dataXY = makeData(0,[],price_history_buffer)
    del(price_history_buffer)
    plt.plot(dataXY[1][0], dataXY[0][0],color='r',label="Price")#, '.k')
    for interval in moving_average_intervals:
        #print("drawChartLoop Interval:",interval)
        plt.plot(dataXY[0][0], dataXY[1][0],color='b',label="SMA")#, '.k')
    del(dataXY)
    
    plt.figtext(0.35, 0.9, "Trade Trigger Stopped", fontdict=None)#, **kwargs)
    '''plt.plot(dataXY[2], dataXY[3],color='b',label="MA 3")#, '.k')
    plt.plot(dataXY[4], dataXY[5],color='g',label="MA 6")#, '.k')'''
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer,tradeHistory): #Used to update the data after the chart as been initalized.
    #this function causes a ram leak, every time teh chart is re drawn it uses more ram. not sure how to release the ram.
    _VARS['fig_agg'].get_tk_widget().forget()
    #plt.close()
    plt.clf()
    #plt.ioff()
    print ("       tradeHistory", tradeHistory)
    dataXY = makeData(stratIndex,moving_average_intervals,price_history_buffer)
    #dataXY=[[1,2,3],[1,2,3]]
    del(moving_average_intervals,price_history_buffer)
    loop=[0]*len(dataXY[0])
    count = 0
     # clears the previous chart to make room for the redraw.
    if stratIndex==2:
        for lo in loop:
            if count==0:
                plt.plot(dataXY[1][0], dataXY[0][0],color='black', marker='o', linestyle='dashed')
            elif count >= len(dataXY[0])-1:
                plt.plot(dataXY[1][count], dataXY[0][count],color='Red',linewidth=1.5)#, marker='o', linestyle='dashed')
            elif count >= len(dataXY[0])-2:
                plt.plot(dataXY[1][count], dataXY[0][count],color='Green',linewidth=1.5)#, marker='o', linestyle='dashed')
            else:
                plt.plot(dataXY[1][count], dataXY[0][count],linestyle='dashed',linewidth=.8) # [Xs][x1,...,xn],[Ys][y1,...,yn]
            count = count +1
        del(loop)
    else:
        for lo in loop:
            if count==0:
                plt.plot(dataXY[1][0], dataXY[0][0],color='black', marker='o', linestyle='dashed')
            else:
                plt.plot(dataXY[1][count], dataXY[0][count]) # [Xs][x1,...,xn],[Ys][y1,...,yn]
            count = count +1
        del(loop)
    #draws up trades
    if tradeHistory[0][0] == 0:
        tradeHistory[0][0] = 0
    else:
        count = 0
        for price in tradeHistory[0]:
            if count <6:
                plt.axhline (price,color = "green",linestyle ="--",linewidth=.5)
            count = count + 1
    #draws down trades
    if tradeHistory[1][0] == 0:
        tradeHistory[1][0] = 0
    else:
        count =0
        for price in tradeHistory[1]:
            if count <6:
                plt.axhline (price,color = "red",linestyle ="--",linewidth=.5)
            count = count + 1
    if trade_switch:
        tempString="Price (Black): "+str(dataXY[0][0][0])
        plt.figtext(0.35, 0.9, tempString, fontdict=None)#, **kwargs)
        del (tempString)
    else:
        plt.figtext(0.35, 0.9, "Trade Trigger Stopped", fontdict=None)#, **kwargs)  
    #plt.figtext(1.1, 1.9, "test", fontdict=None)#, **kwargs)
    del(stratIndex)
    '''loop=[0]*count
    for lo in loop:
    del(count,dataXY,loop)'''
    '''plt.clf() # clears the previous chart to make room for the redraw.
    plt.plot(dataXY[0], dataXY[1],color='r',label="Price")#, '.k')
    plt.plot(dataXY[2], dataXY[3],color='b',label="MA 3")#, '.k')
    plt.plot(dataXY[4], dataXY[5],color='g',label="MA 6")#, '.k')'''
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def subWindow1(stratList,defaultStratIndex):
    stratListString = ""
    stratIndex = -1
    for strat in stratList:
        stratListString = stratListString + "\n" +strat
    layout = [[sg.Text('What strategy index do you want?'), sg.InputText(defaultStratIndex)],
              [sg.Text('Strat List:')],
              [sg.Text(stratListString)],
              [sg.Button('Continue')]]
    window = sg.Window('Pocket Option Bot - SubMenu 1', layout, finalize=True, element_justification='center', font='Helvetica 18')
    terminate = False
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            stratIndex = 0
            break
        if event == 'Continue':
            try:
                temp = int(values[0])
                if 0<=temp and temp<len(stratList):
                    stratIndex = temp
                    defaultStratIndex = str(temp)
                    terminate = True
                    break
                else:
                    print ("Not 0 <= or <",len(stratList))
            except:
                print ("enter data error:",event, values)
        if terminate:
            break
    window.close()
    return int(stratIndex),defaultStratIndex      
def subWindow2(stratList,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover):
    terminate = False
    subWindow=True
    while subWindow:
        stratIndex,defaultStratIndex = subWindow1(stratList,defaultStratIndex)
        stratSettings = []
        if stratIndex == 1: # if strat 1 is true gathers user input for strat settings and returns it to be return at the ent of the function
            SmaMultipliers = []     
            stratDescription = 'Strategy: '+str(stratList[stratIndex])
            layout = [[sg.Text(stratDescription)],
                    [sg.Text('How many Moving Averages?'), sg.InputText(len(strat1DefaultSMAs.split(',')))],
                    [sg.Text('What is the multipier for each SMA? (seperate by ,s)'), sg.InputText(strat1DefaultSMAs)],
                    [sg.Button('Back'),sg.Button('Continue')]]
            window = sg.Window('Pocket Option Bot - SubMenu 2', layout, finalize=True, element_justification='center', font='Helvetica 18')
            terminate = False
            while True:
                stratSettings = []
                event, values = window.read()
                if event == sg.WIN_CLOSED:
                    break
                if event == 'Back':
                    window.close()
                    break
                if event == 'Continue':
                    try:
                        temp = values[0]
                        temp = int(temp)
                        if 1<=temp:
                            stratSettings.append(temp)
                            temp = str(values[1])
                            temp.replace(" ","")
                            SmaMultipliers = temp.split(",")
                            if stratSettings[0] == len(SmaMultipliers):
                                for SmaMultiplyer in SmaMultipliers:
                                    if int(SmaMultiplyer)>0:
                                        terminate = True
                                    else:
                                        terminate = False
                            else:
                                print ("SMA Count:",stratSettings[0],"does not = the count of",len(SmaMultipliers))
                        else:
                            print ("Not 0 <= or <",len(stratList))
                    except:
                        print ("enter data error:",event, values)
                if terminate:
                    window.close()
                    subWindow = False
                    break
            strat1DefaultSMAs = ''
            for SmaMultiplyer in SmaMultipliers:
                stratSettings.append(int(SmaMultiplyer))
                if strat1DefaultSMAs == '':
                    strat1DefaultSMAs = str(SmaMultiplyer)
                else:
                    strat1DefaultSMAs=strat1DefaultSMAs+','+str(SmaMultiplyer)
        elif stratIndex == 2: # if strat 1 is true gathers user input for strat settings and returns it to be return at the ent of the function
            SmaMultipliers = []     
            stratDescription = 'Strategy: '+str(stratList[stratIndex])
            layout = [[sg.Text(stratDescription)],
                    [sg.Text('Trend: Please enter the SMAs that you wish to use to deetermin trend.',font=(12))],
                    [sg.Text('What is the multipier for each SMA? (seperate by ,s)'), sg.InputText(strat2DefaultTrendSMAs)],
                    [sg.Text('What is the multipier for the Path and Cross SMA? (seperate by ,s)'), sg.InputText(strat2DefaultCorssover)],
                    [sg.Text('Path: is the semi stationary moving average that is crossed\nCorss: is the moving average that cross over the Path\nex: 3,7 (this means there will be a trade triggered in the direction of the 3 corssing over the 7 if the trent is also in that direction.)')],
                    [sg.Button('Back'),sg.Button('Continue')]]
            window = sg.Window('Pocket Option Bot - SubMenu 2', layout, finalize=True, element_justification='left', font='Helvetica 18')
            terminate = False
            while True:
                stratSettings = []
                event, values = window.read()
                if event == sg.WIN_CLOSED:
                    break
                if event == 'Back':
                    window.close()
                    break
                if event == 'Continue':
                    try:
                        '''temp = values[0]
                        temp = int(temp)
                        if 1<=temp:'''
                        temp = str(values[0])
                        temp.replace(" ","")
                        SmaMultipliers = temp.split(",")
                        stratSettings.append(len(SmaMultipliers))
                        #if stratSettings[0] == len(SmaMultipliers):
                        for SmaMultiplyer in SmaMultipliers:
                            if int(SmaMultiplyer)>0:
                                terminate = True
                            else:
                                print("0 SMAs sellected for trend")
                                terminate = False
                        strat2DefaultTrendSMAs = ''
                        for SmaMultiplyer in SmaMultipliers:
                            if strat2DefaultTrendSMAs == '':
                                strat2DefaultTrendSMAs = str(SmaMultiplyer)
                            else:
                                strat2DefaultTrendSMAs=strat2DefaultTrendSMAs+","+str(SmaMultiplyer)
                            stratSettings.append(int(SmaMultiplyer))
                        temp = str(values[1])
                        temp.replace(" ","")
                        SmaCorssoverRaw = temp.split(",")
                        strat2DefaultCorssover = ''
                        for SmaCorssover in SmaCorssoverRaw:
                            if int(SmaCorssover)>0:
                                terminate = True
                            else:
                                print("0 SMAs sellected for trend")
                                terminate = False
                        if len(SmaCorssoverRaw) ==2:
                            stratSettings.append(1)
                            strat2DefaultCorssover = str(SmaCorssoverRaw[0]) + "," + str(SmaCorssoverRaw[1])
                            stratSettings.append(int(SmaCorssoverRaw[0]))
                            stratSettings.append(int(SmaCorssoverRaw[1]))
                        else:
                            stratSettings.append(0)
                        #stratSettings.append(SmaCorssoverRaw[0]) ()
                        '''else:
                            print ("SMA Count:",stratSettings[0],"does not = the count of",len(SmaMultipliers))
                        
                        else:
                            print ("Not 0 <= or <",len(stratList))'''
                    except:
                        print ("enter data error:",event, values)
                if terminate:
                    #print ("stratSettings:",stratSettings)
                    window.close()
                    subWindow = False
                    break
            
        else:
            subWindow = False
    #print ("Sub window 2: ",stratIndex,stratSettings)
    #if terminate:
    return stratIndex,stratSettings,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover
def subWindow3(Ticker):
    layout = [[sg.Text('What Ticker do you want?'), sg.InputText(Ticker)],
              [sg.Checkbox('Is this a currency Pair?', default=True, key="PAIR")],
              [sg.Button('Continue')]]
    window = sg.Window('Pocket Option Bot - SubMenu 1', layout, finalize=True, element_justification='left', font='Helvetica 18')
    #fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    terminate = False
    Ticker=""
    marketScanOff = True
    while True:
        event, values = window.read()
        #print(event, values)
        if event == sg.WIN_CLOSED:
            Ticker = "AUDJPY=X"
            window.close()
            break
        if event == 'Continue':
            try:
                temp = values[0]
                temp = str(temp)
                temp.replace(" ","")
                if values['PAIR']:
                    Ticker = temp.upper()+"=X"
                else:
                    Ticker = temp.upper()
                print("delaySec =", delaySec)      
                bot.bootStrapper(Ticker,delaySec)
                print ("bootStrapper started")
                #except:
                print ("entered data error")
                marketScanOff = False
                window.close()
                break
            except:
                print (event,values)
    #print ("Sub windows 3: Ticker=",Ticker)
    return Ticker, marketScanOff
            
def tradeTrigger(stratIndex,stratSettings,tradeCount,tradeCountBuff,tradeHistory):
    priceHistory = bot.getPriceHistoryList()
    #moving_average_intervals=[0]
    #print ("             Trade Trigger Ran")
    if stratIndex == 0:
        del(stratIndex,stratSettings,tradeCount,tradeCountBuff)
        return 0,0,[0],tradeHistory
    elif stratIndex == 1 :
        del(stratIndex)
        moving_average_intervals=[0]
        stop = 0
        for interval in stratSettings:
            if stop == 0:#Takes First 
                stop = interval
            elif moving_average_intervals[0] == 0:#edits the place holder for the mAIs List so that append can work
                moving_average_intervals[0]=interval
            else:
                moving_average_intervals.append(interval)
        del(stop)        
        #print ("     ",(tradeCount+tradeCountBuff),"<",(len(priceHistory)/tradeDelay))
        #print ("         trade buff:",tradeCountBuff)
        if tradeCount+tradeCountBuff<len(priceHistory)/tradeDelay:
            why=strats.strat1(priceHistory,stratSettings)            
            #print ("         Strat 1: Trade Trigger Check")
            if why=="":
                t=1
                del(t)
            else:
                tradeCountBuff = round(len(priceHistory)/tradeDelay)-tradeCount
                #print ("         new trade buff",tradeCountBuff) 
                bot.newTradeLogEntry(why+" ~ "+str(datetime.datetime.now()))
                tradeCount=tradeCount+1
                print ("Trade Count:",tradeCount,"  Trade Triggered")
            del(priceHistory,why)    
        return tradeCount,tradeCountBuff,moving_average_intervals
    elif stratIndex == 2:
        del(stratIndex)
        moving_average_intervals=[0]
        count = 0
        SMACount = 0
        for set in stratSettings:
            if count == 0:
                SMACount = set
            elif count >SMACount:
                break
            elif moving_average_intervals[0]==0:
                moving_average_intervals[0]=set
            else:
                moving_average_intervals.append(set)
            count = count + 1
        #smaCrossover = False
        smaPathMod = 1 # mod stands for modifier. It is used as the sma interval for the average
        smaCrossMod = 1
        if SMACount<len(stratSettings)-1:
            if stratSettings[SMACount+1]==1:
                #smaCrossover = True
                smaCrossMod = stratSettings[SMACount+2]
                smaPathMod = stratSettings[SMACount+3]
        moving_average_intervals.append(smaCrossMod)
        moving_average_intervals.append(smaPathMod)    
        '''for interval in stratSettings:
            if stop == 0:#Takes First 
                stop = interval
            elif moving_average_intervals[0] == 0:#edits the place holder for the mAIs List so that append can work
                moving_average_intervals[0]=interval
            else:S
                moving_average_intervals.append(interval)'''
        del(count)
        #print ("     ",(tradeCount+tradeCountBuff),"<",(len(priceHistory)/tradeDelay))
        if tradeCount+tradeCountBuff<len(priceHistory)/tradeDelay:
            #print ("         Strat 2: Trade Trigger Check")
            why,trade=strats.strat2(priceHistory,stratSettings)
            if why=="":
                t=1
                del(t)
            else:
                tradeCountBuff = round(len(priceHistory)/tradeDelay)-tradeCount
                if trade:
                    if tradeHistory[0][0] == 0:
                        tradeHistory[0][0] = priceHistory[0]
                    else:
                        tradeHistory[0].insert(0,priceHistory[0])
                else:
                    if tradeHistory[1][0] == 0:
                        tradeHistory[1][0]= priceHistory[0]
                    else:
                        tradeHistory[1].insert(0,priceHistory[0])
                ''' else:
                    #print ("up trade in why fail")'''
                bot.newTradeLogEntry(why+" ~ "+str(datetime.datetime.now()))
                tradeCount=tradeCount+1
                print ("Trade Count:",tradeCount,"  Trade Triggered")
                '''if trade:
                else:
                    print ("down trade in why fail")'''
            del(priceHistory,why)    
        return tradeCount,tradeCountBuff,moving_average_intervals,tradeHistory
    else:
        return tradeCount,tradeCountBuff,[0],tradeHistory
        

tradeDelay = 10
tradeCount = 0
tradeCountBuff = 0
delaySec = 1.0
defaultStratIndex = '0'
strat1DefaultSMAs = '60,30,15,7'
strat2DefaultTrendSMAs = '1500,420,105,1'
strat2DefaultCorssover = '45,105'
tradeHistory=[[0],[0]] # up , down
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}     
stratList=['0. Scan',
           '1. SMAs in order place trade in that direction',
           '2. SMAs 1 cross over 2 while in direction of SMA 3 trend'
           ]
#price_history_buffer=600
price_history_buffer= 60
sg.theme('DarkAmber') 
'''temp = subWindow3()
Ticker = temp[0]
marketScanOff = temp[1]
del(temp)'''
Ticker = 'audjpy'
Ticker,marketScanOff = subWindow3(Ticker)
print ("Ticker:", Ticker)
#Temp = subWindow2(stratList)
stratIndex,stratSettings,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover = subWindow2(stratList,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover)
#stratIndex = Temp[0]
print ("stratIndex:", stratIndex)
#stratSettings = Temp[1]
print ("stratSettings:", stratSettings)
#del(Temp)
bootstrap = True
while bootstrap:    #print ("Trade Count:",tradeCount,"beginning of GUI")
    tradeCount,tradeCountBuff,moving_average_intervals,tradeHistory = tradeTrigger(stratIndex,stratSettings,tradeCount,tradeCountBuff,tradeHistory)
    print ("moving_average_intervals:",moving_average_intervals)
    '''temp = tradeTrigger(stratIndex,stratSettings,tradeCount,tradeCountBuff) # needs to be changes for different strats
    tradeCount=temp[0]
    tradeCountBuff = temp[1]
    moving_average_intervals = temp[2]'''
    marketTickerTemp = 'Market Ticker: '+Ticker
    price_history_bufferTemp = "Chart History is "+ str(price_history_buffer)+" prices."
    textBoxTemp1 = ""
    if stratIndex==0:
        textBoxTemp1 = "Scanning Market"
    elif stratIndex==1:
        textBoxTemp1 = "Number of moving averages selected: " + str(stratSettings[0])
        count = 0
        for interval in moving_average_intervals:
            count = count+1
            textBoxTemp1 = textBoxTemp1+"\nMoving Average "+str(count)+": "+str(interval)
    elif stratIndex==2:
        textBoxTemp1 = "Number of moving averages selected: " + str(stratSettings[0])
        count = 0
        for interval in moving_average_intervals:
            count = count+1
            if count > len(moving_average_intervals)-1:
                textBoxTemp1 = textBoxTemp1+"\nPath (Red): "+str(interval)
            elif count > len(moving_average_intervals)-2:
                textBoxTemp1 = textBoxTemp1+"\nCrossover (Green): "+str(interval)
            else:
                textBoxTemp1 = textBoxTemp1+"\nMoving Average "+str(count)+": "+str(interval)
        
    layout = [  [sg.Text(marketTickerTemp)],
                [sg.Text(price_history_bufferTemp)],
                [sg.Text(textBoxTemp1)],
                [sg.Button('Start'), sg.Button('Exit'),sg.Button('Update Chart'),sg.Button('Trade Switch'),sg.Button('Change Settings'),sg.Button('Change Market')],
                [sg.Canvas(key='figCanvas')]]
    _VARS['window'] = sg.Window('Pocket Option Bot - Beta 8.0.0.8',
                                layout,
                                finalize=True,
                                resizable=True,
                                location=(100, 100),
                                element_justification="Left")
    del(marketTickerTemp,price_history_bufferTemp,textBoxTemp1)
    drawChart(moving_average_intervals,price_history_buffer)
    trade_switch = False
    delaySec = 1.0
    while True:
        event, values = _VARS['window'].read(timeout=10) # timeout is the delay in milliseconds | timout needed or it will never rerun the trade check
        if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks Exit
            bot.putTerminate(True)
            bootstrap=False
            break
        if trade_switch:
            tempTradeCount = tradeCount
            tradeCount,tradeCountBuff,moving_average_intervals,tradeHistory = tradeTrigger(stratIndex,stratSettings,tradeCount,tradeCountBuff,tradeHistory)
            if tempTradeCount == tradeCount:
                del(tempTradeCount)
            else:
                updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer,tradeHistory)
                del(tempTradeCount)                
            '''temp = tradeTrigger(stratIndex,stratSettings,tradeCount,tradeCountBuff)
            tradeCount=temp[0]
            tradeCountBuff = temp[1]
            moving_average_intervals = temp[2]'''
            #updateChart(stratIndex,moving_average_intervals,price_history_buffer)
            '''except:
                print ("Chart Update Error")'''
        if event == 'Update Chart':
            updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer,tradeHistory)
        if event == 'Change Settings':
            trade_switch = False
            del(stratIndex,stratSettings)
            stratIndex,stratSettings,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover=subWindow2(stratList,defaultStratIndex,strat1DefaultSMAs,strat2DefaultTrendSMAs,strat2DefaultCorssover)
            #stratIndex = Temp[0]
            print ("stratIndex:", stratIndex)
            #stratSettings = Temp[1]
            print ("stratSettings:", stratSettings)
            #del(Temp)
            bootstrap = True
            break
        if event == 'Change Market':
            bot.putTerminate(True)
            Ticker, marketScanOff = subWindow3(Ticker)
            print ("Ticker:", Ticker)
        if event == 'Trade Switch':
            if trade_switch:
                trade_switch = False
            else:
                trade_switch = True
            updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer,tradeHistory)
        if event == 'Start':
            if marketScanOff:
                print('Market Ticker: You entered ', Ticker) # may never start due to sub window 3
                try:
                    print("delaySec =", delaySec)      
                    bot.bootStrapper(Ticker,delaySec)
                    print ("bootStrapper started")
                    trade_switch=True
                    updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer)
                    marketScanOff=False
                except:
                    print ("entered data error")
                    marketScanOff = True
            else:
                if trade_switch==False:
                    trade_switch = True
            updateChart(trade_switch,stratIndex,moving_average_intervals,price_history_buffer,tradeHistory)
        del(event, values)
    _VARS['window'].close()
#window.close()