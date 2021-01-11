"""State agency was given it's own file on Dec 31st"""
import pandas as pd
from sodapy import Socrata
import numpy as np
import sys
import os

from Agency_Parent import Agency

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)
sys.path.insert(0, "%sFringe" % cost_type_dir)
sys.path.insert(0, "%spdf_scraper" % cost_type_dir)
sys.path.insert(0, "%sCapital_Costs" % cost_type_dir)
sys.path.insert(0, "%sPayroll" % cost_type_dir)
sys.path.insert(0, "%sNon-Payroll_Operating" % cost_type_dir)
from Pensions_Final import pensions_from_payouts_fraction
from Statewide_Payroll import Fraction_Statewide_Payroll
from DCP_Capital import get_DCP_capital
from Statewide_Fringe import get_statewide_fringe

agency_corrections_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting" \
                         "/Exploratory/Agency_Corrections/"
sys.path.insert(0, agency_corrections_dir)
from Agency_Corrections import trial_court_pcnt_criminal



helper_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Agency_Classes/Agency_Helpers"
sys.path.insert(0, helper_dir)
from SOQL_Constructors import construct_expenditures_SOQL, construct_budget_SOQL, construct_payroll_SOQL, construct_settlements_SOQL
from Find_Data import find_data
from CY_To_FY import convert_CY_to_FY


app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

