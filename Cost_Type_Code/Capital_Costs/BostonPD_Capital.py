"""Created on Dec 29th to replace scraper"""
import pandas as pd

def get_BostonPD_Capital_Costs(agency):

    #To do for refactor: get yr from agency
    yr = list(range(2016,2020))
    capital_costs_by_year = pd.Series(index=yr)

    #From FY19 Document
    capital_costs_by_year.loc[2016] = 5441996

    #From FY20 Document
    capital_costs_by_year.loc[2017] = 7909564

    #From FY21 Document
    capital_costs_by_year.loc[2018] = 18625711
    capital_costs_by_year.loc[2019] = 8502943
