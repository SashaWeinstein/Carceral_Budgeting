"""This file is to hold hard-coded numbers of total costs at the state an municipal level """
import pandas as pd

"""Statewide
Numbers from budget summary historical spending at mass.gov"""
#2016 is from https://budget.digital.mass.gov/summary/fy20/enacted?tab=historical-spending
#2017-2019 from https://budget.digital.mass.gov/summary/fy21/enacted?tab=historical-spending
MA_expend_dict = {2016: 38402539928, 2017: 39095346106, 2018: 40463158944, 2019: 42240687227}
MA_expend = pd.Series(MA_expend_dict)

"""Boston
Numbers from citywide summary budget"""
#https://www.boston.gov/sites/default/files/embed/file/2019-04/v1_02-_19_a_summary-budget.pdf
#2018, 2019 data from https://www.boston.gov/sites/default/files/file/2020/10/2-Volume%201%20-%20Operating%20Budget.pdf
Boston_citywide_expend_dict = {2016: 2881.09*10**6, 2017: 2990.13*10**6, 2018: 3192.10*10**6, 2019: 3348.53*10**6}
Boston_citywide_expend = pd.Series(Boston_citywide_expend_dict)


"""Revere
All numbers from citywide budget
For 2016, numbers are from table titled "Mayor's Recommended Budget Overview Detail Expenses"
for 2017, numbers are from page title "Total of all Expenses by Department"
for 2018, 2019 Numbers are from Five Year Financial Forecast page of citywide page
Note that in 2018-2019 expenditures figure is used, whereas in 2017 budget figure is used. Best information available is 
used in each case, but it makes comparing year to year changes in fraction of municipal budget   
"""
Revere_citywide_expend_dict = {}
Revere_citywide_expend_dict[2016] = 178362473 #from FY 2017 Documnet page I-22. Line-item Total All Expenses, column "Recap Estimated FY 2016"
Revere_citywide_expend_dict[2017] = 183839348 #from FY 2018 document page 21. line-item Total fiscal year budget, "Previous appropriation 2017" column
Revere_citywide_expend_dict[2018] = 204066527 #from FY 2019 document page I-28 FY 18 Recap
Revere_citywide_expend_dict[2019] = 211535287 #from FY 2020 document page I-26 FY 19 recap

Revere_citywide_expend = pd.Series(Revere_citywide_expend_dict)

"""Chelsea
All numbers from citywide budget document
2016-2019 from "General Fund Budget" Line-item on page 1 of FY 20 budget document 
Note that FY21 budget has a "Total" line-item on page 58, but number listed there are much lower than Chelsea PD total
budget listed in FY20 budget
"""

Chelsea_citywide_expend_dict = {}
Chelsea_citywide_expend_dict[2016] = 149035333
Chelsea_citywide_expend_dict[2017] = 155212550
Chelsea_citywide_expend_dict[2018] = 163390146
Chelsea_citywide_expend_dict[2019] = 174074177

Chelsea_citywide_expend = pd.Series(Chelsea_citywide_expend_dict)

"""Revere
All numbers from citywide budget document
2016-2019 from page 11 of FY 19 document 
Note that this is a mix of expenditures and budget number. This is most up to date information available"""

Winthrop_citywide_expend_dict = {}
Winthrop_citywide_expend_dict[2016] = 46210166 #FY 2016 Actual
Winthrop_citywide_expend_dict[2017] = 49789852 #FY 2017 Actual
Winthrop_citywide_expend_dict[2018] = 49146338 #FY 2018 Budget
Winthrop_citywide_expend_dict[2019] = 50703576 #Fy 2019 Adopted

Winthrop_citywide_expend = pd.Series(Winthrop_citywide_expend_dict)
