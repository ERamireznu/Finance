#v01: #29/01/26
import pandas as pd
import yfinance as yf
import math
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import fs_Mrev_v07 as fs_M
import tkinter as tk
from tkinter import *
from tkinter import ttk
tt, ff = True, False

#******* prog start ********
Display = []
print('-----------------------------------------------')
import datetime
ahora = str(datetime.datetime.now())
print(ahora[:19])

def get_data():    
    global sto, ndays, All_dates, All_lis_day
    
    sto = (ent00.get()).upper()
    var_data = v_dat.get()
    if var_data == 1:
        ndays = int(ent01.get())
        
        labds = 250
        plazos = [10*labds,5*labds,2*labds,1*labds,labds/2,labds/4,labds/12]
        int_ops = ['max','10y','5y','2y','1y','6mo','3mo']
        for i, pl in enumerate(plazos):
            if ndays > pl:
                n_inter = int_ops[i]
                break
        else:
            n_inter = '1mo'
        
    elif var_data == 2:
        t0 = ent02a.get()   #format(01-12-1000)
        tf = ent02b.get()

        date_0 = f"{t0[6:]}-{t0[3:5]}-{t0[:2]}"   #format(1000-12-01)
        date_f = f"{tf[6:]}-{tf[3:5]}-{tf[:2]}"   
    
    try:
        if var_data == 1:
            Gross_prices_dates = fs_M.get_dayprices_date(sto, n_inter)
            if ndays > len(Gross_prices_dates[0]):
                ndays = len(Gross_prices_dates[0])
            
        elif var_data == 2:
            Gross_prices_dates = fs_M.get_dayprices_2dates(sto, date_0, date_f)
            ndays = len(Gross_prices_dates[0])  #redundant, only for simplicity
        
        All_dates = Gross_prices_dates[0][-ndays:]
        All_lis_day = Gross_prices_dates[1][-ndays:]
        print(f"{sto} data ready (#days: {ndays})")

        #assigning var:
        win01_lab02a.config(text=f"Max. value: {ndays-1}",fg='grey')

        #enabling:
        for w in widgs01:
            w.config(state="normal")

    except:
        print(f"No data for {sto}")
#******************************************

def ma_search_calc():
    global per_ref, dic_perclasb, MAsearch_end, MA_top
    dic_perclasb = {}
    per_ref = float(win01_ent00.get())
    MAsearch_beg = int(win01_ent01.get())
    MAsearch_end = int(win01_ent02.get())
    p_beg = int(win01_ent03.get())
    p_end = int(win01_ent04.get())
    MA_NumResults = int(win01_ent05.get())        

    Only_1_atatime = tt
    PrintDetails = ff
    
    lis_day = All_lis_day[MAsearch_beg : MAsearch_end]
    periods = [x for x in range(p_beg, p_end+1, 1)]
    
    GRes_buy_data = []
        
    for per1 in periods:
        lis_ma = fs_M.mov_average_series(lis_day, per1, len(lis_day))  #ndays) 
        histo = fs_M.histogram(lis_day, lis_ma, per1)
        
        Res_buy = []
        res_sel_buy = []
        res_sel_buy2 = []

        global percla_buy
        for i in range(len(histo[0])):
            if histo[0][i][1] > per_ref:
                percla_buy = histo[0][i-1]   #perc class buy; ex:(-0.3363, 1.92)               
                break

        dic_perclasb[per1] = percla_buy

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

    #MA display:    
    line2 = ['   ','#ds','per ','MA ','#ops','rent','ddown','#ds(in)']

    #****filters:
    GRes_buy_dataF = []
    for i in range(len(GRes_buy_data)):        
        if GRes_buy_data[i][4] > 1:
            GRes_buy_dataF.append(GRes_buy_data[i])

    #reducing:
    temp_simp = []
    for x in GRes_buy_dataF:
        temp_simp.append([x[0],x[1],x[2],x[3],x[4],x[5],x[7],x[8]])
    GRes_buy_dataF = temp_simp
    print('')
    print('MA search')
    print(f"{sto}  #days: {len(lis_day)}, from MA{min(periods)} to MA{max(periods)}") 
    print(f"data:[{MAsearch_beg}:{MAsearch_end}] ({All_dates[MAsearch_beg]}:{All_dates[MAsearch_end]})") 
    print('')
    if len(GRes_buy_dataF)>0:
        GRes_buy_data_ord = sorted(GRes_buy_dataF, key = lambda x:x[5], reverse = True)   #sorted by rent
        GRes_buy_data_ord.insert(0, line2)
        
        GRes_buy_data_ord_df = pd.DataFrame(GRes_buy_data_ord[:MA_NumResults + 1])
        print(GRes_buy_data_ord_df.to_string(index=False, header=False))
        but02_ena = True
        MA_top = GRes_buy_data_ord[1][3]

    else:
        print('No MAs found (with > 1 operation) for this data')
    print('------------------------------------------------')

    #assigning vars:
    var_evalbeg = tk.IntVar(value = MAsearch_end)
    win02_ent01.config(textvariable = var_evalbeg)
    var_evalend = tk.IntVar(value = ndays)    
    win02_ent02.config(textvariable = var_evalend)
    var_period = tk.IntVar(value = MA_top)  
    win02_ent03.config(textvariable = var_period)
    win03_ent00.config(textvariable = var_period)  #for show now
    
    #enabling:
    for w in widgs02:
        w.config(state="normal")
    for w in widgs03:
        w.config(state="normal")
