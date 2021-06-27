# Analysis of MorningStar financial statements based on the book "65 Steps From Zero To Pro".

 ##  Algorithm from the book: "65 Steps From Zero To Pro" | Barshevsky Grigory

 ###   Data: MorningStar(Premium accaunt.) -
 ###   Income Statement_Annual_As Originally Reported(xls files),
 ###   Balance Sheet_Annual_As Originally Reported(xls files),
 ###   Dividents data(xls files).
 
    

## Pre-installation
You need to install:
* MongoDB.
* Create database: morningstar.
* Create collections:
   - Balance
   - Dividents
   - Income
   - grow_data
   - score
   - temp_express_analiz
 
 Using example:
 Input: financial statements from morningstar (examples in directory in)
 Start balance_income_dividents_to_mongoDB.py. 
 Start analiz_mongoDB.py. 
 Output: score collection, log in log dir
