import pandas as pd
import sys
import os

#For refactor: have to clean this up, don't want to import both places
from Statewide_Pensions import pensions_by_agency
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/pensions")


exploratory_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"
data_dir_path = "%sdata/" % exploratory_dir

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)

pensions_statewide, contributions_by_year = pensions_by_agency(False)


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
        self.local_pensions = pd.Series(index=self.year_range, data=0)  # New Dec 22
        #To do during big refactor: this should go in it's own method for symmetry's sake
        if self.alias in pensions_statewide.index or self.alias == "trial_court":
            #To do during refator: this should go in separate trial court class
            if self.alias == "trial_court":
                self.pensions = pensions_statewide.loc["trial_court_statewide", self.year_range]
                self.local_pensions = pensions_statewide.loc["trial_court_local", self.year_range]
            elif self.alias =="Suffolk_Sheriff":
                # To-do: move this to sheriff object
                """Added august 12th to account for City of Boston's obligations to retirees of suffolk sheriff's office. From
                    Boston state budget:
                         State legislation converted all existing and future Suffolk County Sheriff employees to state employees
                         effective January 1, 2010. The State charges the City for Suffolk County through an assessment based on the
                        residual unfunded pension liability for former Sherriff employees who retired prior to January 1, 2010.
                        Once the unfunded pension liability is fully extinguished, the budget for Suffolk County
                        will no longer be necessary.
                """
                self.pensions = pensions_statewide.loc[self.alias, self.year_range] + 3.87*(10**6)

            else:
                self.pensions = pensions_statewide.loc[self.alias, self.year_range]
        else:
            self.pensions = pd.Series(index=self.year_range, data=0)
        self.fringe = pd.Series(index=self.year_range, data=0)
        self.federal_expenditures_by_year = pd.Series(index=list(range(2016, 2020)),
                                                      data=0)  # needs fix: have to use range here cause some police year ranges aren't 2016-2020. Have to fix that then can use self.year_range
        self.final_cost = pd.Series(
            index=list(range(2016, 2020)))  # Not fully implemented yet, just works for state agencies
        self.capital_expenditures = None  # New August 19th
        assert category in ["Legal", "Jails", "Police",
                            "Other"], "Category for" + self.alias + "not an existing category"

    def find_data(self, file_name, client, dataset, SOQL_constructor=None):
        """Last updated July 9th to allow for re-querying and overwriting csv's
        Look for matching csv in data directory, if it's there not fetch it from API
        file_name is generated from agency, dataset
        client is Socrata object
        dataset is name of dataset in cthru system"""
        file_path = data_dir_path + file_name
        if not self.requery and os.path.exists(file_path):
            df = pd.read_csv(file_path)
        else:
            result_json = self.API_call(client=client, dataset=dataset,
                                        SOQL_constructor=SOQL_constructor)  # State and Municipal Agencies have different API calls
            df = pd.DataFrame(result_json)
            assert df.shape[0] < 999999, "Dataset found with more than 999999 records, need to up limit"
            df.to_csv(file_path)
        return df

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