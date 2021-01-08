"""Winthrop was given it's own file on Jan 8th"""

import pandas as pd
import sys

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)

from LocalPD_Pensions import WinthropPD_Pensions_Benefits

from PoliceDept import PoliceDepartment

class WinthropPD(PoliceDepartment):
    """Last Updated by Sasha July 30th to pass ReverePD object"""

    def __init__(self, ReverePD_fraction):
        year_range = list(range(2016, 2020))
        PoliceDepartment.__init__(self, "Winthrop PD", "Winthrop PD", year_range)

        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Expenses",
                                                                           "Capital Expenses",
                                                                           "Total Expenses"])
        self.get_budget_summary()
        self.fringe, self.pensions = WinthropPD_Pensions_Benefits(ReverePD_fraction)
        self.add_operating_costs()

    def add_operating_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Written August 12th
        Need to subtract capital expenditures here"""


        self.operating_costs = self.budget_summary.loc["Total Expenses"]

        self.payroll_by_year = self.budget_summary.loc["Payroll Expenses"]
        self.capital_expenditures_by_year = self.budget_summary.loc["Capital Expenses"]
        self.non_payroll_operating_expenditures_by_year = self.operating_costs - self.payroll_by_year - \
                                                          self.capital_expenditures_by_year
        self.payroll_expenditures_by_year = self.payroll_by_year


    def get_budget_summary(self):
        """New on Jan 8th move to all hard-coded"""

        #From 2019 budget document page 67
        self.budget_summary.loc["Payroll Expenses", 2016] = 2842909
        self.budget_summary.loc["Capital Expenses", 2016] = 0
        self.budget_summary.loc["Total Expenses", 2016] = 3037686


        #From 2021 Budget Document Page 73

        self.budget_summary.loc["Payroll Expenses", 2017] = 2927191
        self.budget_summary.loc["Capital Expenses", 2017] = 39393
        self.budget_summary.loc["Total Expenses", 2017] = 3213280

        self.budget_summary.loc["Payroll Expenses", 2018] = 3066911
        self.budget_summary.loc["Capital Expenses", 2018] = 40000
        self.budget_summary.loc["Total Expenses", 2018] = 3331505

        self.budget_summary.loc["Payroll Expenses", 2019] = 3803402
        self.budget_summary.loc["Capital Expenses", 2019] = 0
        self.budget_summary.loc["Total Expenses", 2019] = 4036935
