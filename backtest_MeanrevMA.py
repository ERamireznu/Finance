#v: 18/01/26
import pandas as pd
import yfinance as yf
import math
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import fs_Mrev_v07 as fs_M
tt, ff = True, False

# params ==============================================\/

sto = 'WMT'
ndays = 920 #252*2 # number of days (bars)
per_ref = 2.0  #(%)
Only_1_atatime = tt

#data milestones:
MAsearch_beg = 0 
MAsearch_end = 300
Evalua_beg = MAsearch_end
Evalua_end = ndays

#---------
prms01 = ff #gral search of best MAs
if prms01:
    periods = [x for x in range(30, 150, 1)]
    MA_Display = tt
    PrintDetails = ff
    MA_NumResults = 10
    #---------
    Evaluation = ff
    Chart = ff
#---------
prms02 = tt   #specific MA: evaluation, chart
if prms02:
    periods = [36]
    PrintDetails = tt
    MA_Display = ff
    #---------
    Evaluation = tt
    Chart = tt
    
# params ==============================================/\

#******* prog start ********
Display = []
print('-----------------------------------------------')
import datetime
ahora = str(datetime.datetime.now())
print(ahora[:19])

labds = 250
plazos = [10*labds,5*labds,2*labds,1*labds,labds/2,labds/4,labds/12]
int_ops = ['max','10y','5y','2y','1y','6mo','3mo']
for i, pl in enumerate(plazos):
    if ndays > pl:
        n_inter = int_ops[i]
        break
else:
    n_inter = '1mo'

Gross_prices_dates = fs_M.get_dayprices_date(sto, n_inter)
##Gross_prices_dates = orly_.orly_data
if ndays > len(Gross_prices_dates[0]):
    ndays = len(Gross_prices_dates[0])
All_dates = Gross_prices_dates[0][-ndays:]
All_lis_day = Gross_prices_dates[1][-ndays:]

lis_day = All_lis_day[MAsearch_beg : MAsearch_end]

##GRes_buy = []
GRes_buy_data = []
    
for per1 in periods:
    lis_ma = fs_M.mov_average_series(lis_day, per1, len(lis_day))  #ndays) 
    histo = fs_M.histogram(lis_day, lis_ma, per1)
    
    Res_buy = []
    res_sel_buy = []
    res_sel_buy2 = []

    for i in range(len(histo[0])):
        if histo[0][i][1] > per_ref:
            percla_buy = histo[0][i-1]   #perc class buy; ex:(-0.3363, 1.92)               
            break

    #selecting bars:
    sumap = 0
    for j in range(len(histo[3])):   #Cent100 list
        if sumap <= percla_buy[1]: # and len(histo[3][j])>0:
            res_sel_buy.append(histo[3][j])
            sumap = histo[0][j][1]
        else:
            break
        
    for lis in res_sel_buy:
        for x in lis:
            res_sel_buy2.append(x)

    if len(res_sel_buy2)>0:
        entries =  fs_M.group_getfirst(sorted(res_sel_buy2))
    else:
        continue

    # Evaluation of bars founded
    # conditions: buy, for start [when values reach a ref percentage]
    # [values already in 'entries'][teo: it will bounce back]
    bought = False
    for i in entries:
        tempB = []
        tempB.append('in:')
        tempB.append(i)
        start = round(lis_ma[i]*(percla_buy[0] + 1), 2)  #Trade Start price
        if start >= lis_day[i][2] and start <= lis_day[i][1]:
            tempB.append(f"@{start}")
        else:
            start = lis_day[i][3]
            tempB.append(f"@{lis_day[i][3]}") #C value, assumed as open price(worse value, probably)
        tempB.append(f'H{chr(8593)}')
        if lis_day[i][3] > lis_day[i][0]:  #green bar
            tempB.append(lis_day[i][1])  #highest number when bought (starting)
        elif i < len(lis_day):              #red bar, takes H from next bar (can't be the last data bar)
            tempB.append(lis_day[i+1][1])
        else:
            tempB.append(start)     #if it's precisely the last bar
        tempB.append(f'L{chr(8595)}')
        tempB.append(lis_day[i][2])  #lowest number when bought (starting)                
        bought = True

        for j in range(i+1, len(lis_day)):   #waiting for close condition:
            if bought and \
               lis_day[j][1] >= lis_ma[j] and \
               lis_day[j-1][1] < lis_ma[j-1]:

                tempB.append('out:')
                tempB.append(j)
                tempB.append(f"@{lis_ma[j]}")  #21/03/24 21:58 antes: j+1    #could be different, depends on j bar
                tempB.append('  rent:')
                tempB.append(round((lis_ma[j]-start)/start, 4))
                tempB.append('  rentH:')
                tempB.append(round((tempB[4]-start)/start, 4))
                tempB.append('  ddown:')
                tempB.append(round((tempB[6]-start)/start, 4))
                tempB.append(' #ds:')
                tempB.append(tempB[8]-tempB[1])

                bought = False
                Res_buy.append(tempB)
                break

            elif bought and j == len(lis_day)-1:
                tempB.append('out: end of data')
                tempB.append(j)
                forced_close = lis_day[j][3]  #last C of data bars
                tempB.append(f"@{forced_close}")  #21/03/24 21:58 antes: j+1    #could be different, depends on j bar
                tempB.append('**rent:')
                tempB.append(0)  #operation is not closed yet
