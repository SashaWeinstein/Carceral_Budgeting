"""CPCS got it's own file Dec 29th"""

import pandas as pd
import sys
from sodapy import Socrata
from Agency_Classes_Big import StateAgency
cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"

sys.path.insert(0, "%sCapital_Costs" % cost_type_dir)


app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

from DCP_Capital import get_capital_expenditures
DCP_capital_expenditures = get_capital_expenditures(client)


class CPCS(StateAgency):
    """CPCS needs it's own class as it's R24 dollars are counted towards payroll instead of operating costs"""
    def __init__(self, alias, official_name, year_range, payroll_vendors, category, client, correction_function,
                 settlement_agencies):
        StateAgency.__init__(self, alias, official_name, year_range, category, correction_function, settlement_agencies,
                             payroll_vendors, None, client, remove_R24=True)


    def get_final_costs(self, apply_correction=True):
        """Created August 12 for new methodology where we use expenditures for everything"""
        if not self.final_costs_calculated:
            self.final_costs_calculated = True
            # self.add_expenditures(client)
            # self.get_expenditures_by_year()
            self.RR_correction()
            self.add_settlements()
            self.add_payroll_by_year()
            self.add_fringe()
            self.payroll_by_year += self.R24_by_year #This is dangerous but it's ok for now. After refactor, cthru_payroll_by_year and final_payroll_by_year should be split into two categories
            self.operating_costs = self.expenditures_by_year.loc["Total Expenditures"]
            # New Aug 24th: split operating costs into payroll, non-payroll

            if self.alias in DCP_capital_expenditures.index:
                self.capital_expenditures_by_year += DCP_capital_expenditures.loc[self.alias, self.year_range]

            self.final_cost = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year + \
                              self.settlements + self.fringe + \
                              self.capital_expenditures_by_year

        if apply_correction:
            return self.correction_function(self.final_cost)
        else:
            return self.final_cost

    def RR_correction(self):
        """Written 12/17 to move public counsel dollars from expenditures to payroll"""

        self.R24_by_year = self.R24.groupby("budget_fiscal_year").sum()["amount"].loc[self.year_range]


    def add_payroll_by_year(self, total_OT_only=False):
        """Special version of this function for CPCS gets payroll by year already created in RR_correction and populated
        with public counsel spending"""
        self.add_payroll(total_OT_only)
        payroll_by_calendar_year = self.payroll.groupby("year")[self.pay_col].sum().T
        payroll_by_FY = pd.Series(index=self.year_range)
        for y in self.year_range:
            payroll_by_FY.loc[y] = .5 * payroll_by_calendar_year.loc["pay_total_actual", y - 1] + \
                                      .5 * payroll_by_calendar_year.loc["pay_total_actual", y]

        self.payroll_by_year = payroll_by_FY*(1-self.fraction_payroll_federal)

