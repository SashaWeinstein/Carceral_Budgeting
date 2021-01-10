"""CPCS got it's own file Dec 29th"""

from State_Agency import StateAgency


class CPCS(StateAgency):
    """CPCS needs it's own class as it's R24 dollars are counted towards payroll instead of operating costs"""
    def __init__(self, alias, official_name, year_range, payroll_vendors, category, client, correction_function,
                 settlement_agencies):
        StateAgency.__init__(self, alias, official_name, year_range, category, correction_function, settlement_agencies,
                             payroll_vendors, None, client, remove_R24 = True)
        self.payroll_by_year = self.payroll_by_year + self.R24_by_year

    def remove_R24_expenditures(self):
        """Only used for CPCS"""
        self.R24 = self.expenditures[(self.expenditures["object_code"] == "(R24) PUBLIC COUNSEL") &
                                     (self.expenditures["vendor"].str.contains("(?i)payroll") == False)]
        self.expenditures = self.expenditures[self.expenditures["object_code"] != "(R24) PUBLIC COUNSEL"]
        self.R24_by_year = self.R24.groupby("budget_fiscal_year").sum()["amount"].loc[self.year_range]

