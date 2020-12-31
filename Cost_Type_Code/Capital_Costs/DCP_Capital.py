"""This code is to take capital costs from CAPITAL ASSET MANAGEMENT AND MAINTENANCE DIVISION (DCP) which has capital
expenditures for state police, DOC, and courts. Site for Capital Asset Management and Maintenance Division is
here https://www.mass.gov/service-details/about-our-organization
The way it seems to work is that some long-term capital project financing is paid for through DCP but some is also paid
for through the relevant agency w/ appropriation code (2CN) CAPITAL. It seems to be that bigger projects are paid for
through DCP and smaller projects are through the agency's expenditures but that's just my sense from glancing at it"""

import pandas as pd
import sys

sys.path.insert(0, "../")
from Agency_Classes.Agency_Helpers.Find_Data import find_data

# Note that right now I assign all court expenditures to trial court, they could be spread out across legal category too
carceral_appropriations = {"trial_court": ["(11025600) COURT FACILITIES CAPITAL NEEDS",
                                           "(03302223) COURT FACILITY IMPROVEMENTS",
                                           "(11025700) COURT FACILITIES 2018",
                                           "(03302204) COURT FACILITIES CAPITAL NEEDS & F&E"],

                           "DOC": ["(89008500) JAIL AND CORRECTIONAL FACILITIES",
                                   "(11020004) COUNTY CORRECTION FACILITIES IMPROVEMNTS",
                                   "(89100023) CORRECTION FACILITY IMPROVEMENTS",
                                   "(11027967) COUNTY CORREC FACILITIES CONSTRUC/EXPAN-"],

                           "State_Police": ["(81001001) DEPARTMENT OF STATE POLICE"],
                           }


def get_capital_expenditures(client, requery=False):
    DCP = find_data(requery, client, "pegc-naaa", "Department = 'CAPITAL ASSET MANAGEMENT AND MAINTENANCE DIVISION (DCP)'"
                                          " AND budget_fiscal_year >= 2016 and budget_fiscal_year <= 2019",
                    "DCP_expenditures.csv")
    DCP = clean_DCP(DCP)
    df = pd.DataFrame(columns=list(range(2016, 2020)))
    for key in carceral_appropriations:
        df.loc[key] = DCP[DCP["appropriation_name"].isin(carceral_appropriations[key])]\
            .groupby("budget_fiscal_year").sum()["amount"]
    return df.fillna(0)

def clean_DCP(DCP):
    DCP["amount"] = DCP["amount"].astype(float)
    DCP["budget_fiscal_year"] = DCP["budget_fiscal_year"].astype(int)
    return DCP
