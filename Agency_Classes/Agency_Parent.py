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

    def __init__(self, alias, official_name, year_range, category, correction_function=lambda x: x):
        self.alias = alias
        self.official_name = official_name
        self.year_range = year_range
        self.calender_year_data = False
        self.requery = False
        self.category = category
        # Following two attr are from expenditures dataset
        self.payroll_expenditures_by_year = pd.Series(index=year_range, data=0)
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.correction_function = correction_function
        self.pensions = pd.Series(index=year_range, data=0)
        self.payroll_by_year = pd.Series(index=self.year_range, data=None)
        self.local_pensions = pd.Series(index=year_range, data=0)
        self.hidden_payroll = pd.Series(index=year_range, data=0)
        self.fringe = pd.Series(index=self.year_range, data=0)
        self.non_hidden_fringe = pd.Series(index=self.year_range, data=0)
        self.hidden_fringe = pd.Series(index=self.year_range, data=0)
        self.federal_expenditures_by_year = pd.Series(index=year_range,
                                                      data=0)
        self.non_hidden_capital_expenditures_by_year = pd.Series(index=year_range, data=0)
        self.hidden_capital_expenditures_by_year = pd.Series(index=year_range, data=0)
        self.capital_expenditures_by_year = pd.Series(index=year_range, data=0)
        assert category in ["Legal", "Jails", "Police",
                            "Other"], "Category for" + self.alias + "not an existing category"



    def API_call(self, client, dataset, SOQL_constructor):
        """Moved from StateAgency to Parent Agency class on July 2nd"""
        return client.get(dataset, where=SOQL_constructor(), limit=999999)

    def calculate_hidden_payroll(self):
        """Added Jan 14"""
        self.hidden_payroll = self.payroll_by_year - self.payroll_expenditures_by_year

    def get_final_costs(self, apply_correction=True, by_cost_type=False, split_hidden=False):
        """This is to be called in code that accesses the data anaylsis. Three options for the user
         1) Apply correction. Bobby has at certain points asked for statewide costs not limited to suffolk county
         2) Break out costs by cost type. Sometimes I want this, sometimes I just want final number
         3) Split payroll into payroll expenditures and hidden payroll """

        self.total_cost = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year + \
                          self.pensions + self.fringe + \
                          self.capital_expenditures_by_year

        if apply_correction:
            correction = self.correction_function
        else:
            correction = lambda x: x
        #Don't know why some costs aren't saved as floats. Fix during refactor
        """To do during refactor: currently setting by_cost_type equal to false doesn't doesnt get correct answer
        as it doesn't apply correct correction to TRC pensions. Need to get final cost regardless of whether user asks
        for answers by cost type, then add values to rv based on by_cost_tye/split_hidden
        """
        rv = []
        final_cost = correction(self.total_cost).astype(float)
        rv.append(final_cost)
        if by_cost_type:
            if split_hidden:
                #Split Payroll
                payroll_expenditures = correction(self.payroll_expenditures_by_year).astype(float)
                rv.append(payroll_expenditures)
                hidden_payroll = correction(self.hidden_payroll).astype(float)
                rv.append(hidden_payroll)

                #Split fringe
                non_hidden_fringe = correction(self.non_hidden_fringe)
                rv.append(non_hidden_fringe)
                hidden_fringe = correction(self.hidden_fringe)
                rv.append(hidden_fringe)

                #Split Capital costs
                non_hidden_capital = correction(self.non_hidden_capital_expenditures_by_year)
                rv.append(non_hidden_capital)
                hidden_capital = correction(self.hidden_capital_expenditures_by_year)
                rv.append(hidden_capital)

            else:
                final_payroll = correction(self.payroll_by_year).astype(float)
                rv.append(final_payroll)
                final_fringe = correction(self.fringe).astype(float)
                rv.append(final_fringe)
                final_capital = correction(self.capital_expenditures_by_year).astype(float)
                rv.append(final_capital)
            final_non_payroll_operating = correction(self.non_payroll_operating_expenditures_by_year).astype(float)
            rv.append(final_non_payroll_operating)
            final_pensions = self.pension_correction(apply_correction, correction).astype(float) #This uses pension correction function as TRC has seperate correction
            rv.append(final_pensions)


        return rv

    def __repr__(self):
        return "Agency object for " + self.alias