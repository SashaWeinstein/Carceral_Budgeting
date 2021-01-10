import pandas as pd
import sys
import os

#For refactor: have to clean this up, don't want to import both places
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/pensions")
# from Statewide_Pensions import pensions_by_agency


exploratory_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"
data_dir_path = "%sdata/" % exploratory_dir

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)

# pensions_statewide, contributions_by_year = pensions_by_agency(False)


class Agency():
    """For keeping track of info associated with a government agency
    New July 17th: category attribute. I'm grouping the agencies into three categories:
    Legal which includes trial court, SCDAO, CPCS, DAAA
    Jails which is DOC, sheriff
    Cops which is state, local police
    New July 21st: correction function which corrects based on fact that state agencies spend a
    certain % of their budget on suffolk county
    Eventually each type should go here"""

    def __init__(self, alias, official_name, year_range, category, correction_function=None):
        self.alias = alias
        self.official_name = official_name
        self.year_range = year_range
        self.calender_year_data = False
        self.requery = False
        self.category = category
        # Following two attr are from expenditures dataset
        self.payroll_expenditures_by_year = None
        self.true_payroll_by_year = None  # Work on this next
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        if correction_function:
            self.correction_function = correction_function
        else:
            self.correction_function = lambda x: x
        self.pensions = pd.Series(index=year_range, data=0)
        self.local_pensions = pd.Series(index=year_range, data=0)

        self.fringe = pd.Series(index=self.year_range, data=0)
        self.federal_expenditures_by_year = pd.Series(index=list(range(2016, 2020)),
                                                      data=0)  # needs fix: have to use range here cause some police year ranges aren't 2016-2020. Have to fix that then can use self.year_range

        self.capital_expenditures_by_year = pd.Series(index=year_range, data=0)
        assert category in ["Legal", "Jails", "Police",
                            "Other"], "Category for" + self.alias + "not an existing category"



    def API_call(self, client, dataset, SOQL_constructor):
        """Moved from StateAgency to Parent Agency class on July 2nd"""
        return client.get(dataset, where=SOQL_constructor(), limit=999999)

    def clean_labels(self, df):
        """Written by Sasha on June 22nd to clean row labels so they look nice
        To do: send all word to uppercase except acronyms"""
        df.index = [i.replace("_", " ") for i in df.index]

    def to_float(self):
        """Written July 8th"""
        self.budget_summary = self.budget_summary.applymap(lambda x: float(x.replace(",", "")) if type(x) == str else x)
        self.budget_summary.fillna(0, inplace=True)

    def __repr__(self):
        return "Agency object for " + self.alias