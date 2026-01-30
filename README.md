INTRO
This project is about the search of a proper Simple Moving Average (MA from here) to use for a Mean Reversion strategy.
Traditionally, there is the use of some MAs for this purpose (50 days, 100 days, 200 days,...). But considering every stock show its own
behaviour in the market, we will search for another numbers here.

HOW IT WORKS
Given the data series, it is calculated the MA for every period within the range entered by the user (as "Periods __ to __").
Then, for every MA value is calculated the "distance" with its correspondent candlestick. Having all these distances ordered in an
histogram, the user specifies a percentage ("Reference %") for selecting the distances that are into that category (Ex.:
Reference % = 2% --> all distances that are in the most extreme 2% away from the MA).
Every distance represents an option to open a buy (see Note 1), so we consider it as a bought position until its next cross 
of the price with the MA (see Note 2). 
Then calculate this for every MA, add their positions profit/losses, and order the MAs according to results.


QUICK GUIDE
- The file of the main script is "backtest_MeanrevMA_v01.py"
- It works with some functions written in "fs_Mrev_v07.py"
- ("backtest_MeanrevMA" was the original, it's obsolete now.)
- Libraries: yfinance (for downloading data), tkinter, pandas and math.
- Starting with the launch of the main script, this is the display:
- <img width="505" height="795" alt="image" src="https://github.com/user-attachments/assets/49dc949c-7c22-4f60-8973-d33790265077" />
- 1st section (Get data):
  Symbol: stock, ETF, some forex pairs,... (always using yahoo finance style)
  Data: enter number of days you will work with (recommended), considering it will be the last {number} days;
        alternatively, you can enter 2 dates for getting the data (format: dd-mm-yyyy)
  Submit: download the data required from yfinance, and enables 2nd section.
- 2nd section (MA search)
  Reference %: 
