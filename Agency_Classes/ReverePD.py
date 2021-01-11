"""Revere PD was given it's own class on January 8th"""
import pandas as pd
import sys

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)
sys.path.insert(0, "%sFringe" % cost_type_dir)
sys.path.insert(0, "%sCapital_Costs" % cost_type_dir)
from LocalPD_Pensions import  ReverePD_Pensions
from LocalPD_Fringe import ReverePD_Fringe
from ReverePD_Capital_Costs import ReverePD_Capital_Costs

from Police_Dept import PoliceDepartment

class ReverePD(PoliceDepartment):
    """Created by Sasha June 25th
    Revere has no API, so this code will iterate over pdfs I manually downloaded from Revere's site
    To do: summarize 2016 budget, get $ spend on weapons and weapons related expenses
    New July 6th: different documents have different mission statements, store in dict
    Right now, this doesn't use the Budget Summary the page after the pie chart for 2017, 2018, 2019 though
    possible we could get some useful info out of it.
    For Revere PD, there is a big capital expenditure for line-item 'public safety.''"""

    def __init__(self, yr):
        PoliceDepartment.__init__(self, alias="Revere PD", official_name="Revere PD", year_range=yr)
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Recommended",
                                                                           "Total Recommended",
                                                                           "Payroll Adopted",
                                                                           "Non-Payroll Expenses Adopted"
                                                                           "Total Adopted",
                                                                           "Payroll Mayor's Request",
                                                                           "Non-Payroll Expenses Request",
                                                                           "Total Mayor's Request",
                                                                           "Total Expenditures"])
        self.get_budget_summary()
        self.add_operating_costs()
        self.capital_expenditures_by_year = ReverePD_Capital_Costs()
        self.pensions, self.PD_fraction = ReverePD_Pensions(self)
        self.fringe = ReverePD_Fringe(self.PD_fraction)


    def get_budget_summary(self):
        """Hardcode in numbers from budget pdf"""
        #From 2016 Document Page 175
        self.budget_summary.loc["Total Mayor's Request", 2016] = 10061723
        #Page 183
        self.budget_summary.loc["Payroll Mayor's Request", 2016] = 8997073
        #Page 186
        self.budget_summary.loc["Non-Payroll Expenses Mayor's Request", 2016] = 1064650

        #From 2017 Document Page 173
        self.budget_summary.loc["Payroll Adopted", 2016] = 9047062
        self.budget_summary.loc["Non-Payroll Expenses Adopted", 2016] = 1064650
        self.budget_summary.loc["Total Adopted", 2016] = 10111712

        self.budget_summary.loc["Payroll Mayor's Request", 2017] = 9064601
        self.budget_summary.loc["Non-Payroll Expenses Mayor's Request", 2017] = 1012450
        self.budget_summary.loc["Total Mayor's Request", 2017] = 10077051

        #From 2018 Document page 201
        self.budget_summary.loc["Payroll Adopted", 2017] = 9083601
        self.budget_summary.loc["Non-Payroll Expenses Adopted", 2017] = 1012450
        self.budget_summary.loc["Total Adopted", 2017] = 10096051

        self.budget_summary.loc["Payroll Mayor's Request", 2018] = 9357467
        self.budget_summary.loc["Non-Payroll Expenses Mayor's Request", 2018] = 1093714
        self.budget_summary.loc["Total Mayor's Request", 2018] = 10451181

        #From 2019 Document page 104
        self.budget_summary.loc["Payroll Adopted", 2018] = 9357467
        self.budget_summary.loc["Non-Payroll Expenses Adopted", 2018] = 979764
        self.budget_summary.loc["Total Adopted", 2018] = 10337231

        self.budget_summary.loc["Payroll Mayor's Request", 2019] = 9735336
        self.budget_summary.loc["Non-Payroll Expenses Mayor's Request", 2019] = 868764
        self.budget_summary.loc["Total Mayor's Request", 2019] = 10604100

        #From 2020 Document page 104
        self.budget_summary.loc["Payroll Adopted", 2019] = 9735336
        self.budget_summary.loc["Non-Payroll Expenses Adopted", 2019] = 983764
        self.budget_summary.loc["Total Adopted", 2019] = 10719100



    def add_operating_costs(self):
        """Pensions_statewide shouldn't be passed in, better solution should be found
        Note that we take budgeted dollars for payroll because the budgeted dollars are broken down by
        payroll vs non-payroll in a more precise way"""
        self.operating_costs = self.budget_summary.loc["Total Adopted"]
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Adopted", self.year_range]
        self.non_payroll_operating_expenditures_by_year = self.budget_summary.loc["Non-Payroll Expenses Adopted"]
        self.payroll_by_year = self.payroll_expenditures_by_year
        self.payroll_by_year = self.payroll_by_year.astype(float) #Why is this conversion needed? Figure out during refactor
