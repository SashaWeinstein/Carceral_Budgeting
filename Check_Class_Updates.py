"""Written by Sasha on July 7th
Idea of this code is to take most recent csv's in results folder and compare them to csv's produced by updated
Agency_Classes code to make sure they match. I don't want to accidentally change something while I update code
If I want to change my state agencies class I could compare 2016-2019 for cthru data"""

import pandas as pd
import numpy as np
from Agency_Classes import BostonPD, ChelseaPD, ReverePD, WinthropPD

def check_all():
    out_dict = {}

    out_dict["Winthrop"] = check("results/winthrop_budget_pdfs/winthropPD_Jul2.csv", WinthropPD())
    return out_dict
    out_dict["Boston"] = check("results/boston_budget_pdfs/Jul2.csv", BostonPD())
    out_dict["Chelsea"] = check("results/chelsea_city_auditor/Jul7.csv", ChelseaPD())
    out_dict["Revere"] = check("results/revere_mayors_office/Jul6.csv", ReverePD())
    return out_dict


def check(path, object):
    saved_budget_summary = pd.read_csv(path)
    saved_budget_summary  = clean(saved_budget_summary)

    object.from_PDF()
    object.budget_summary.reset_index(inplace=True)
    new_budget_summary = clean(object.budget_summary)
    if not np.array_equal(saved_budget_summary, new_budget_summary):
        return saved_budget_summary, new_budget_summary
    else:
        return "all good"

def clean(df):
    df = df.iloc[:, 1:].applymap(lambda x: float(x.replace(",", "")) if type(x) == str else x)
    df.fillna(0, inplace=True)
    return df