#*****end of def ma_search_calc()

#========================================================================\/
#Evaluation of new bars with collected parameters

def evaluation_calc():
    Evalua_beg = int(win02_ent01.get())
    Evalua_end = int(win02_ent02.get())
    perE = int(win02_ent03.get()) #ideally the period found in the previous stage (now by default)
    Chart = var_ch.get()

    percla_buy = dic_perclasb[perE]

    lis_day_eval = All_lis_day[Evalua_beg : Evalua_end] 
    lis_ma_eval = []    #not using now
    Dates_eval = All_dates[Evalua_beg:]
    ERes_buy = []
    m = -1
    bought01 = ff

    for h in range(0, len(lis_day_eval)):
        #assure there are data for ma calc:
        if (Evalua_beg +h+1 -perE) < 1:
            continue
        #get MA open value:
        suma_g = 0
        for g in range(Evalua_beg +h+1 -perE, Evalua_beg +h+1):   
            suma_g += All_lis_day[g][3]
        ma_open = round(suma_g/perE, 2)
        lis_ma_eval.append(ma_open)    #not using now        
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
                for g in range(Evalua_beg +m+1 -perE, Evalua_beg +m+1):   
                    suma_c += All_lis_day[g][3]
                ma_clos = round(suma_c/perE, 2)
                
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
        print(f"{sto}  (Buy); MA{perE}, P.ref(t): {per_ref}%")
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
        print('Evaluation: No results.')

    #========================================================================/\
    #------------------------------------------------------------\/
    if Chart:
        if len(ERes_buy) > 0:
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

            lis_ma_ch = data_ch["Close"].rolling(perE).mean()

            #add plots
            apds = [mpf.make_addplot(lis_ma_ch,panel=0,color="blue",width=0.5,label=f"MA {perE}"),
                    mpf.make_addplot(entry_long,type="scatter",marker="^",
                                     markersize=20,color="blue",label='buy open'),
                    mpf.make_addplot(close_long,type="scatter",marker="v",
                                     markersize=20,color="orange",label='buy close')]

            mpf.plot(data_ch,type="candle",style="yahoo",volume=False,addplot=apds,title=f"{sto}, Mean Reversion backtest",warn_too_much_data=3000)
        else:
            print('No results for chart.')
    #------------------------------------------------------------/\
#*****end of def evaluation_calc()
def show_now():
    per_now = int(win03_ent00.get()) #default: MA_top (by default in Evaluation too)
    percla_buy_now = dic_perclasb[per_now]

    hoy = str(datetime.datetime.now())[:10]
    ma_now, dis_now = 0, 0
    if hoy == All_dates[-1]:        
        #MA with per_now (last value):
        ma_now = (fs_M.mov_average_series(All_lis_day[-per_now:], per_now, len(All_lis_day[-per_now:])))[-1]
        #dist:
        dis_now = round(((All_lis_day[-1][3] - ma_now)/ma_now)*100, 2)
    else:
        last_val = (fs_M.get_dayprices_date(sto, '1d'))
        if last_val[0][0] == All_dates[-1]:
            #MA with per_now (last value), not a labour day:
            ma_now = (fs_M.mov_average_series(All_lis_day[-per_now:], per_now, len(All_lis_day[-per_now:])))[-1]
            #dist:
            dis_now = round(((All_lis_day[-1][3] - ma_now)/ma_now)*100, 2)            

    if ma_now == 0 and dis_now == 0:
        print('No last data available')
    else:
        print('')
        print('Now:')
        print(f"{sto} Buy parameters; MA{per_now}, P.ref(t): {per_ref}%")
        print(f"distance to reach: {round(percla_buy_now[0]*100,2)}%")
        print(f"distance now     : {dis_now}%")
        
        adva = round((dis_now/(percla_buy_now[0]*100))*200)  #rel. to can0 width
        can0.configure(bg='white')
        can0.create_line(0, 5, adva , 5, fill='red', width=3)
        win03_lab03.configure(text=f"{round(percla_buy_now[0]*100,2)}% (dist. to reach)")
        if adva >= 200:
            win03_lab04.place(x=350, y=710)
            print('Buy now!')
            win03_lab05.configure(text=f"BUY now!")
        elif adva > 0:
            win03_lab04.place(x=140+adva, y=710)
        else:
            win03_lab04.place(x=140, y=710)
        win03_lab04.configure(text=f"{dis_now}% (dist. now)")
    
