"""This code generates final results to .csv's to be used for Results, Misc_Analyses, and Visulize directories
Idea is that I load this py file into a jupyter notebook, eyeball csv's before I save them
note that 'By Type' refers to 'by cost type'"""



import pandas as pd
import os
import sys


home_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory"
sys.path.insert(0, home_dir)

from Initialize_Agencies import get_agencies
yr = list(range(2016,2020))
agencies = get_agencies(yr)


def get_by_Agency_Cost_Type_empty_df():
    return pd.DataFrame(columns=["Agency", "Category ", "Cost Type"] + yr)



def get_preCorrection_by_Agency_Type():
    final_by_agency_type_pre_correction = get_by_Agency_Cost_Type_empty_df()
    for _, agency in agencies.items():
        total_cost, payroll, fringe, capital, non_payroll_operating, pensions = agency.get_final_costs(False, True)
        final_by_agency_type_pre_correction.loc[agency.alias + " Payroll Costs"] = [agency.alias, agency.category, "Payroll"] + list(payroll)
        final_by_agency_type_pre_correction.loc[agency.alias + " Non-Payroll Operating Costs"] = [agency.alias, agency.category, "Non-Payroll Operating"] + list(non_payroll_operating)
        final_by_agency_type_pre_correction.loc[agency.alias + " Pension Costs"] = [agency.alias, agency.category, "Pensions"] + list(pensions)
        final_by_agency_type_pre_correction.loc[agency.alias + " Fringe Benefit Costs"] = [agency.alias, agency.category,"Fringe Benefits"] + list(fringe)
        final_by_agency_type_pre_correction.loc[agency.alias + " Capital Costs"] = [agency.alias, agency.category, "Capital"] + list(capital)
    return final_by_agency_type_pre_correction

by_agency_type = get_by_Agency_Cost_Type_empty_df()
for _, agency in agencies.items():
    total_cost, payroll, fringe, capital, non_payroll_operating, pensions  = agency.get_final_costs(True, True)
    by_agency_type.loc[agency.alias + " Payroll Costs"] = [agency.alias, agency.category, "Payroll"] + list(payroll)
    by_agency_type.loc[agency.alias + " Non-Payroll Operating Costs"] = [agency.alias, agency.category, "Non-Payroll Operating"] + list(non_payroll_operating)
    by_agency_type.loc[agency.alias + " Pension Costs"] = [agency.alias, agency.category, "Pensions"] + list(pensions)
    by_agency_type.loc[agency.alias + " Fringe Benefit Costs"] = [agency.alias, agency.category, "Fringe Benefits"] + list(fringe)
    by_agency_type.loc[agency.alias + " Capital Costs"] = [agency.alias, agency.category, "Capital"] + list(capital)

def get_by_Agency_Type():
    return by_agency_type


def get_by_Type():
    by_type = by_agency_type.groupby("Cost Type").sum()[yr]
    return by_type



by_agency_type_split_hidden = pd.DataFrame(columns=["Agency", "Category", "Cost Type", "Hidden"] + yr)
for _, agency in agencies.items():
    total_cost, non_hidden_payroll, hidden_payroll,\
    non_hidden_fringe, hidden_fringe, non_hidden_capital, hidden_capital,\
    non_payroll_operating, pensions =\
        agency.get_final_costs(True, True, True)
    title_costs= [
        ("Stated Payroll Costs", non_hidden_payroll, False),
        ("Hidden Payroll Costs", hidden_payroll, True),
        ("Stated Fringe Costs", non_hidden_fringe, False),
        ("Hidden Fringe Costs", hidden_fringe, True),
        ("Stated Capital Costs", non_hidden_capital, False),
        ("Hidden Capital Costs", hidden_capital, True),
        ("Non-Payroll Operating Costs", non_payroll_operating, False),
        ("Pension Costs", pensions, True)
    ]
    print("iterated to agency of ", agency.alias)
    for t in title_costs:
        print("iterated to tuple of ")
        print(t[0])
        print(t[1])
        print(t[2])
        by_agency_type_split_hidden.loc[agency.alias + " " + t[0]] = [agency.alias, agency.category, t[0], t[2]] + list(t[1])

def get_by_Agency_Type_SH():
    """SH stands for split hidden"""
    return by_agency_type_split_hidden

def agency_type_apply_gb(columns):
    return by_agency_type_split_hidden.groupby(columns).sum()[yr]


def get_by_Type_SH():
    by_cost_type_split_payroll = agency_type_apply_gb("Cost Type")
    return by_cost_type_split_payroll

def get_by_Agency():
    by_agency = agency_type_apply_gb("Agency")
    return by_agency

def get_by_Agency_SH():
    final_by_agency_SH = agency_type_apply_gb(["Agency", "Hidden"])
    return final_by_agency_SH

def get_by_Category():
    by_category = agency_type_apply_gb("Category")
    return by_category

def get_by_Category_SH():
    by_category = agency_type_apply_gb(["Category", "Hidden"])
    return by_category

def get_by_Year():
    return pd.DataFrame(by_agency_type_split_hidden[yr].sum()).reset_index()

def get_by_Year_SH():
    by_hidden = agency_type_apply_gb("Hidden")
    return by_hidden


from Agency_Corrections import all_agency_corrections
def get_Agency_corrections():
    return all_agency_corrections()