##                tempB.append(round((forced_close-start)/start, 4))
                tempB.append('**rentH:')
                tempB.append(round((tempB[4]-start)/start, 4))
                tempB.append('**ddown:')
                tempB.append(round((tempB[6]-start)/start, 4))
                tempB.append(' #ds:')
                tempB.append(tempB[8]-tempB[1])

                bought = False
                Res_buy.append(tempB)
                break                        

            else:
                if lis_day[j][1] > tempB[4]:
                    tempB[4] = lis_day[j][1]
                if lis_day[j][2] < tempB[6]:
                    tempB[6] = lis_day[j][2]
##                        print('changing H/L') #debug

                #['in:', i, Start[i], 'H:', H[i/j], 'L:', L[i/j], 'out:', j, Close[j], 'rent', rent, 'rentH', rentH, 'ddown', ddown, '#ds', #ds  ] 
                #   0    1    2        3       4     5      6       7     8    9       10      11     12      13      14     15       16    17

    
    #alternative for only 1 bought at a time (deleting buys with same bar closing):
    if Only_1_atatime:    
        Onlyone_Res_buy = [Res_buy[0]]
        for k in range(1, len(Res_buy)):
            if Res_buy[k][8] > Res_buy[k-1][8]:
                Onlyone_Res_buy.append(Res_buy[k])
        Res_buy = Onlyone_Res_buy
            
    tot_rent, tot_rentH, tot_ddown, tot_days = 0, 0, 0, 0
    for z in Res_buy:
        tot_rent += z[-7]
        tot_rentH += z[-5]
        tot_ddown += z[-3]
        tot_days += z[-1]

    if tot_days == 0:
        tot_days = 1    #semi-solution, for avoiding ZeroDivisionError
        
    #***********************
    if PrintDetails:
        if len(periods)==1:
            print('MA details')
        print(f"{sto}  (Buy); MA{per1}, P.ref(t): {per_ref}%")
        print(f"data:[{MAsearch_beg}:{MAsearch_end}] ({All_dates[MAsearch_beg]}:{All_dates[MAsearch_end]}) (#days: {len(lis_day)})")
        print(f"range, dist: {percla_buy[0]}  P.ref(r): {round(percla_buy[1],2)}%")
##                print('entries (all): ', sorted(res_sel_buy2))
        print('entries: ', entries)

        Res_buy = [[x[0],x[1],f"({All_dates[x[1]]})",x[2],x[7],x[8],x[9],x[10],x[11],x[14],x[15],x[16],x[17]] for x in Res_buy]

        #for better display:
        resume_line = ['','',f"#ops: {len(Res_buy)}",'','','','',f"{chr(8721)}rent:",round(tot_rent, 4),f"{chr(8721)}ddown:",round(tot_ddown, 4),f"{chr(8721)}#ds:",tot_days]
        Res_buy.append(resume_line)
        
        Res_buy_df = pd.DataFrame(Res_buy)
        print(Res_buy_df.to_string(index=False, header=False))
