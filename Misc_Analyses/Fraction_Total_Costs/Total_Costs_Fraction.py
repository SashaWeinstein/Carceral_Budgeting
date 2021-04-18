"""This file was created for the January Slidedeck. Get fraction of statewide spending committed
to incarceration and Boston City expenditures committed to BPD"""

import pandas as pd

import sys
sys.path.insert(0, "../../Final_Results")
from Final_Results_Helpers import get_Result
yr = list(range(2016,2020))

#2016 is from https://budget.digital.mass.gov/summary/fy20/enacted?tab=historical-spending
#2017-2019 from https://budget.digital.mass.gov/summary/fy21/enacted?tab=historical-spending
MA_expend = {2016: 38402539928, 2017: 39095346106, 2018: 40463158944, 2019: 42240687227}
MA_expend = pd.Series(MA_expend)
#https://www.boston.gov/sites/default/files/embed/file/2019-04/v1_02-_19_a_summary-budget.pdf
#2018, 2019 data from https://www.boston.gov/sites/default/files/file/2020/10/2-Volume%201%20-%20Operating%20Budget.pdf
Boston_citywide_expend = {2016: 2881.09*10**6, 2017: 2990.13*10**6, 2018: 3192.10*10**6, 2019: 3348.53*10**6}
Boston_citywide_expend = pd.Series(Boston_citywide_expend)


sys.path.insert(0, "../../Agency_Corrections")
from Agency_Corrections import population_correction

suff_expend = population_correction(MA_expend)


by_agency = get_Result("Final_by_Agency_splitHidden.csv")

def is_municipal(x):
    if x in ["Boston PD", "Revere PD", "Chelsea PD", "Winthrop PD"]:
        return True
    return False

def get_Statewide_Fraction():
    by_agency["Municipal"] = [is_municipal(x) for x in by_agency.index]
    by_agency_statewide = by_agency[by_agency["Municipal"] == False]
    statewide_by_year_SH = by_agency_statewide.groupby("Hidden")[yr].sum().rename(index= {False:"Stated", True:"Hidden"})
    statewide_by_year_SH.loc["Total"] = statewide_by_year_SH.sum()

    return statewide_by_year_SH/suff_expend

def get_Boston_Fraction():
    BPD_SH = by_agency.loc["Boston PD"].set_index("Hidden")[yr]
    BPD_SH = BPD_SH.rename(index= {False:"Stated", True:"Hidden"})
    BPD_SH.loc["Total"] = BPD_SH.sum()

    return BPD_SH/Boston_citywide_expend

def get_Statewide_plus_Boston_Fraction():
    """The reason I'm doing it this way now is that I don't have expenditure record for non-boston cities handy.
    The expenditure record for those cities is spotty, probably better to just report fraction of 'total' spending
    for Boston, state-level agencies"""
    selected = by_agency[[x not in ["Chelsea PD", "Revere PD", "Winthrop PD"] for x in by_agency.index]]
    by_year_SH = selected.groupby("Hidden")[yr].sum().rename(index= {False:"Stated", True:"Hidden"})
    by_year_SH.loc["Total"] = by_year_SH.sum()

    denominator = (suff_expend+Boston_citywide_expend)

    return by_year_SH/denominator


