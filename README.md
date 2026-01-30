INTRO
This project is about the search of a proper Simple Moving Average (MA from here) to use for a Mean Reversion strategy.
Traditionally, there is the use of some MAs for this purpose (50 days, 100 days, 200 days,...). But considering every stock has its own
behaviour in the market, we will search for another numbers here. The project is made thinking in equities that show an uptrend
in the long term, looking for good buy entries on them.

HOW IT WORKS
Given the data series, it is calculated the MA for every period within the range entered by the user (as "Periods __ to __").
Then, for every MA value is calculated the "distance" with its correspondent candlestick. Having all these distances ordered in an
histogram, the user specifies a percentage ("Reference %") for selecting the distances that are into that category (Ex.:
Reference % = 2% --> all distances that are in the most extreme 2% away from the MA).
Every distance represents an option to open a buy (see Note 1), so we consider it as a bought position until its next cross 
of the price with the MA (see Note 2). 
Then calculate this for every MA, add their positions profit/losses, and order the MAs according to results.
Finally, usually take the first MA or another in the list, if the first one seems to be an exception (see Note 3). And with this MA 
selected, do an evaluation of it on the rest of data available.
Aditionally, if the data obtained includes the last values, in section "Now" you can check how the current price is related to the MA.

QUICK GUIDE (with example)
- The file of the main script is "backtest_MeanrevMA_v01.py" ("backtest_MeanrevMA" was the original, it's obsolete now).
- It works with some functions written in "fs_Mrev_v07.py"
- Libraries: yfinance (for downloading data), tkinter, pandas and math. For chart (optional): numpy, mplfinance.
- Starting with the launch of the main script, this is the display:
- <img width="505" height="795" alt="image" src="https://github.com/user-attachments/assets/49dc949c-7c22-4f60-8973-d33790265077" />
- 1st section (Get data):
  Symbol: stock, ETF, some forex pairs,... (always using yahoo finance style)
  Data: enter number of days you will work with (recommended), considering it will be the last {number} days;
        alternatively, you can enter 2 dates for getting the data (format: dd-mm-yyyy)
  Submit: it downloads the data required from yfinance, and enables 2nd section.
  {Example --> Symbol= AXP; Data: number of bars= 1400 (that is 1400 last values)}
- 2nd section (MA search)
  {Example --> Reference % = 2.0 (to open buy positions consider, from all distances MA-value, those distances that are in 2.0% of the longest)}
  {Example --> Begin = 0; End = 400; Periods = 30 to 150 (begin/end of MA search, periods for calculating the MAs)}
  {Example --> Number of results = 10 (for display in console; in this case there could be 121 results, but we will not consider as a result if a     MA returns less than 2 operations).
  <img width="497" height="227" alt="image" src="https://github.com/user-attachments/assets/ba742cce-24bc-4fb4-bf06-ebc05c482747" />
  <img width="375" height="256" alt="image" src="https://github.com/user-attachments/assets/0e40f150-ee48-490c-b7af-76432e201a76" />
- 3rd section (Evaluation)  
  {Example --> Begin = 400; End = 1400; Period = 77 (begin/end for evaluation with MA of "best" period as a default value)}
  <img width="504" height="189" alt="image" src="https://github.com/user-attachments/assets/b776338a-14f4-4ffd-a962-266b834e654c" />
  <img width="723" height="250" alt="image" src="https://github.com/user-attachments/assets/3fa41aa3-0246-4dc6-bb0f-00eb5b83adfa" />
  Aditionally there is a chart to show the positions evaluated, if requested.
 - 4th section (Now)
   {Example --> Period = 77  (what woul be now with the selected MA, as a default?)
   <img width="466" height="208" alt="image" src="https://github.com/user-attachments/assets/3b3024c0-9333-42ae-9238-ae0621ce1a0f" />

*Note 1: when the price falls far from the MA, there will be several "good distances" to open a position; but, to be more realistic, we
consider just one position open at a time.
*Note 2: this is a typical condition for closing ("reversion to the media"); we are not considering here neither TP (take profit) nor SL 
(stop loss).
*Note 3: sometimes the MAs ordered by best results show something like (in order): 137, 78, 79, 76,...; in this cases "the best" seems to be 
an exception and it could be not as good as the others, which seem to belong to a "family" of good MAs.
  
DISCLAIMER
As always, this project does not represent financial advice. 
Feel free to use it (and criticize it), but do your own research and make your own decisions before investing.