##        print(f"        {chr(8721)}rent/{chr(8721)}#ds:",round((tot_rent/tot_days),6))
##                print('Totals  #ops: ',len(Res_buy) ,'  rent: ', round(tot_rent, 4),' rentH: ', round(tot_rentH, 4),' ddown: ',round(tot_ddown, 4),'  #days(in): ',tot_days,' rent/#days: ',round((tot_rent/tot_days),6))
        
    #***********************
    if tot_rent > 0 and tot_ddown != 0:
        coef = abs(round(tot_rent / tot_ddown, 2))
    else:
        coef = 0        
##    GRes_buy.append((line1,'Totals  #ops: ',len(Res_buy) ,'  rent: ', round(tot_rent, 4),' rentH: ', round(tot_rentH, 4),' ddown: ',round(tot_ddown, 4),'  #ds(in): ',tot_days,' rent/#ds: ',round((tot_rent/tot_days),6),'r/rL:',coef))
##                    #   0          1               2            3           4                5               6                7            8                   9             10        11                 12                 13     14
    if tot_days > 0 and len(Res_buy) > 0:
        GRes_buy_data.append([sto, len(lis_day), per_ref, per1, len(Res_buy), round(tot_rent, 4), round(tot_rentH, 4), round(tot_ddown, 4),tot_days,round((tot_rent/tot_days),6),coef,round(tot_ddown/len(Res_buy), 4),round(tot_rentH/len(Res_buy), 4)])
                              #0      1           2       3       4           5                   6                   7                    8         9                           10    11                              12                                    

if MA_Display:
##            MA_min = GRes_buy_data[0][3]
    ops_min = sorted(GRes_buy_data, key = lambda x:x[4])[0][4]
    rent_min = sorted(GRes_buy_data, key = lambda x:x[5])[0][5]
    rentH_min = sorted(GRes_buy_data, key = lambda x:x[6])[0][6]
    ddown_min = sorted(GRes_buy_data, key = lambda x:x[7])[0][7]
    dsin_min = sorted(GRes_buy_data, key = lambda x:x[8])[0][8]
    rentds_min = sorted(GRes_buy_data, key = lambda x:x[9])[0][9]
    rrl_min = sorted(GRes_buy_data, key = lambda x:x[10])[0][10]
    rLops_min = sorted(GRes_buy_data, key = lambda x:x[11])[0][11]
    rHops_min = sorted(GRes_buy_data, key = lambda x:x[12])[0][12]

##            MA_max = GRes_buy_data[-1][3]
    ops_max = sorted(GRes_buy_data, key = lambda x:x[4])[-1][4]
    rent_max = sorted(GRes_buy_data, key = lambda x:x[5])[-1][5]
    rentH_max = sorted(GRes_buy_data, key = lambda x:x[6])[-1][6]
    ddown_max = sorted(GRes_buy_data, key = lambda x:x[7])[-1][7]
    dsin_max = sorted(GRes_buy_data, key = lambda x:x[8])[-1][8]
    rentds_max = sorted(GRes_buy_data, key = lambda x:x[9])[-1][9]
    rrl_max = sorted(GRes_buy_data, key = lambda x:x[10])[-1][10]
    rLops_max = sorted(GRes_buy_data, key = lambda x:x[11])[-1][11]    
    rHops_max = sorted(GRes_buy_data, key = lambda x:x[12])[-1][12]
    
    line2 = ['   ','#ds','per ','MA ','#ops','rent','ddown','#ds(in)']
    line3 = ['Min','   ','    ','   ',ops_min,rent_min,ddown_min,dsin_min]
    line4 = ['Max','   ','    ','   ',ops_max,rent_max,ddown_max,dsin_max]
    line5 = ['' for i in range(len(line2))]

    #****filters:
    GRes_buy_dataF = []
    for i in range(len(GRes_buy_data)):        
        if GRes_buy_data[i][4] > 1:
            GRes_buy_dataF.append(GRes_buy_data[i])     #les than 2 results we will consider not valid

    #reducing:
    temp_simp = []
    for x in GRes_buy_dataF:
        temp_simp.append([x[0],x[1],x[2],x[3],x[4],x[5],x[7],x[8]])
    GRes_buy_dataF = temp_simp
    
    GRes_buy_data_ord = sorted(GRes_buy_dataF, key = lambda x:x[5], reverse = True)   #sorted by rent
    GRes_buy_data_ord.insert(0, line2)
    GRes_buy_data_ord.insert(1, line3)
    GRes_buy_data_ord.insert(2, line4)
    GRes_buy_data_ord.insert(3, line5)
    GRes_buy_data_ord_df = pd.DataFrame(GRes_buy_data_ord[:MA_NumResults + 4])
    print(f"{sto}  #days: {len(lis_day)}, from MA{min(periods)} to MA{max(periods)}") 
    print(f"data:[{MAsearch_beg}:{MAsearch_end}] ({All_dates[MAsearch_beg]}:{All_dates[MAsearch_end]})") 
    print(GRes_buy_data_ord_df.to_string(index=False, header=False))
    print('------------------------------------------------')

