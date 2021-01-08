"""
Boston PD class was given it's own file Dec 29
"""
import pandas as pd

from Agency_Classes_Big import PoliceDepartment

from LocalPD_External_Funds import BostonPD_External_Funds
from BostonPD_Non_Payroll_Operating import get_BostonPD_Non_Payroll_Operating
from BostonPD_Capital import get_BostonPD_Capital_Costs
from LocalPD_Pensions import BostonPD_Pensions
from LocalPD_Fringe import BostonPD_Fringe
from LocalPD_True_Payroll import True_Earnings


class BostonPD(PoliceDepartment):
    """"""

    def __init__(self, yr):
        PoliceDepartment.__init__(self, "Boston PD", "Boston PD", yr)
        print("got to init of boston PD")
        self.federal_expenditures_by_year = BostonPD_External_Funds()  # New August 14th

        self.non_payroll_operating_expenditures_by_year, self.fraction_all_federal, self.non_hidden_fringe = \
            get_BostonPD_Non_Payroll_Operating(self)
        self.add_true_earnings()
        self.pensions = BostonPD_Pensions(self)
        self.fringe = BostonPD_Fringe(self) + self.non_hidden_fringe
        self.capital_expenditures_by_year = get_BostonPD_Capital_Costs()


    def add_true_earnings(self):
        """New July 30th. Replace expenditure numbers 2016-2019 with true earnings
        Note that for 2016 for chelsea we don't have actual payroll so I will use rough estimation, need better
         way to fix later"""
        print("got to add true earnings method of BPD class")
        total_earnings, self.PD_fraction_non_teacher, self.PD_fraction_total, PD_payroll = True_Earnings(self.alias)
        self.payroll = PD_payroll
        self.payroll_by_year = total_earnings * (1-self.fraction_all_federal)