class StateAgency(Agency):
    """Last updated July 10th to get revenue data into it's own dataframe
    Possible to do: return one summary dataframe instead of expenditures, budget, revenue by year
    Another to do: add client in initialize agencies code
    To do: fix how year range is set, it's getting passed from multiple places and creating conflicts
    Really, really need to fix this it's causing lots of bugs. Need to set year range from one place, when
    agency class is created, and have it all propogate
    Also: something strange is happending where once initialize agencies has been run and then I call it agian,
    the objects aren't re-initialized. Should figure out what is going on
    Actually, objects are getting intialized when I import initialize agencies, which isn't what I want."""

    def __init__(self, alias, official_name, year_range, category, correction_function=None, settlement_agencies=None,
                 payroll_vendors=[], payroll_official_name=None, client=None,
                 pension_function=pensions_from_payouts_fraction,
                 remove_R24=False):
        Agency.__init__(self, alias, official_name, year_range, category, correction_function)
        self.client = client
        self.payroll_official_name = payroll_official_name  # MBTA is lowercase in payroll system for some reason
        self.payroll_vendors = payroll_vendors  # Should be a list of vendors.
        self.settlement_agencies = settlement_agencies
        self.capital_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.non_hidden_fringe = pd.DataFrame()  # New Nov 9th
        self.non_hidden_fringe_by_year = pd.Series(index=self.year_range, data=0)
        self.calender_year_data = True  # New June 24th

        self.payroll = None  # New on June 22nd
        self.payroll_by_year = pd.Series(index=self.year_range, data=None)
        self.pay_col = None  # List of column names to keep and sum payroll info over

        self.expenditures_by_year = pd.DataFrame(columns=self.year_range)
        self.operating_costs = None  # This is where cost type "operating costs" will be stored
        self.remove_R24 = remove_R24
        self.get_expenditures_by_year()
        self.add_payroll_by_year()
        # Code to get payroll fraction should be moved somewhere else
        self.payroll_fraction = Fraction_Statewide_Payroll(self)
        self.pensions, self.local_pensions = pension_function(self)
        self.add_fringe()
        self.capital_expenditures_by_year += get_DCP_capital(self)
        self.final_costs_calculated = False
        self.get_final_costs()

    #Important refactor: change this function which I hate so bad
    def get_final_costs(self, apply_correction=True):
        """This is a stupid function right now. The only reason to have a special 'get final costs' function right
        now is that the trial court uses a more complex agency correction. So maybe this should be replaced with a
        'apply correction' function that applies correction, which we call instead of the 'agency_correction' when
        results are produced. """

        #During refactor move this somewhere
        if self.alias =="trial_court":
            pcnt_criminal_correction = trial_court_pcnt_criminal()

        self.final_cost = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year + \
                          self.pensions + self.fringe + \
                          self.capital_expenditures_by_year

        if apply_correction:
            if self.alias == "trial_court":
                return self.correction_function(self.final_cost) + self.local_pensions*pcnt_criminal_correction  #Janky but should work
            return self.correction_function(self.final_cost)
        else:
            return self.final_cost

    def add_expenditures(self):
        """Adds expenditures for agency over the given year range
        Uses this dataset https://cthru.data.socrata.com/dataset/Comptroller-of-the-Commonwealth-Spending/pegc-naaa
        client is Socrata object
        year_range is list of years to do analysis over
        Do to: pull out spending on fringe benefits and put that in benefit series
        """
        file_name = self.alias + "_expenditures.csv"
        self.expenditures = find_data(self.requery, self.client,  "pegc-naaa", construct_expenditures_SOQL(self),
                                      file_name)

        self.clean_expenditures()
        self.remove_federal()
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"].str.contains("INTRAGOVERNMENTAL") == False]

        self.remove_capital_expenditures()
        self.remove_fringe_expenditures()

        if self.remove_R24:
            self.remove_R24_expenditures() #This is called for CPCS

    def remove_fringe_expenditures(self):
        non_hidden_fringe = self.expenditures[
            self.expenditures["object_class"] == "(DD) PENSION & INSURANCE RELATED EX"]
        self.non_hidden_fringe_by_year = non_hidden_fringe.groupby("budget_fiscal_year").sum()["amount"].T
        self.non_hidden_fringe_by_year = self.non_hidden_fringe_by_year.reindex(self.year_range, fill_value=0)
        self.expenditures = self.expenditures[
            self.expenditures["object_class"] != "(DD) PENSION & INSURANCE RELATED EX"]

    def remove_capital_expenditures(self):
        capital_expenditures = self.expenditures[self.expenditures["appropriation_type"] == "(2CN) CAPITAL"]
        self.capital_expenditures_by_year = capital_expenditures.groupby("budget_fiscal_year").sum()[
            "amount"].T
        self.capital_expenditures_by_year = self.capital_expenditures_by_year.reindex(self.year_range, fill_value=0)
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"] != "(2CN) CAPITAL"]

    def clean_expenditures(self):
        self.expenditures["amount"] = self.expenditures["amount"].astype(float)
        self.expenditures["budget_fiscal_year"] = self.expenditures["budget_fiscal_year"].astype(int)

    def remove_federal(self):
        """Written on Dec 31st
        Fraction Payroll Federal is used to correct payroll record
        Federal Expenditures per year is used for footnotes"""

        self.find_fraction_payroll_expend_federal()
        self.find_federal_expenditures_by_year()
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"].str.contains("FEDERAL")==False]

    def find_federal_expenditures_by_year(self):
        """This number is used for footnotes """
        federal_expenditures = self.expenditures[
            self.expenditures["appropriation_type"].str.contains("FEDERAL")]
        self.federal_expenditures_by_year = federal_expenditures.groupby("budget_fiscal_year").sum()[
            "amount"].T
        self.federal_expenditures_by_year = self.federal_expenditures_by_year.reindex(self.year_range, fill_value=0)

    def find_fraction_payroll_expend_federal(self):
        """Find what fraction of the payroll expenditures are federal money and save to use in payroll correction"""
        federal_payroll_expenditures = self.expenditures[ \
            (self.expenditures["appropriation_type"].str.contains("(?i)federal")) &
            (self.expenditures["vendor"].str.contains("(?i)payroll"))]
        federal_payroll_expenditures_by_year = federal_payroll_expenditures.groupby("budget_fiscal_year")[
            "amount"].sum()
        self.fraction_payroll_federal = federal_payroll_expenditures_by_year / \
                                        self.expenditures[self.expenditures["vendor"].str.contains("(?i)payroll")] \
                                            .groupby("budget_fiscal_year")["amount"].sum()
        self.fraction_payroll_federal = self.fraction_payroll_federal.loc[self.year_range].fillna(0)


    def get_expenditures_by_year(self):
        """This could be clearer I think"""
        self.add_expenditures()
        payroll_expenditures = self.expenditures[self.expenditures["vendor"].str.contains("(?i)payroll")]
        non_payroll_expenditures = self.expenditures[self.expenditures["vendor"].str.contains("(?i)payroll") == False]
        assert np.isclose(payroll_expenditures["amount"].sum() + non_payroll_expenditures["amount"].sum(),
                          self.expenditures["amount"].sum())

        self.payroll_expenditures_by_year = payroll_expenditures.groupby("budget_fiscal_year").sum()["amount"].loc[
            self.year_range]
        self.non_payroll_operating_expenditures_by_year = non_payroll_expenditures. \
            groupby("budget_fiscal_year").sum()["amount"].loc[self.year_range]


    def add_payroll(self, total_OT_only=False):
        """Created by Sasha on June 22nd to get payroll data from cthru endpoint
        Dataset is here https://cthru.data.socrata.com/dataset/Commonwealth-Of-Massachusetts-Payrollv2/rxhc-k6iz
        client is Socrata object
        year_range is list of years to get data for
        New July 6th: total_OT_only is bool for whether we want all pay categories or just OT, total payroll
        """
        file_name = self.alias + "_payroll.csv"
        self.payroll = find_data(self.requery, self.client, "rxhc-k6iz", construct_payroll_SOQL(self),
                                      file_name)
        assert not self.payroll.empty, "no payroll info found for " + self.alias
        if total_OT_only:
            self.pay_col = ["pay_total_actual", "pay_overtime_actual"]
        else:
            self.pay_col = [i for i in self.payroll.columns if i[:3] == "pay"]
        self.payroll[self.pay_col] = self.payroll[self.pay_col].astype(float)
        self.payroll.loc[:, "year"] = self.payroll.loc[:, "year"].astype(int)

    def add_payroll_by_year(self):
        """Written by Sasha on June 24th to take code from exploratory main"""
        self.add_payroll(False)
        payroll_by_calendar_year = self.payroll.groupby("year")["pay_total_actual"].sum().T
        payroll_by_FY = convert_CY_to_FY(payroll_by_calendar_year, self.year_range)
        self.payroll_by_year = payroll_by_FY * (1-self.fraction_payroll_federal)

    def add_fringe(self):
        """Combines fringe from expenditure record with fringe from statewide benefits"""
        hidden_fringe = get_statewide_fringe(self)
        self.fringe = hidden_fringe.loc[self.year_range] + self.non_hidden_fringe_by_year

    def add_settlements(self):
        """Settlements are NOT used in Dec 31st version of anaylsis. This code is here in case settlements are to be
        added"""
        self.settlements = pd.Series(index=self.year_range, data=[0] * len(self.year_range))
        if self.settlement_agencies:
            file_name = self.alias + "_settlements.csv"
            settlements_overall = find_data(self.requery, self.client, "6j38-k6fr", construct_settlements_SOQL(self),
                                            file_name)
            settlements_overall["line_amount"] = settlements_overall["line_amount"].astype(float)
            self.settlements = pd.Series(index=self.year_range, data=[0] * len(self.year_range))
            self.settlements = self.settlements + settlements_overall.groupby("bfy").sum()["line_amount"]
            self.settlements = self.settlements.loc[self.year_range].fillna(0)
