"""The Revere Budgets have a capital expenditures section, where some projects are totally revere PD related and some
 are 'Public Safety.' For the 'Public Safety' Projects we will take the % of public safety budget that goes to the
 cops and say that the % of 'Public Safety' capital expenditures that go to cops is the same %"""

import pandas as pd

def get_ReverePD_Capital_Costs():
    df = pd.DataFrame(columns=list(range(2016,2020)),
                      index=["ReverePD Projects", "Public Safety Projects"])

    correction = pd.Series(index = list(range(2016,2020)), data=0)

    #From FY16 Document
    df.loc["ReverePD Projects", 2016] = 102859.34
    df.loc["Public Safety Projects", 2016] = 1292643.74

    #From FY17 Document
    df.loc["ReverePD Projects", 2017] = 104200
    df.loc["Public Safety Projects", 2017] = 1294156
    correction.loc[2016] = 10111712/21237316

    #From FY18 Document
    df.loc["ReverePD Projects", 2018] = 101950
    df.loc["Public Safety Projects", 2018] = 1082010
    correction.loc[2017] = 10096051/21845099

    #From FY19 Document
    df.loc["ReverePD Projects", 2019] = 50000
    df.loc["Public Safety Projects", 2019] =0
    correction.loc[2018] = 10332731/22393355
    return df.loc["ReverePD Projects"] + correction*df.loc["Public Safety Projects"]


