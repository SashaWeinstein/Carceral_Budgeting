import pandas as pd
from MBTA_Payroll_Scraper import scrape_payroll


from State_Agency import StateAgency
from Pensions_Final import pensions_from_payroll_fraction

class MBTA(StateAgency):
    """Giving MBTA Police it's own class because code I use to generate it's numbers is different enough"""

    def __init__(self, alias, official_name, year_range, category, client, correction_function=None):
        #Jank but if works for know then points in correct direction for later
        StateAgency.__init__(self, alias, official_name, year_range, category,
                             payroll_vendors=[],
                             payroll_official_name='Massachusetts Bay Transportation Authority (MBT)',
                             client=client, correction_function=correction_function, pension_function=pensions_from_payroll_fraction)
        self.payroll_by_year = pd.Series(index=self.year_range, data=0)
        self.payroll_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.get_final_costs()

    def get_expenditures_by_year(self):
        """MBTA has no non-payroll operating expenditures"""
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.non_hidden_fringe_by_year = pd.Series(index=self.year_range, data=0)

    def get_final_costs(self, apply_correction=True, add_hidden_costs=False, pensions_statewide=None):
        """Janky to pass pensions_statewide df but never use it, but I'm up against deadline today """
        if self.payroll_by_year.sum() == 0:
            self.add_payroll_by_year()

        #For refactor: need to assign this to be zero or something
        # self.payroll_expenditures_by_year = self.operating_costs

        #Following is duplicated code
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=list(range(2016, 2020)), data=0)
        final = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year \
                + self.pensions + self.fringe + self.capital_expenditures_by_year
        return self.correction_function(final)

    def add_payroll_by_year(self):
        """This is combination of cthru and budget pdf I found online at
        https://www.mbta.com/financials/mbta-budget"""
        self.add_payroll(True)
        self.payroll["police_pay"] = self.payroll.apply(lambda x: self.get_police_pay(x),
                                                        axis=1)
        self.payroll_by_calendar_year = self.payroll.groupby("year").agg(
            {"pay_total_actual": "sum", "police_pay": "sum"}).T
        scraped = scrape_payroll('data/MBTA_pdfs/Scraper_Results_Dec20.json', False)
        for y in [2015, 2017]:
            self.payroll_by_calendar_year.loc["pay_total_actual", y] = scraped[y]["total_pay_actual"]
            self.payroll_by_calendar_year.loc["police_pay", y] = scraped[y]["police_pay"]
        self.payroll_by_year[2016] = self.payroll_by_calendar_year.loc["police_pay", 2015]  # Missing data for 2016
        self.payroll_by_year[2017] = self.payroll_by_calendar_year.loc["police_pay", 2017]

        for y in self.year_range[2:]:
            self.payroll_by_year.loc[y] = .5 * self.payroll_by_calendar_year.loc["police_pay", y - 1] + \
                                          .5 * self.payroll_by_calendar_year.loc["police_pay", y]

    def get_police_pay(self, row):
        position = row["position_title"].lower()
        if "police" in position or "sergeant" in position:
            return row["pay_total_actual"]
        else:
            return 0