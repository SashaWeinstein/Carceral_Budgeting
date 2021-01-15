"""Chelsea PD was given it's own class January 8th"""

import pandas as pd
import sys

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)
sys.path.insert(0, "%sFringe" % cost_type_dir)
sys.path.insert(0, "%sPayroll" % cost_type_dir)
from LocalPD_True_Payroll import True_Earnings
from LocalPD_Pensions import ChelseaPD_Pensions
from LocalPD_Fringe import ChelseaPD_Fringe


from Police_Dept import PoliceDepartment

class ChelseaPD(PoliceDepartment):
    """Created by Sasha on June 25th. As of right now I don't have access to API for Chelsea's open data site
    here https://chelseama.finance.socrata.com/#!/view-data so instead I'm manually downloading csv's
    New July 6th: take out 'appropriations column' and replace with 'proposed budget column' which
    will only be populated with 2021 data
    Note that there is additional debt service for chelsea but I can't figure out what projects that debt service is
    from"""

    def __init__(self, yr):
        PoliceDepartment.__init__(self, alias="Chelsea PD", official_name="Chelsea PD", year_range=yr)
        self.dept_title = "Police Department Program Budget"
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Expenditures",
                                                                           "Non-Payroll Expenditures",
                                                                           "Total Expenditures"])
        self.get_budget_summary()
        self.add_true_earnings()
        self.calculate_hidden_payroll()
        self.pensions = ChelseaPD_Pensions(self)
        self.fringe = ChelseaPD_Fringe(self)


    def get_budget_summary(self):
        """Created Thursday Dec 24th. Hard-coded from budget documents"""
        #From FY20 Document
        self.budget_summary.loc["Payroll Expenditures", 2016] = 9685922
        self.budget_summary.loc["Non-Payroll Expenditures", 2016] = 1050166
        self.capital_expenditures_by_year.loc[2016] =173000

        #From FY21 Documeent
        self.budget_summary.loc["Payroll Expenditures", 2017] = 9551598
        self.budget_summary.loc["Non-Payroll Expenditures", 2017] = 701295.76
        self.capital_expenditures_by_year.loc[2017] = 164000

        self.budget_summary.loc["Payroll Expenditures", 2018] = 9923457.54
        self.budget_summary.loc["Non-Payroll Expenditures", 2018] = 710475.69
        self.capital_expenditures_by_year.loc[2018] = 161438.91

        self.budget_summary.loc["Payroll Expenditures", 2019] = 11526261.80
        self.budget_summary.loc["Non-Payroll Expenditures", 2019] = 639385.29
        self.capital_expenditures_by_year.loc[2019] = 0


    def add_true_earnings(self):
        """New July 30th. Replace expenditure numbers 2016-2019 with true earnings
        Note that for 2016 for chelsea we don't have actual payroll so I will use rough estimation, need better
         way to fix later"""
        self.payroll_by_year,self.PD_fraction_non_teacher, self.PD_fraction_total, self.payroll = True_Earnings(self.alias)

        #2016 is missing from earnings dataset, use 2017 number
        self.PD_fraction_non_teacher[2016] = self.PD_fraction_non_teacher[2017]
        self.PD_fraction_total[2016] = self.PD_fraction_total[2017]

        #Payroll expenditures are numbers from budget documents
        self.payroll_expenditures_by_year = self.budget_summary.loc[
            "Payroll Expenditures", self.year_range]
        #No earnings for 2016, use budget document numbers instead
        self.payroll_by_year[2016] = self.budget_summary.loc["Payroll Expenditures", 2016]
        self.payroll_expenditures_by_year[2016] = self.budget_summary.loc["Payroll Expenditures", 2016]

        self.non_payroll_operating_expenditures_by_year = self.budget_summary.loc["Non-Payroll Expenditures"]
        self.operating_costs = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year
