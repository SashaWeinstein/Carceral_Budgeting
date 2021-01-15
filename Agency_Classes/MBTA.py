import sys
import pandas as pd
cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPayroll" % cost_type_dir)
agency_helper_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory" \
                    "/Agency_Classes/Agency_Helpers"
sys.path.insert(0, agency_helper_dir)

from CY_To_FY import convert_CY_to_FY
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

    def get_expenditures_by_year(self):
        """MBTA has no non-payroll operating expenditures"""
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.non_hidden_fringe_by_year = pd.Series(index=self.year_range, data=0)



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

        self.payroll_by_year = convert_CY_to_FY(self.payroll_by_calendar_year.loc["police_pay"], self.year_range[2:])
        self.payroll_by_year[2016] = self.payroll_by_calendar_year.loc["police_pay", 2015]  # Missing data for 2016
        self.payroll_by_year[2017] = self.payroll_by_calendar_year.loc["police_pay", 2017]

    def get_police_pay(self, row):
        position = row["position_title"].lower()
        if "police" in position or "sergeant" in position:
            return row["pay_total_actual"]
        else:
            return 0