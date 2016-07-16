# BacktestFrame
A Backtest Framework in Python

#### Framework Structure

|--frame_main.py	-- main function  
|--frame_block.py	-- backtest process and output process  
|--frame_module.py	-- strategy functions and low level modules  
|--output		-- backtest results saved in this folder  
&emsp;&emsp;|--pics  		-- value curve saved in this folder  
&emsp;&emsp;|--returns		-- daily returns data saved in this folder

#### Requirements
numpy  
pandas  
matplotlib  

#### Input Data
The data modules connecting to databases have not done yet.  
Current test data is compressed in MajorContract.zip.

#### Usage
Use function test in frame_main.py to conduct single target backtest.
Use script Strategy_test.py to conduct multi targets backtest.

note: Correlation.py is integrated into Strategy_test.py