#========================================================================\/
#Evaluation of new bars with collected parameters
if Evaluation:
    lis_day_eval = All_lis_day[Evalua_beg : Evalua_end] 
    per1 = periods[0]
    lis_ma_eval = []
    Dates_eval = All_dates[Evalua_beg:]
    ERes_buy = []
    m = -1
    bought01 = ff

    for h in range(0, len(lis_day_eval)):
        #get MA open value:
        suma_g = 0
        for g in range(Evalua_beg +h+1 -per1, Evalua_beg +h+1):   
            suma_g += All_lis_day[g][3]
        ma_open = round(suma_g/per1, 2)
        lis_ma_eval.append(ma_open)        
        #to only 1 at a time:
        if bought01 == ff and h <= m:
            continue
                    
        #calc distance:
        if lis_day_eval[h][2] <= ma_open*(1 + percla_buy[0]):
            start_now = round(ma_open*(1 + percla_buy[0]), 2)
            tempB_now = ['in:']
            tempB_now.append(h)
            
            if start_now >= lis_day_eval[h][2] and start_now <= lis_day_eval[h][1]:
                tempB_now.append(f"@{start_now}")
            else:
                start_now = lis_day_eval[h][3]
                tempB_now.append(f"@{lis_day_eval[h][3]}") #C value, assumed as open price(worse value, probably)
            tempB_now.append(f'H{chr(8593)}')
            if lis_day_eval[h][3] > lis_day_eval[h][0]:  #green bar
                tempB_now.append(lis_day_eval[h][1])  #highest number when bought (starting)
            elif h < len(lis_day_eval):              #red bar, takes H from next bar (can't be the last data bar)
                tempB_now.append(lis_day_eval[h+1][1])
            else:
                tempB_now.append(start)     #if it's precisely the last bar
            tempB_now.append(f'L{chr(8595)}')
            tempB_now.append(lis_day_eval[h][2])  #lowest number when bought (starting)                
            bought01 = True    
                
            for m in range(h+1, len(lis_day_eval)):   #waiting for close condition:
                #get MA close value:
                suma_c = 0
                for g in range(Evalua_beg +m+1 -per1, Evalua_beg +m+1):   
                    suma_c += All_lis_day[g][3]
                ma_clos = round(suma_c/per1, 2)
                
                if bought01 and lis_day_eval[m][1] >= ma_clos and \
                   lis_day_eval[m-1][1] < lis_day_eval[m][1]:

                    tempB_now.append('out:')
                    tempB_now.append(m)
                    tempB_now.append(f"@{ma_clos}")  #21/03/24 21:58 antes: m+1    #could be different, depends on m bar
                    tempB_now.append('  rent:')
                    tempB_now.append(round((ma_clos-start_now)/start_now, 4))
                    tempB_now.append('  rentH:')
                    tempB_now.append(round((tempB_now[4]-start_now)/start_now, 4))
                    tempB_now.append('  ddown:')
                    tempB_now.append(round((tempB_now[6]-start_now)/start_now, 4))
                    tempB_now.append(' #ds:')
                    tempB_now.append(tempB_now[8]-tempB_now[1])

                    bought01 = False
                    ERes_buy.append(tempB_now)
                    break    

                elif bought01 and m == len(lis_day_eval)-1:
                    tempB_now.append('out: end of data')
                    tempB_now.append(m)
                    forced_close = lis_day_eval[m][3]  #last C of data bars
                    tempB_now.append(f"@{forced_close}")  #21/03/24 21:58 antes: m+1    #could be different, depends on m bar
                    tempB_now.append('**rent:')
                    tempB_now.append(0)  #operation is not closed yet