#gui:
root = tk.Tk()
root.title("MA search/backtest")
root.geometry("500x760")

lab_title = tk.Label(root, text="MA searching and backtest (interval: Days)", font=("Arial", 8, "bold"))
lab00a = tk.Label(root, text="Get data", font=("Arial", 8, "bold")) 
lab00 = tk.Label(root, text="Symbol")
ent00 = tk.Entry(root, width=10)
#-----------------\/
v_dat = IntVar(value=1) 
rb01 = Radiobutton(root, text="Data: number of bars", variable = v_dat, value=1) #radio0102
ent01 = tk.Entry(root, width=10)
lab00b = tk.Label(root, text="(number) last values",fg='grey')
rb02 = Radiobutton(root, text="Data: from date to date", variable = v_dat, value=2) #radio0102
ent02a = tk.Entry(root, width=10) 
lab01 = tk.Label(root, text="to") 
ent02b = tk.Entry(root, width=10) 
lab01a = tk.Label(root, text="format: (dd-mm-yyyy)",fg='grey')
#-----------------/\
but00 = tk.Button(root, text="Submit", command=get_data)
#----------------------------------\/
sep00 = ttk.Separator(root, orient='horizontal')

color01= 'gray95'

win01_lab0a = tk.Label(root, text="MA search", font=("Arial", 8, "bold"), bg=color01)
win01_lab00 = tk.Label(root, text="Reference %", bg=color01)
win01_ent00 = tk.Entry(root, width=5)
win01_lab01 = tk.Label(root, text="Begin", bg=color01)
win01_ent01 = tk.Entry(root, width=10)    
win01_lab02 = tk.Label(root, text="End", bg=color01)
win01_ent02 = tk.Entry(root, width=10)
win01_lab02a = tk.Label(root, bg=color01) #++++++++++++++

win01_lab03 = tk.Label(root, text="Periods", bg=color01)
win01_ent03 = tk.Entry(root, width=5)
win01_lab04 = tk.Label(root, text="to", bg=color01)
win01_ent04 = tk.Entry(root, width=5)

win01_lab05 = tk.Label(root, text="Number of results", bg=color01)
win01_ent05 = tk.Entry(root, width=10)

win01_but00 = tk.Button(root, text="Search", bg=color01, command=ma_search_calc)   #ma_search_calc()

#----------------------------------/\
sep01 = ttk.Separator(root, orient='horizontal')
#----------------------------------\/
color02 = color01

win02_lab00 = tk.Label(root, text="Evaluation", font=("Arial", 8, "bold"), bg=color02)    

win02_lab01 = tk.Label(root, text="Begin", bg=color02)
win02_ent01 = tk.Entry(root, width=10) #a var will be assigned after
win02_lab01a = tk.Label(root, text="Def. value: after where MA search ends",fg='grey',bg=color02)

win02_lab02 = tk.Label(root, text="End", bg=color02)    
win02_ent02 = tk.Entry(root, width=10) #a var will be assigned after
win02_lab02a = tk.Label(root, text="Def. value: end of data bars",fg='grey',bg=color02)

win02_lab03 = tk.Label(root, text="Period", bg=color02)  
win02_ent03 = tk.Entry(root, width=10) #a var will be assigned after
win02_lab03a = tk.Label(root, text="Def. value: possible best MA (check values)",fg='grey',bg=color02)

win02_lab04 = tk.Label(root, text="Chart", bg=color02)
var_ch = tk.BooleanVar(value=False)  # starts unchecked
win02_chb04 = tk.Checkbutton(root, variable=var_ch, bg=color02)

