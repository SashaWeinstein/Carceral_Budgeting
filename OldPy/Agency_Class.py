"""Last updated by Sasha on June 22nd to collect data for payroll, budget as well as expenditures
To do: clean this up
Maybe rename all functions for cthru data with term "cthru" in name.
Or maybe split this into classes that inherit from Agency, like state and local"""
import pandas as pd
from sodapy import Socrata
import os

class Agency():
    """For keeping track of info associated with a government agency
    To do: make client, year_range attributes
    Last updated by Sasha on June 23rd to add local agencies, which are municipal police departments for now"""
    def __init__(self, alias, official_name, payroll_vendors=[], payroll_official_name=None, level="state"):
        self.level = level #New June 23rd, level is like state vs municipal
        self.alias = alias
        self.official_name = official_name
        self.payroll_official_name = payroll_official_name  # MBTA is lowercase in payroll system for some reason
        self.payroll_vendors = payroll_vendors  # Should be a list of vendors.
        self.expenditures = None
        self.payroll = None  # New on June 22nd
        self.pay_col = None  # List of column names to keep and sum payroll info over
        self.official_budget_name = self.official_name.split("(")[0][:-1] # Name in budget data in fmz7-6ft9
        self.budget = None
        self.budget_cols = None
        self.operating_budget = None # For Boston PD, maybe boston PD should get a class that inherits from Agency

    def add_expenditures(self, client, year_range):
        """Adds expenditures for agency over the given year range
        Uses this dataset https://cthru.data.socrata.com/dataset/Comptroller-of-the-Commonwealth-Spending/pegc-naaa
        client is Socrata object
        year_range is list of years to do analysis over"""
        file_name = "data/" + self.alias + "_expenditures.csv"
        self.expenditures = self.find_data(file_name, client, "pegc-naaa", year_range, self.construct_expenditures_SOQL)
        self.expenditures["amount"] = self.expenditures["amount"].astype(float)


    def get_expenditures_payroll(self):
        assert type(self.expenditures) == pd.core.frame.DataFrame,\
               "get payroll called before expenditures data assigned"
        self.expenditures["payroll_amount"] = self.expenditures[self.expenditures["vendor"].isin(self.payroll_vendors)]\
                                              ["amount"]
        self.expenditures["payroll_amount"].fillna(0, inplace=True)

    def add_payroll(self, client, year_range):
        """Created by Sasha on June 22nd to get payroll data from cthru endpoint
        Dataset is here https://cthru.data.socrata.com/dataset/Commonwealth-Of-Massachusetts-Payrollv2/rxhc-k6iz
        client is Socrata object
        year_range is list of years to get data for
        """
        file_name = "data/" + self.alias + "_payroll.csv"
        self.payroll = self.find_data(file_name, client, "rxhc-k6iz", year_range, self.construct_payroll_SOQL)
        assert not self.payroll.empty, "no payroll info found for " + self.alias
        self.pay_col = [i for i in self.payroll.columns if i[:3] == "pay"]
        # Following line is commented out because I wanted a simpler csv for Bobby at one point
        # self.pay_col = ["pay_total_actual", "pay_overtime_actual"]
        self.payroll[self.pay_col] = self.payroll[self.pay_col].astype(float)

    def add_buget(self, client, year_range):
        """Created by Sasha on June 22nd"""
        file_name = "data/" + self.alias + "_budget.csv"
        self.budget = self.find_data(file_name, client, "fmz7-6ft9", year_range, self.construct_budget_SOQL)
        assert not self.budget.empty, "no budget info found for " + self.alias
        self.budget_cols = ["total_enacted_budget", "total_available_for_spending"]
        self.budget[self.budget_cols] = self.budget[self.budget_cols].astype(float)

    def find_data(self, file_name, client, dataset, year_range, SOQL_constructor):
        """Look for matching csv in data directory, if it's there not fetch it from API
        file_name is generated from agency, dataset
        client is Socrata object
        dataset is name of dataset in cthru system"""
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
        else:
            result_json = client.get(dataset, where=SOQL_constructor(year_range), limit=999999)
            df = pd.DataFrame(result_json)
            assert df.shape[0] < 999999, "Agency found with more than 999999 expenditure records"
            df.to_csv(file_name)
        return df

    def get_local_PD_data(self):
        """Written by Sasha on June 23rd. First local police department this is built for is Boston PD"""
        if self.alias == "Boston PD":
            file_name = "data/" + self.alias + "Operating_Budget.csv"


    def construct_expenditures_SOQL(self, yr):
        return "Department = '" + self.official_name + "' AND budget_fiscal_year >= " + str(yr[0]) + \
               " AND budget_fiscal_year <= " + str(yr[-1])

    def construct_payroll_SOQL(self, yr):
        """Created by Sasha on June 22nd"""
        if self.payroll_official_name:
            official_name = self.payroll_official_name
        else:
            official_name = self.official_name
        return "department_division = '" + official_name + "' AND Year >= " + str(yr[0]) + \
                "AND Year <= " + str(yr[-1])

    def construct_budget_SOQL(self, yr):
        """Created by Sasha on June 22nd"""
        return "department_name = '" + self.official_budget_name + "' AND fiscal_year >= " + str(yr[0]) + \
        "AND fiscal_year <= " + str(yr[-1])

    def __repr__(self):
        return "Agency object for " + self.alias