##                    tempB_now.append(round((forced_close-start_now)/start_now, 4))
                    tempB_now.append('**rentH:')
                    tempB_now.append(round((tempB_now[4]-start_now)/start_now, 4))
                    tempB_now.append('**ddown:')
                    tempB_now.append(round((tempB_now[6]-start_now)/start_now, 4))
                    tempB_now.append(' #ds:')
                    tempB_now.append(tempB_now[8]-tempB_now[1])

                    bought01 = False
                    ERes_buy.append(tempB_now)
                    break
                
                else:
                    if lis_day_eval[m][1] > tempB_now[4]:
                        tempB_now[4] = lis_day_eval[m][1]
                    if lis_day_eval[m][2] < tempB_now[6]:
                        tempB_now[6] = lis_day_eval[m][2]

    if len(ERes_buy) > 0:
        tot_rent, tot_rentH, tot_ddown, tot_days = 0, 0, 0, 0
        for z in ERes_buy:
            tot_rent += z[-7]
            tot_rentH += z[-5]
            tot_ddown += z[-3]
            tot_days += z[-1]

        if tot_days == 0:
            tot_days = 1    #semi-solution, for avoiding ZeroDivisionError
        
        print('')
        print('Evaluation')
        print(f"{sto}  (Buy); MA{per1}, P.ref(t): {per_ref}%")
        print(f"data:[{Evalua_beg}:{Evalua_end}] ({All_dates[Evalua_beg]}:{All_dates[Evalua_end-1]}) (#days: {len(lis_day_eval)})")
        print(f"range, dist: {percla_buy[0]}  P.ref(r): {round(percla_buy[1],2)}%")

        ERes_buy = [[x[0],x[1],f"({Dates_eval[x[1]]})",x[2],x[7],x[8],x[9],x[10],x[11],x[14],x[15],x[16],x[17]] for x in ERes_buy]

        #for better display:
        resume_line = ['','',f"#ops: {len(ERes_buy)}",'','','','',f"{chr(8721)}rent:",round(tot_rent, 4),f"{chr(8721)}ddown:",round(tot_ddown, 4),f"{chr(8721)}#ds:",tot_days]
        ERes_buy.append(resume_line)
        
        ERes_buy_df = pd.DataFrame(ERes_buy)
        print(ERes_buy_df.to_string(index=False, header=False))

    else:
        print('')
        print('Evaluation: No data. End')

#========================================================================/\
#------------------------------------------------------------\/
if Evaluation and Chart:
    import mplfinance as mpf
    import numpy as np
    num = len(lis_day_eval)
    #OHLC data:
    dates = pd.to_datetime(All_dates[Evalua_beg : Evalua_end])
    data_ch = pd.DataFrame({"Open": np.array([x[0] for x in lis_day_eval]),
        "High": np.array([x[1] for x in lis_day_eval]),
        "Low": np.array([x[2] for x in lis_day_eval]),
        "Close": np.array([x[3] for x in lis_day_eval])}, index=dates)       

    #entry points (NaN everywhere except entries):
    entry_long = [np.nan] * num
    entries = [x[1] for x in ERes_buy[:-1]]
    for ent in entries:
        entry_long[ent] = data_ch["Low"].iloc[ent] * 1#0.97

    close_long = [np.nan] * num
    closings = [x[5] for x in ERes_buy[:-1]]
    for clo in closings:
        close_long[clo] = data_ch["High"].iloc[clo] * 1#1.03

    lis_ma_ch = data_ch["Close"].rolling(per1).mean()

    #add plots
    apds = [mpf.make_addplot(lis_ma_ch,panel=0,color="blue",width=0.5,label=f"MA {per1}"),
            mpf.make_addplot(entry_long,type="scatter",marker="^",
                             markersize=20,color="blue",label='buy open'),
            mpf.make_addplot(close_long,type="scatter",marker="v",
                             markersize=20,color="orange",label='buy close')]

    mpf.plot(data_ch,type="candle",style="yahoo",volume=False,addplot=apds,title=f"{sto}, Mean Reversion backtest",warn_too_much_data=3000)


#------------------------------------------------------------/\
