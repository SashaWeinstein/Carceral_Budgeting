"""This file was created for the January Slidedeck. Get fraction of statewide spending committed
to incarceration and Boston City expenditures committed to BPD"""

import pandas as pd

import sys

sys.path.insert(0, "../../Final_Results")
from Final_Results_Helpers import get_Result

yr = list(range(2016, 2020))

from Serve_Total_Costs import MA_expend, Boston_citywide_expend, Revere_citywide_expend, Chelsea_citywide_expend, \
    Winthrop_citywide_expend

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
    statewide_by_year_SH = get_by_year_SH(by_agency_statewide)
    statewide_by_year_SH.loc["Total"] = statewide_by_year_SH.sum()

    return statewide_by_year_SH / suff_expend


def get_Boston_Fraction():
    BPD_SH = by_agency.loc["Boston PD"].set_index("Hidden")[yr]
    BPD_SH = BPD_SH.rename(index={False: "Stated", True: "Hidden"})
    BPD_SH.loc["Total"] = BPD_SH.sum()

    return BPD_SH / Boston_citywide_expend


def get_Statewide_plus_Boston_Fraction():
    """The reason I'm doing it this way now is that I don't have expenditure record for non-boston cities handy.
    The expenditure record for those cities is spotty, probably better to just report fraction of 'total' spending
    for Boston, state-level agencies"""
    selected = by_agency[[x not in ["Chelsea PD", "Revere PD", "Winthrop PD"] for x in by_agency.index]]
    by_year_SH = get_by_year_SH(selected)

    denominator = (suff_expend + Boston_citywide_expend)

    return by_year_SH / denominator


def get_Total_Fraction():
    by_year_SH = get_by_year_SH(by_agency)
    denominator = suff_expend + Boston_citywide_expend + Chelsea_citywide_expend + Revere_citywide_expend + \
                  Winthrop_citywide_expend
    return  (by_year_SH/denominator).mean(axis=1), denominator


def get_Municipal_Fraction():
    """Find fraction of municipal budgets dedicated to policing"""
    selected = by_agency[[x in ["Boston PD", "Chelsea PD", "Revere PD", "Winthrop PD"] for x in by_agency.index]]
    by_year_SH = get_by_year_SH(selected)
    print(by_year_SH.loc["Total"].mean())
    denominator = Boston_citywide_expend + Chelsea_citywide_expend + Revere_citywide_expend + Winthrop_citywide_expend
    return (by_year_SH / denominator).mean(axis=1), denominator.mean()


def get_by_year_SH(selected):
    by_year_SH = selected.groupby("Hidden")[yr].sum().rename(index={False: "Stated", True: "Hidden"})
    by_year_SH.loc["Total"] = by_year_SH.sum()
    return by_year_SH