win02_but00 = tk.Button(root, text="Evaluate", bg=color02, command=evaluation_calc)   #evaluation_calc()

#----------------------------------/\
sep02 = ttk.Separator(root, orient='horizontal')
#----------------------------------\/
win03_lab00 = tk.Label(root, text="Now", font=("Arial", 8, "bold"))
win03_lab01 = tk.Label(root, text="Period")  
win03_ent00 = tk.Entry(root, width=10) #a var will be assigned after
win03_lab02 = tk.Label(root, text="Def. value: MA used in Evaluation",fg='grey')
win03_but00 = tk.Button(root, text="Show", command=(show_now))

can0 = Canvas(root, width=200, height=8)
win03_lab03 = tk.Label(root, text="", font=("Arial", 7))
win03_lab04 = tk.Label(root, text="", font=("Arial", 7))
win03_lab05 = tk.Label(root, text="", font=("Arial", 7))

#----------------------------------/\
#disabling:
widgs01 = [win01_lab0a,win01_lab00,win01_ent00,win01_lab01,win01_ent01,win01_lab02,win01_ent02,
win01_lab02a,win01_lab03,win01_ent03,win01_lab04,win01_ent04,win01_lab05,win01_ent05,win01_but00]
for w in widgs01:
    w.config(state="disabled")
    
widgs02 = [win02_lab00,win02_lab01,win02_ent01,win02_lab01a,win02_lab02,win02_ent02,win02_lab02a,
win02_lab03,win02_ent03,win02_lab03a,win02_lab04,win02_chb04,win02_but00]
for w in widgs02:
    w.config(state="disabled")

widgs03 = [win03_lab00,win03_lab01,win03_ent00,win03_lab02,win03_but00,can0,win03_lab03,win03_lab04,
           win03_lab05]
for w in widgs03:
    w.config(state="disabled")

#geometry:
lab_title.place(x=10, y=10)
lab00a.place(x=10, y=40)
lab00.place(x=10, y=70)
ent00.place(x=70, y=70)

rb01.place(x=10, y=100)
ent01.place(x=170, y=100)
lab00b.place(x=240, y=100)
rb02.place(x=10, y=125)
ent02a.place(x=170, y=125)
lab01.place(x=240, y=125)
ent02b.place(x=260, y=125)
lab01a.place(x=330, y=125)

but00.place(x=10, y=160)
#=========
sep00.place(x=0, y=205, relwidth=1, relheight=1)
#=========
win01_lab0a.place(x=10, y=210)
win01_lab00.place(x=10, y=240) 
win01_ent00.place(x=90, y=240) 
win01_lab01.place(x=10, y=270) 
win01_ent01.place(x=60, y=270) 
win01_lab02.place(x=10, y=300) 
win01_ent02.place(x=60, y=300)
win01_lab02a.place(x=130, y=300)

win01_lab03.place(x=10, y=330) 
win01_ent03.place(x=70, y=330) 
win01_lab04.place(x=110, y=330) 
win01_ent04.place(x=130, y=330)

win01_lab05.place(x=10, y=360) 
win01_ent05.place(x=130, y=360)
win01_but00.place(x=10, y=390)
#=========
sep01.place(x=0, y=435, relwidth=1, relheight=1)
#=========
win02_lab00.place(x=10, y=440) 

win02_lab01.place(x=10, y=470) 
win02_ent01.place(x=60, y=470)
win02_lab01a.place(x=140, y=470)
win02_lab02.place(x=10, y=500) 
win02_ent02.place(x=60, y=500)
win02_lab02a.place(x=140, y=500)

win02_lab03.place(x=10, y=530) 
win02_ent03.place(x=60, y=530)
win02_lab03a.place(x=140, y=530)

win02_lab04.place(x=10, y=560) 
win02_chb04.place(x=55, y=560)

win02_but00.place(x=10, y=590)
#=========
sep02.place(x=0, y=635, relwidth=1, relheight=1)
#=========
win03_lab00.place(x=10, y=640)
win03_lab01.place(x=10, y=670) 
win03_ent00.place(x=60, y=670)
win03_lab02.place(x=140, y=670)

win03_but00.place(x=10, y=700)

can0.place(x=140, y=700)
win03_lab03.place(x=350, y=698)
win03_lab04.place(x=140, y=710)
win03_lab05.place(x=140, y=722)
#=========
root.mainloop()

