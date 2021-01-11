import pandas as pd

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


    def get_final_costs(self, apply_correction=True, by_cost_type=False):
        """This is to be called in code that accesses the data anaylsis. Two options for the user
         1) Apply correction. Bobby has at certain points asked for statewide costs not limited to suffolk county
         2) Break out costs by cost type. Sometimes I want this, sometimes I just want final number"""

        self.total_cost = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year + \
                          self.pensions + self.fringe + \
                          self.capital_expenditures_by_year

        if apply_correction:
            correction = self.correction_function
        else:
            correction = lambda x: x

        #Don't know why some costs aren't saved as floats. Fix during refactor
        final_cost = correction(self.total_cost).astype(float)
        final_payroll = correction(self.payroll_by_year).astype(float)
        final_non_payroll_operating = correction(self.non_payroll_operating_expenditures_by_year).astype(float)
        final_pensions = self.pension_correction(apply_correction, correction).astype(float) #This has seperate method because TRC class overwrites
        final_fringe = correction(self.fringe).astype(float)
        final_capital = correction(self.capital_expenditures_by_year).astype(float)

        if by_cost_type:
            return final_cost, final_payroll, final_non_payroll_operating, final_pensions, final_fringe, final_capital
        else:
            return final_cost

    def __repr__(self):
        return "Agency object for " + self.alias