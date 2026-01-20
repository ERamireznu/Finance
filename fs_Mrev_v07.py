import yfinance as yf
import math
def get_dayprices_date(stock_, num_inter):
    lisday0 = [] 
    des = 2
    # get ticker date & price data:
    try:
        data = yf.download(stock_, period = num_inter, interval='1d')
        dates = data.index
        date_list = dates.tolist()
        dates_exit = [str(x)[:10] for x in date_list]        
        for b in range(0, len(data)):
            valO = round(data.iloc[b][3], des)
            valH = round(data.iloc[b][1], des)
            valL = round(data.iloc[b][2], des)
            valC = round(data.iloc[b][0], des)
            lisday0.append((valO, valH, valL, valC))
    except:
        print("no data available")
    return(dates_exit, lisday0) #([list with dates (str)], [list with OHLC data])

def mov_average_series(lisday, per_ma, ndays_):
    lis_ma = []
    for b in range(0, ndays_):  # create MA(x)
        if b < (per_ma-1):     # fills the first cells with 0s (matching same counter)
            lis_ma.append(0)            
        else:   #(b >= per_ma)
            sumac = 0
            for c in range(b - (per_ma-1), b+1):  #02/01/26: adjusts made for matching counters (MA values include current bar values; ex: MA108[0]=lis_day[0]+...[107]) 
                sumac += lisday[c][3]
            lis_ma.append(round(sumac/per_ma, 2))
    return lis_ma

def group_getfirst(comp):  #try to not repeat bars when they are neighbors (trade would be with 1st bar)
    comp2 = [comp[0]]   #sets the first coincidence
    for i in range(1,len(comp)):
        if comp[i]-comp[i-1] > 3:  #(3) considered as a neighborhood (same trade)
            comp2.append(comp[i])
    return comp2

def histogram(lisday, lisma, per00):   #(lis_day OHLC, list MA)
    lis_dist = []
    full_histo_dat = []
    full_histo = []
    Cent100 = [[] for x in range(100)]
    Cent100_acum = [[] for x in range(100)]

    for i in range(per00):
        lis_dist.append((0,0)) # fills the first cells with 0s (matching same counter)

    for i in range(per00, len(lisday)-1):
        if lisday[i][1] >= lisma[i+1]:    #changed to lisma[i+1] from lisma[i](index didn't match previously)
            dist = round((lisday[i][1] - lisma[i+1]) / lisma[i+1], 4)
        else:
            dist = round((lisday[i][2] - lisma[i+1]) / lisma[i+1], 4)
        lis_dist.append((i, dist))

    distances = [x[1] for x in lis_dist]    

    rmin = round(min(distances) - 0.005, 2)
    rmax = round(max(distances) + 0.005, 2)
    anc = round((rmax - rmin)/100, 4)

    #classify list elements in "cents" (partials)----
    for i, x  in lis_dist:
        y0 = math.trunc((x - rmin)/anc - 1)    #percentile where 'x' belongs to
        Cent100[y0].append(i)

    #classify list elements in "cents" (accrued)----
    for i, x  in lis_dist:
        for j in range(1, 101):
            if x < (rmin + j*anc):
                Cent100_acum[j-1].append(i)

    # make histogram (end)
    for j in range(1, 101):
        cen_dat = (round(rmin + j*anc, 4), round((len(Cent100_acum[j-1])/len(lis_dist))*100,2))
        full_histo_dat.append(cen_dat)
        cen_str = '<'+str(round(rmin + j*anc, 4))+': '+str(round((len(Cent100_acum[j-1])/len(lis_dist))*100,2))+'%'
        full_histo.append(cen_str)

    return(full_histo_dat, full_histo, lis_dist, Cent100, Cent100_acum)
    #     (histo_data    ;histo_string; i, dist; parciales; acumulados)
