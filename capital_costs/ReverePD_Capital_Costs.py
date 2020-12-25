"""The Revere Budgets have a capital expenditures section, where some projects are totally revere PD related and some
 are 'Public Safety.' For the 'Public Safety' Projects we will take the % of public safety budget that goes to the
 cops and say that the % of 'Public Safety' capital expenditures that go to cops is the same %
 Fustrating that the capital projects summary section doesn't exist from 2019 on"""

import pandas as pd

def get_ReverePD_Capital_Costs():
    df = pd.DataFrame(columns=list(range(2016,2020)),
                      index=["ReverePD Projects", "Public Safety Projects"])

    correction = pd.Series(index = list(range(2016,2020)), data=0)

    #From FY16 Document Page 27
    df.loc["ReverePD Projects", 2016] = 102859.34
    df.loc["Public Safety Projects", 2016] = 1292643.74

    #From FY17 Document Page I - 34
    df.loc["ReverePD Projects", 2017] = 104200
    df.loc["Public Safety Projects", 2017] = 1294156
    #Page I-26
    correction.loc[2016] = 10111712/21237316

    #From FY18 Document Page 30
    df.loc["ReverePD Projects", 2018] = 101950
    df.loc["Public Safety Projects", 2018] = 1082010
    # Page 22
    correction.loc[2017] = 10096051/21845099

    #From FY19 Document
    df.loc["ReverePD Projects", 2019] = 0
    df.loc["Public Safety Projects", 2019] =0
    #Page 30
    correction.loc[2018] = 10332731/22393355

    return df.loc["ReverePD Projects"] + correction*df.loc["Public Safety Projects"]


