"""Version 2 Created by Sasha Oct 27th
New in version 2:
Change methodology in how cthru expenditures are split into payroll, non-payroll. Use vendor instead of object class
"""
import pandas as pd
import numpy as np
from sodapy import Socrata
from PyPDF2 import PdfFileReader, PdfFileWriter
import requests
import textract
import difflib
import re
import os
import sys

sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/pensions")
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/fringe")
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/pdf_scraper")
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"
                   "capital_costs")
from State_Pensions_2Ver import by_agency
from LocalPD_True_Payroll import True_Earnings
from MBTA_Payroll_Scraper import scrape_payroll
from Local_PD_Pensions import BostonPD_Pensions, ChelseaPD_Pensions, ReverePD_Pensions, WinthropPD_Pensions_Benefits
from Local_PD_Fringe_Benefits import BostonPD_Fringe, ChelseaPD_Fringe, ReverePD_Fringe
from Statewide_Fringe import Total_Statewide_Payroll, Total_Statewide_Fringe
from LocalPD_External_Funds import BostonPD_External_Funds_Correction
from DCP_Capital import get_capital_expenditures
from ReverePD_Capital_Costs import get_ReverePD_Capital_Costs

data_dir_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"
saved_scraped_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory" \
                     "/data/Scraped_Saved/"

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

pensions_statewide = by_agency(False)
total_statewide_payroll = Total_Statewide_Payroll(client)
total_statewide_fringe = Total_Statewide_Fringe(client)
DCP_capital_expenditures = get_capital_expenditures(client)


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
        self.true_payroll_by_year = None #Work on this next 
        self.non_payroll_operating_expenditures_by_year = None
        if correction_function:
            self.correction_function = correction_function
        else:
            self.correction_function = lambda x: x
        if self.alias in pensions_statewide.index:
            self.pensions = pensions_statewide.loc[self.alias, self.year_range]
        else:
            self.pensions = pd.Series(index=self.year_range, data=0)
        self.fringe = pd.Series(index=self.year_range, data=0)
        self.capital_costs = pd.Series(index=self.year_range, data=0)
        self.federal_expenditures_by_year = pd.Series(index=list(range(2016,2020)), data=0) # needs fix: have to use range here cause some police year ranges aren't 2016-2020. Have to fix that then can use self.year_range
        self.final_cost = pd.Series(index=list(range(2016,2020))) # Not fully implemented yet, just works for state agencies
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


class StateAgency(Agency):
    """Last updated July 10th to get revenue data into it's own dataframe
    Possible to do: return one summary dataframe instead of expenditures, budget, revenue by year
    Another to do: add client in initialize agencies code
    To do: fix how year range is set, it's getting passed from multiple places and creating conflicts
    Really, really need to fix this it's causing lots of bugs. Need to set year range from one place, when
    agency class is created, and have it all propogate
    Also: something strange is happending where once initialize agencies has been run and then I call it agian,
    the objects aren't re-initialized. Should figure out what is going on
    Actually, objects are getting intialized when I import initialize agencies, which isn't what I want."""

    def __init__(self, alias, official_name, year_range, category, correction_function=None, settlement_agencies=None,
                 payroll_vendors=[], payroll_official_name=None, client=None):
        Agency.__init__(self, alias, official_name, year_range, category, correction_function)
        self.client = client
        self.payroll_official_name = payroll_official_name  # MBTA is lowercase in payroll system for some reason
        self.payroll_vendors = payroll_vendors  # Should be a list of vendors.
        self.settlement_agencies = settlement_agencies
        self.expenditures = None
        self.capital_expenditures_by_year = pd.Series(index=self.year_range, data=0)
        self.non_hidden_fringe = pd.DataFrame()  # New Nov 9th
        self.non_hidden_fringe_by_year = pd.Series(index=self.year_range, data=0)
        self.calender_year_data = True  # New June 24th
        self.payroll = None  # New on June 22nd
        self.payroll_by_year = pd.Series(index=self.year_range, data=None)
        self.pay_col = None  # List of column names to keep and sum payroll info over
        self.official_budget_name = self.official_name.split("(")[0][:-1]  # Name in budget data in fmz7-6ft9
        self.budget = None
        self.budget_cols = ["beginning_balance_prior", "original_enacted_budget", "total_enacted_budget",
                            "transfer_in", "transfer_out",
                            "supplemental_budget", "total_available_for_spending",
                            "planned_savings_9c_spending", "total_expenses",
                            "retained_revenue_collected"]
        self.expenditures_by_year = pd.DataFrame(columns=self.year_range)
        self.budget_by_year = pd.DataFrame(columns=self.year_range)
        self.operating_costs = None  # This is where cost type "operating costs" will be stored


        self.final_costs_calculated = False
        self.get_final_costs()

    def get_final_costs(self, apply_correction=True):
        """Created August 12 for new methodology where we use expenditures for everything"""
        if not self.final_costs_calculated:
            self.final_costs_calculated = True
            self.get_expenditures_by_year()
            self.add_settlements()
            self.add_payroll_by_year()
            self.add_fringe()

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


    def add_expenditures(self, client):
        """Adds expenditures for agency over the given year range
        Uses this dataset https://cthru.data.socrata.com/dataset/Comptroller-of-the-Commonwealth-Spending/pegc-naaa
        client is Socrata object
        year_range is list of years to do analysis over
        Do to: pull out spending on fringe benefits and put that in benefit series
        """
        file_name = self.alias + "_expenditures.csv"
        self.expenditures = self.find_data(file_name, client, "pegc-naaa", self.construct_expenditures_SOQL)
        self.expenditures["amount"] = self.expenditures["amount"].astype(float)
        self.expenditures["budget_fiscal_year"] = self.expenditures["budget_fiscal_year"].astype(int)
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"].str.contains("INTRAGOVERNMENTAL") == False]
        self.federal_expenditures = self.expenditures[self.expenditures["appropriation_type"].str.contains("FEDERAL")]
        self.federal_expenditures_by_year = self.federal_expenditures.groupby("budget_fiscal_year").sum()["amount"].T
        self.federal_expenditures_by_year = self.federal_expenditures_by_year.reindex(self.year_range, fill_value=0)
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"].str.contains("FEDERAL") == False]
        self.capital_expenditures = self.expenditures[self.expenditures["appropriation_type"] == "(2CN) CAPITAL"]
        self.capital_expenditures_by_year = self.capital_expenditures.groupby("budget_fiscal_year").sum()["amount"].T
        self.capital_expenditures_by_year = self.capital_expenditures_by_year.reindex(self.year_range, fill_value=0)
        self.expenditures = self.expenditures[self.expenditures["appropriation_type"] != "(2CN) CAPITAL"]
        self.non_hidden_fringe = self.expenditures[self.expenditures["object_class"] == "(DD) PENSION & INSURANCE RELATED EX"]
        self.expenditures = self.expenditures[self.expenditures["object_class"]!="(DD) PENSION & INSURANCE RELATED EX"]

    def get_expenditures_payroll(self):
        assert type(self.expenditures) == pd.core.frame.DataFrame, \
            "get payroll called before expenditures data assigned"
        self.expenditures["payroll_amount"] = self.expenditures[self.expenditures["vendor"].isin(self.payroll_vendors)] \
            ["amount"]
        self.expenditures["payroll_amount"].fillna(0, inplace=True)

    def get_expenditures_by_year(self):
        """Written by Sasha on June 24th to take code that was in Exploratory Main"""
        self.add_expenditures(self.client)
        self.get_expenditures_payroll()
        payroll_expenditures = self.expenditures[self.expenditures["vendor"].str.contains("(?i)payroll")]
        non_payroll_expenditures = self.expenditures[self.expenditures["vendor"].str.contains("(?i)payroll")==False]
        assert np.isclose(payroll_expenditures["amount"].sum() + non_payroll_expenditures["amount"].sum(),
               self.expenditures["amount"].sum())
        self.expenditures_by_year = self.expenditures.groupby("budget_fiscal_year").agg({"amount": "sum",
                                                                                         "payroll_amount": "sum"}).T
        self.expenditures_by_year.rename(index={"amount": "Total Expenditures",
                                                "payroll_amount": "Payroll Expenditures"}, inplace=True)
        self.expenditures_by_year = self.expenditures_by_year.loc[:, self.year_range]

        self.payroll_expenditures_by_year = payroll_expenditures.groupby("budget_fiscal_year").sum()["amount"].loc[list(range(2016, 2020))]
        self.non_payroll_operating_expenditures_by_year = non_payroll_expenditures. \
            groupby("budget_fiscal_year").sum()["amount"].loc[list(range(2016, 2020))]


    def get_possible_pension_spending(self):
        """Written July 17th to help me figure out if pension spending is already in this dataset"""
        self.expenditures_by_year.loc["Object Class Mentions \"Pension\""] = \
            self.expenditures[self.groupby("budget_fiscal_year") \
                .agg({"amount": "sum"})]

    def add_payroll(self, total_OT_only=False):
        """Created by Sasha on June 22nd to get payroll data from cthru endpoint
        Dataset is here https://cthru.data.socrata.com/dataset/Commonwealth-Of-Massachusetts-Payrollv2/rxhc-k6iz
        client is Socrata object
        year_range is list of years to get data for
        New July 6th: total_OT_only is bool for whether we want all pay categories or just OT, total payroll
        """
        file_name = self.alias + "_payroll.csv"
        self.payroll = self.find_data(file_name, self.client, "rxhc-k6iz", self.construct_payroll_SOQL)
        assert not self.payroll.empty, "no payroll info found for " + self.alias
        if total_OT_only:
            self.pay_col = ["pay_total_actual", "pay_overtime_actual"]
        else:
            self.pay_col = [i for i in self.payroll.columns if i[:3] == "pay"]
        self.payroll[self.pay_col] = self.payroll[self.pay_col].astype(float)
        self.payroll.loc[:, "year"] = self.payroll.loc[:, "year"].astype(int)

    def add_payroll_by_year(self, total_OT_only=False):
        """Written by Sasha on June 24th to take code from exploratory main"""
        self.add_payroll(total_OT_only)
        payroll_by_calendar_year = self.payroll.groupby("year")[self.pay_col].sum().T
        for y in self.year_range:
            self.payroll_by_year[y] = .5*payroll_by_calendar_year.loc["pay_total_actual", y-1] + \
                                      .5*payroll_by_calendar_year.loc["pay_total_actual", y]


    def add_budget(self):
        """Created by Sasha on June 22nd
        Connects to API for
        https://cthru.data.socrata.com/dataset/Budget_Actual_With_Other_Spending_Authorizationv3/fmz7-6ft9"""
        file_name = self.alias + "_budget.csv"
        self.budget = self.find_data(file_name, self.client, "fmz7-6ft9", self.construct_budget_SOQL)
        assert not self.budget.empty, "no budget info found for " + self.alias
        self.budget[self.budget_cols] = self.budget[self.budget_cols].astype(float)

    def add_budget_by_year(self):
        """New July 10th to get revenues too"""
        self.add_budget()
        self.budget_by_year = self.budget.groupby("fiscal_year")[self.budget_cols].sum().T
        self.budget_by_year.columns = [int(x) for x in self.budget_by_year.columns]

        self.budget_by_year = self.budget_by_year.loc[:, self.year_range]
        self.clean_labels(self.budget_by_year)

    def appropriations_rev_9c(self):
        """Written on July 14th to calculate row for each agency that is
        total enacted spending + total revenues - 9c for this week's investigation of where extra money for
        'total available for spending' comes from"""
        self.budget_by_year.loc["All Appropriations Plus Revenues Minus 9c"] = \
            self.budget_by_year.loc[["total enacted budget", "retained revenue collected"], :].sum() - \
            self.budget_by_year.loc["planned savings 9c spending"]

    def add_settlements(self):
        """New August 10th to get settlement data from cthru"""
        self.settlements = pd.Series(index=self.year_range, data=[0] * len(self.year_range))
        if self.settlement_agencies:
            file_name = self.alias + "_settlements.csv"
            settlements_overall = self.find_data(file_name, self.client, "6j38-k6fr", self.construct_settlements_SOQL)
            settlements_overall["line_amount"] = settlements_overall["line_amount"].astype(float)
            self.settlements = pd.Series(index=self.year_range, data=[0] * len(self.year_range))
            self.settlements = self.settlements + settlements_overall.groupby("bfy").sum()["line_amount"]
            self.settlements = self.settlements.loc[self.year_range].fillna(0)

    def add_fringe(self):
        """New August 14th, at this point only gets health insurance from GIC"""
        if self.payroll_by_year.empty: #This is the sort of code that should come out, I should just call payroll by year beforehand
            self.add_payroll_by_year()
        pcnt_by_year = self.payroll_by_year / total_statewide_payroll
        self.non_hidden_fringe_by_year = self.non_hidden_fringe.groupby("budget_fiscal_year").sum()["amount"].T
        self.non_hidden_fringe_by_year = self.non_hidden_fringe_by_year.reindex(self.year_range, fill_value=0)
        hidden_fringe = pcnt_by_year * total_statewide_fringe
        self.fringe = hidden_fringe.loc[self.year_range] + self.non_hidden_fringe_by_year

    def construct_expenditures_SOQL(self):
        return "Department = '" + self.official_name + "' AND budget_fiscal_year >= 2016"

    def construct_payroll_SOQL(self):
        """Created by Sasha on June 22nd"""
        if self.payroll_official_name is not None:
            official_name = self.payroll_official_name
        else:
            official_name = self.official_name
        return "department_division = '" + official_name + "' AND Year >= " + str(self.year_range[0]-1) + \
               "AND Year <= " + str(self.year_range[-1])

    def construct_budget_SOQL(self):
        """Updated on July 14th to not filter based on year range attribute, because year range should be changed
        without having to requery. Instead hardcode in 2016"""
        return "department_name = '" + self.official_budget_name + "' AND fiscal_year >= 2016"

    def construct_settlements_SOQL(self):
        """New August 10th"""
        SOQL = "("
        for a in self.settlement_agencies:
            SOQL += "dept_paid_on_behalf_of = '" + self.settlement_agencies[0] + "' OR "
        SOQL = SOQL[:-4] + ") AND bfy >= " + str(self.year_range[0])
        return SOQL


class MBTA(StateAgency):
    """Giving MBTA Police it's own class because code I use to generate it's numbers is different enough"""

    def __init__(self, alias, official_name, year_range, category, client, correction_function=None):
        StateAgency.__init__(self, alias, official_name, year_range, category,
                             payroll_vendors=[],
                             payroll_official_name='Massachusetts Bay Transportation Authority (MBT)',
                             client=client, correction_function=correction_function)
        self.payroll_by_year = pd.Series(index=self.year_range, data=0)
        self.payroll_expenditures_by_year = pd.Series(index=self.year_range, data= 0)

    def get_final_costs(self, apply_correction=True, add_hidden_costs=False, pensions_statewide=None):
        """Janky to pass pensions_statewide df but never use it, but I'm up against deadline today """
        if self.payroll_by_year.sum() == 0:
            self.add_payroll_by_year()

        self.payroll_expenditures_by_year = self.operating_costs
        self.non_payroll_operating_expenditures_by_year = pd.Series(index=list(range(2016, 2020)), data=0)
        final = self.payroll_by_year +self.non_payroll_operating_expenditures_by_year \
                + self.pensions + self.fringe + self.capital_expenditures_by_year
        return self.correction_function(final)

    def add_payroll_by_year(self):
        """This is combination of cthru and budget pdf I found online at
        https://www.mbta.com/financials/mbta-budget"""
        self.add_payroll(True)
        self.payroll["police_pay"] = self.payroll.apply(lambda x: self.get_police_pay(x),
                                                        axis=1)
        self.payroll_by_calendar_year = self.payroll.groupby("year").agg({"pay_total_actual": "sum", "police_pay": "sum"}).T
        scraped = scrape_payroll('data/MBTA_pdfs/Payroll_Result_Jul21.json')
        for y in ["2015", "2017"]:
            self.payroll_by_calendar_year.loc["pay_total_actual", int(y)] = scraped[y]["total_pay_actual"]
            self.payroll_by_calendar_year.loc["police_pay", int(y)] = scraped[y]["police_pay"]
        self.payroll_by_year[2016] = self.payroll_by_calendar_year.loc["police_pay", 2015] #Missing data for 2016
        self.payroll_by_year[2017] = self.payroll_by_calendar_year.loc["police_pay", 2017]
        for y in self.year_range[2:]:
            self.payroll_by_year.loc[y] = .5*self.payroll_by_calendar_year.loc["police_pay", y-1] +\
                                          .5*self.payroll_by_calendar_year.loc["police_pay", y]


    def get_police_pay(self, row):
        if "police" in row["position_title"].lower():
            return row["pay_total_actual"]
        else:
            return 0


class PoliceDepartment(Agency):
    """New July 7th
    To do: code where you iterate through pages until you've found mission can be moved here"""

    def __init__(self, alias, official_name, year_range):
        Agency.__init__(self, alias, official_name, year_range, "Police")
        self.capital_expenditures_by_year = pd.Series(index=list(range(2016, 2020)), data=0)
        self.operating_costs = pd.Series(index=year_range, data=0)
        self.correction_function = lambda x: x

    def text_from_pdf(self, path):
        """Written on July 1st originally to be used for Boston and Winthrop PD"""
        pdf_path = path + ".pdf"
        text_path = path + ".txt"
        if os.path.exists(text_path):
            with open(text_path, "r") as budget:
                full_text = budget.read()
        else:
            full_text = str(textract.process(pdf_path, method="tesseract", language="eng")).replace("\\n", " ")
            with open(text_path, "w+") as budget:
                budget.write(full_text)
        return full_text

    def match_mission(self, mission, page):
        """Moved to parent Agency class on July 1st to allow mission statement to vary slightly
         Updated July 6th to return matching text for debug"""
        for i in range(len(page) - len(mission)):
            if difflib.get_close_matches(mission, [page[i:i + len(mission)]], n=1):
                return [page[i:i + len(mission)]]
        return None

    def bp_to_list(self, bp, line_item, line_item_len=None):
        """New July 16th: convert to integers in this function. Should get in habit of converting to integers as
        soon as I scrape stuff"""
        if line_item_len is None:
            line_item_len = len(line_item)
        line_item_start = re.search(line_item, bp)
        bp = bp[line_item_start.start() + line_item_len:]
        line_item_end = re.search("[A-Za-z]", bp)
        if line_item_end:
            final = bp[:line_item_end.end()]
        else:
            final = bp
        return [float(x.replace(",", "")) for x in final.split(" ")
                if x and x.replace(",", "").replace(".", "").isnumeric()]

    def get_dollar_amounts_payroll(self, bp, total_payroll_line_item):
        """Written by Sasha July 1st to get payroll from Boston PD
        Should use new bp_to_list eventually
        May be depcreciated if bp_to_list is all I need"""

        return self.bp_to_list(bp, "vertime"), self.bp_to_list(bp, total_payroll_line_item)

    def Add_True_Earnings(self):
        """New July 30th. Replace expenditure numbers 2016-2019 with true earnings
        Note that for 2016 for chelsea we don't have actual payroll so I will use rough estimation, need better
         way to fix later"""
        total_earnings, PD_fraction_non_teacher, PD_fraction_total, PD_payroll = True_Earnings(self.alias)
        if 2016 not in PD_fraction_non_teacher.index:
            PD_fraction_non_teacher[2016] = PD_fraction_non_teacher[2017] - \
                                            (PD_fraction_non_teacher[2018] - PD_fraction_non_teacher[2017])
        self.pensions = self.add_pension_costs(PD_fraction_non_teacher)
        self.fringe = self.add_fringe_benefits(PD_fraction_total)
        self.payroll = PD_payroll
        self.payroll_by_year = total_earnings
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Expenditures", list(range(2016,2020))] # Need to fix year range
        if self.alias == "Chelsea PD":
            self.payroll_by_year[2016] = self.budget_summary.loc["Payroll Budget", 2016]
            self.payroll_expenditures_by_year[2016] = self.budget_summary.loc["Payroll Budget", 2016]
        self.non_payroll_operating_expenditures_by_year = self.budget_summary.loc["Total Expenditures"] - \
                                                  self.budget_summary.loc["Payroll Expenditures"]
        self.non_payroll_operating_expenditures_by_year = \
            self.non_payroll_operating_expenditures_by_year.loc[list(range(2016, 2020))]
        self.operating_costs = self.payroll_by_year + self.non_payroll_operating_expenditures_by_year

    def scrape(self):
        file_path = saved_scraped_path + self.alias + ".csv"

        if os.path.exists(file_path):
            self.budget_summary = pd.read_csv(file_path, index_col=0)
            self.budget_summary.columns = [int(x) for x in self.budget_summary.columns]
            if self.alias in ["Boston PD", "Chelsea PD"]:
                self.capital_expenditures_by_year = pd.read_json(saved_scraped_path+self.alias+"_capital_expenditures.json",
                                                         typ='series', orient='records')
        else:
            self.from_PDF()
            self.budget_summary.to_csv(file_path)
            if self.alias in ["Boston PD", "Chelsea PD"]:
                self.capital_expenditures_by_year.to_json(saved_scraped_path+self.alias+"_capital_expenditures.json")

    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Pensions_statewide shouldn't be passed in, better solution should be found but I'm up against deadline"""

        return self.operating_costs + self.pensions + self.fringe + self.capital_expenditures_by_year

    def add_budget_by_year(self, client=None):
        """Last updated by August 3rd"""
        pass


class BostonPD(PoliceDepartment):
    """Last updated July 16th to get capital projects, external funds.
    There's no single number that combines operating budget, external funds, and capital budget so I'll have to add
    them myself. I'll know I did it right if my numbers match vera's"""

    def __init__(self, url_dict=None):
        year_range = list(range(2016, 2022))
        big_range = list(range(2010, 2022))  # New July 16th
        PoliceDepartment.__init__(self, "Boston PD", "Boston PD", year_range)
        self.url_dict = url_dict  # Maps dataset alias to API url
        self.operating_budget = None  # From API
        self.mission = "The mission of the Police Department is Neighborhood Policing"
        self.federal_expenditures_by_year = BostonPD_External_Funds_Correction().iloc[0,:]  # New August 14th
        self.add_pension_costs = BostonPD_Pensions
        self.add_fringe_benefits = BostonPD_Fringe
        if self.url_dict:
            self.add_operating_budget()
        self.budget_summary = pd.DataFrame(columns=big_range, index=["Payroll Budget",
                                                                     "OT Budget",
                                                                     "Total Budget",
                                                                     "Payroll Appropriation",
                                                                     "OT Appropriation",
                                                                     "Total Appropriation",
                                                                     "Payroll Expenditures",
                                                                     "OT Expenditures",
                                                                     "Total Expenditures"]).fillna(0)
        self.scrape()
        self.Add_True_Earnings()
        self.get_final_costs()


    def from_PDF(self):
        """Last updated July 16th to pare down final budget summary df in a more clear way. To do: take out to_float()
        because I convert to float in bp_to_list now"""
        payroll_signifier = "51000 Permanent Employees"
        for y in [2016, 2017, 2020, 2021]:
            pdf_path = data_dir_path + "bostonPD/boston_FY" + str(y)[2:] + ".pdf"
            self.PDF_scraper_extractable(y, pdf_path, payroll_signifier)
        for y in [2018, 2019]:
            path = data_dir_path + "bostonPD/boston_FY" + str(y)[2:]
            self.PDF_scraper_non_extractable(y, path, payroll_signifier)
        self.budget_summary = self.budget_summary.loc[:, self.year_range]
        self.to_float()  # Probably don't need this, should take it out eventually

    def PDF_scraper_extractable(self, year, path, payroll_signifier):
        """Written by Sasha on June 29th to get data from a particular pdf and get it budget summary df
        As of July 2nd: added 2021 budget, otherwise seems clean"""
        budget_obj = PdfFileReader(path)
        overall_found = False
        PD_section = False
        external = False
        correction = None
        for i in range(budget_obj.getNumPages()):
            if "/Contents" in budget_obj.getPage(i).keys() and \
                    self.match_mission(self.mission, budget_obj.getPage(i).extractText()) is not None:
                PD_section = True
            # if PD_section and not overall_found and "Operating Budget" in budget_obj.getPage(i).extractText():
            #     bp = budget_obj.getPage(i).extractText().replace("\n", " ")
            #     dollar_amounts_overall = self.bp_to_list(bp, "Total\s+\d+", 5)
            #     self.update_budget_summary(year, dollar_amounts_overall, "Overall")
            #     overall_found = True
            if PD_section and payroll_signifier in budget_obj.getPage(i).extractText():
                bp = budget_obj.getPage(i).extractText().replace("\n", " ")
                total_dollar_amounts = self.bp_to_list(bp, "Grand Total")
                if external and year - 2 in self.federal_expenditures.index:
                    correction = 1 - self.federal_expenditures.loc[year - 2] / total_dollar_amounts[1]
                self.update_budget_summary(year, total_dollar_amounts, "Overall", correction)
                OT_dollar_amounts = self.bp_to_list(bp, "vertime")
                self.update_budget_summary(year, OT_dollar_amounts, "OT", correction)
                payroll_dollar_amounts = self.bp_to_list(bp, "Total Personnel Services")
                self.update_budget_summary(year, payroll_dollar_amounts, "Payroll", correction)
                external = True
            if PD_section and "Police Department Capital Budget" in budget_obj.getPage(i).extractText():
                bp = budget_obj.getPage(i).extractText().replace("\n", " ")
                capital_projects_amounts = self.bp_to_list(bp, "Total Department")
                self.update_capital_expenditures(year, capital_projects_amounts)
                break

    def PDF_scraper_non_extractable(self, year, path, payroll_signifier):
        """This code was given it's own function on July 7th"""
        full_text = self.text_from_pdf(path)
        mission_position = [x for x in re.finditer(self.mission, full_text)]
        assert len(mission_position) == 1, "Found multiple mission statements for cops"
        PD_text = full_text[mission_position[0].start():]
        # dollar_amounts_overall = self.bp_to_list(PD_text, "Total\s+\d+", 5)
        # self.update_budget_summary(year, dollar_amounts_overall, "Overall")
        payroll_position = [x for x in re.finditer(payroll_signifier, PD_text)]
        if year == 2018:
            payroll_text = PD_text[payroll_position[0].start():]
            self.alt_get_dollar_amounts_payroll(year)
        else:
            correction = None
            for i in range(2):
                payroll_text = PD_text[payroll_position[i].start():]
                overall_dollar_amounts = self.bp_to_list(payroll_text, "Grand Total")
                if i == 1 and year - 2 in self.federal_expenditures.columns:
                    correction = 1 - self.federal_expenditures.loc[year - 2] / overall_dollar_amounts[1]
                self.update_budget_summary(year, overall_dollar_amounts, "Overall", correction)
                OT_dollar_amounts = self.bp_to_list(payroll_text, "vertime")
                self.update_budget_summary(year, OT_dollar_amounts, "OT", correction)
                payroll_dollar_amounts = self.bp_to_list(payroll_text, "Total Personnel Services")
                self.update_budget_summary(year, payroll_dollar_amounts, "Payroll", correction)
        capital_budget_position = re.search("Police Department Capital Budget", PD_text)
        capital_budget_text = PD_text[capital_budget_position.start():]
        capital_dollar_amounts = self.bp_to_list(capital_budget_text, "Total Department")
        self.update_capital_expenditures(year, capital_dollar_amounts)

    def alt_get_dollar_amounts_payroll(self, year):
        """Need workaround for 2018 because OCR doesn't read it in right
        New July 16th: add external funds (second integer)"""
        correction = 1 - self.federal_expenditures.loc[year - 2] / 9562319
        self.budget_summary.loc["Payroll Budget", year] = 337939296 + 4789220 * correction
        self.budget_summary.loc["Payroll Appropriation", year - 1] = 328663838 + 4383901 * correction
        self.budget_summary.loc["Payroll Expenditures", year - 2] = 319608659 + 4387452 * correction
        self.budget_summary.loc["OT Budget", year] = 56494667 + 1067784 * correction
        self.budget_summary.loc["OT Appropriation", year - 1] = 55660719 + 566556 * correction
        self.budget_summary.loc["OT Expenditures", year - 2] = 57479518 + 570673 * correction
        self.budget_summary.loc["Total Budget", year] = 373814105 + 11506920 * correction
        self.budget_summary.loc["Total Appropriation", year - 1] = 364321048 + 10498013 * correction
        self.budget_summary.loc["Total Expenditures", year - 2] = 348887844 + 9562319 * correction

    def update_budget_summary(self, year, dollar_amounts, line_item, correction):
        """Updated by Sasha on August 17th to correct for federal/private dollars in federal funds"""
        print("got to update budget summary for year ", year, " correction is ", correction)
        print("dollar amounts before correction ", dollar_amounts)
        if correction:
            dollar_amounts = [x * correction for x in dollar_amounts]
        print("dollar amounts after correction ", dollar_amounts)

        if line_item == "Overall":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston operating budget not found"
            self.budget_summary.loc["Total Budget", year] += dollar_amounts[3]
            self.budget_summary.loc["Total Appropriation", year - 1] += dollar_amounts[2]
            self.budget_summary.loc["Total Expenditures", year - 2] += dollar_amounts[1]
            print("for year", year, "boston had", dollar_amounts[1]*(1-correction), "in federal spending")
        elif line_item == "OT":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD overtime pay not found"
            self.budget_summary.loc["OT Budget", year] += dollar_amounts[3]
            self.budget_summary.loc["OT Appropriation", year - 1] += dollar_amounts[2]
            self.budget_summary.loc["OT Expenditures", year - 2] += dollar_amounts[1]
        elif line_item == "Payroll":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD total pay not found"
            self.budget_summary.loc["Payroll Budget", year] += dollar_amounts[3]
            self.budget_summary.loc["Payroll Appropriation", year - 1] += dollar_amounts[2]
            self.budget_summary.loc["Payroll Expenditures", year - 2] += dollar_amounts[1]

    def update_capital_expenditures(self, year, dollar_amounts):
        """New August 20th to get capital expenditures in seperate attribute"""
        print("got to update capital expenditures for year" , year)
        self.capital_expenditures_by_year[year - 2] = dollar_amounts[1]

    def add_operating_budget(self):
        """Written by Sasha on June 23rd"""
        file_name = self.alias + "_operating_budget.csv"
        boston_df = self.find_data(file_name, client=None, dataset="operating_budget")
        self.operating_budget = boston_df[boston_df["Dept"] == "Police Department"]
        budget_cols = [i for i in self.operating_budget.columns if "18" in i or "19" in i or "20" in i or "21" in i]
        for x in budget_cols:
            self.operating_budget[x] = self.operating_budget[x].str.replace(",", "")
            self.operating_budget[x] = self.operating_budget[x].str.replace("-", "0").astype(float)

    def get_Boston_PD_expenditures(self):
        """Written by Sasha on June 23rd. The Boston PD has two years of expenditures in it's operating budget dataset
        For now just take these. It's incomplete but without guidance from Bobby it makes sense to just take what's
        easiest to find and download.
        This has been depreciated, can be deleted when this all working"""
        expenditure_cols = ["FY18 Actual", "FY19 Actual"]
        return self.operating_budget[["Expense Category"] + expenditure_cols]

    def get_expenditures_by_year(self, client=None):
        """Written by Sasha on June 24th so all agencies have the same functions called in exploratory main"""

        expenditure_cols = ["FY18 Actual", "FY19 Actual"]
        expenditures_by_year = self.operating_budget[["Expense Category"] + expenditure_cols] \
            .groupby("Expense Category").sum()
        expenditures_by_year.loc[self.alias + " Total Expenditures"] = expenditures_by_year.sum()
        expenditures_by_year.rename(columns={"FY18 Actual": 2018, "FY19 Actual": 2019},
                                    index={"Personnel Services": "Boston PD Expenditure on Personnel Services"},
                                    inplace=True)
        return expenditures_by_year.loc[["Boston PD Expenditure on Personnel Services",
                                         self.alias + " Total Expenditures"]]


class ChelseaPD(PoliceDepartment):
    """Created by Sasha on June 25th. As of right now I don't have access to API for Chelsea's open data site
    here https://chelseama.finance.socrata.com/#!/view-data so instead I'm manually downloading csv's
    New July 6th: take out 'appropriations column' and replace with 'proposed budget column' which
    will only be populated with 2021 data
    Note that there is additional debt service for chelsea but I can't figure out what projects that debt service is
    from"""

    def __init__(self):
        year_range = list(range(2016, 2021))
        PoliceDepartment.__init__(self, "Chelsea PD", "Chelsea PD", year_range)
        self.dept_title = "Police Department Program Budget"
        self.add_pension_costs = ChelseaPD_Pensions
        self.add_fringe_benefits = ChelseaPD_Fringe
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Proposed Budget",
                                                                           "OT Proposed Budget",
                                                                           "Total Proposed Budget",
                                                                           "Payroll Budget",
                                                                           "OT Budget",
                                                                           "Total Budget",
                                                                           "Payroll Expenditures",
                                                                           "OT Expenditures",
                                                                           "Total Expenditures"])
        self.scrape()
        self.Add_True_Earnings()
        self.get_final_costs()


    def from_PDF(self):
        """Written by Sasha on July 2nd to iterate through the two budgets we have"""
        self.PDF_scraper_2020(data_dir_path + "ChelseaPD/Budget_FY20_Chelsea.pdf")
        self.PDF_scraper_2021(data_dir_path + "ChelseaPD/Budget_FY21_Chelsea.pdf")
        self.to_float()

    def PDF_scraper_2020(self, path):
        """Written by Sasha on June 29th to get data from pdfs here
        https://www.chelseama.gov/city-auditor/pages/financial-documents-reports"""
        budget_FY20_pdf = PdfFileReader(path)
        for p in range(budget_FY20_pdf.getNumPages()):
            if self.dept_title in budget_FY20_pdf.getPage(p).extractText():
                bp = budget_FY20_pdf.getPage(p).extractText().replace("\n", " ")
                PD_start = re.search("Police Department Program Budget ", bp)
                bp = bp[PD_start.end():]
                dollar_amounts_payroll = self.bp_to_list(bp, "Salaries, Wages and Benefits")
                self.update_budget_summary_2020(2020, dollar_amounts_payroll, "Payroll")
                dollar_amounts_operation = self.bp_to_list(bp, "Operations and Maintenance")
                overall_dollar_amounts = [dollar_amounts_payroll[i] + dollar_amounts_operation[i]
                                          for i in range(len(dollar_amounts_payroll))]
                self.update_budget_summary_2020(2020, overall_dollar_amounts, "Overall")
                capital_dollar_amounts = self.bp_to_list(bp, "Capital")
                self.update_budget_summary_2020(2020, capital_dollar_amounts, "Capital")
                break

    def PDF_scraper_2021(self, path):
        budget_obj = PdfFileReader(path)
        PD_section = False
        for p in range(budget_obj.getNumPages()):
            if "Police Salaries" in budget_obj.getPage(p).extractText():
                bp = budget_obj.getPage(p).extractText().replace("\n", " ")
                PD_section = True
                payroll_dollar_amounts = self.bp_to_list(bp, "Group Total:")
                self.update_budget_summary_2021(2021, payroll_dollar_amounts, "Payroll")
                bp = budget_obj.getPage(p + 1).extractText().replace("\n", " ")
                operation_dollar_amounts = self.bp_to_list(bp, "Group Total:")
                self.update_budget_summary_2021(2021, (payroll_dollar_amounts, operation_dollar_amounts), "Non-Capital")
                capital_start = re.search("Capital", bp)
                bp = bp[capital_start.start():]
                capital_dollar_amounts = self.bp_to_list(bp, "Group Total:")
                self.update_budget_summary_2021(2021, capital_dollar_amounts, "Capital")
                break

    def update_budget_summary_2021(self, year, dollar_amounts, line_item):
        """On July 7th the name of this function was changed"""
        if line_item == "Non-Capital":
            payroll_dollars, operations_dollars = dollar_amounts
            assert dollar_amounts != [], "No total line item found for " + str(year)
            self.budget_summary.loc["Total Expenditures", year - 2] = payroll_dollars[2] + operations_dollars[2]
            self.budget_summary.loc["Total Expenditures", year - 3] = payroll_dollars[1] + operations_dollars[1]
            self.budget_summary.loc["Total Expenditures", year - 4] = payroll_dollars[0] + operations_dollars[0]
            self.budget_summary.loc["Total Budget", year - 1] = payroll_dollars[3] + operations_dollars[3]
            self.budget_summary.loc["Total Proposed Budget", year] = payroll_dollars[4] + operations_dollars[4]
        elif line_item == "Payroll":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Chelsea PD total pay not found"
            self.budget_summary.loc["Payroll Expenditures", year - 2] = dollar_amounts[2]
            self.budget_summary.loc["Payroll Expenditures", year - 3] = dollar_amounts[1]
            self.budget_summary.loc["Payroll Expenditures", year - 4] = dollar_amounts[0]
            self.budget_summary.loc["Payroll Budget", year - 1] = dollar_amounts[3]
            self.budget_summary.loc["Payroll Proposed Budget", year] = dollar_amounts[4]
        elif line_item == "Capital":
            assert dollar_amounts is not None, "Dollar amounts for " + str(
                year) + " Chelsea PD capital expenditures not found"
            self.capital_expenditures_by_year[year - 2] = dollar_amounts[2]
            self.capital_expenditures_by_year[year - 3] = dollar_amounts[1]
            self.capital_expenditures_by_year[year - 4] = dollar_amounts[0]

    def update_budget_summary_2020(self, year, dollar_amounts, line_item):
        """Written on July 7th during update"""
        if line_item == "Overall":
            for i in range(5):
                self.budget_summary.loc["Total Budget", year - i] = dollar_amounts[4 - i]

        if line_item == "Payroll":
            for i in range(5):
                self.budget_summary.loc["Payroll Budget", year - i] = dollar_amounts[4 - i]

        if line_item == "Capital":
            # Note that for 2016, we use budget instead of expenditures
            self.capital_expenditures_by_year[year - 4] = dollar_amounts[0]


class ReverePD(PoliceDepartment):
    """Created by Sasha June 25th
    Revere has no API, so this code will iterate over pdfs I manually downloaded from Revere's site
    To do: summarize 2016 budget, get $ spend on weapons and weapons related expenses
    New July 6th: different documents have different mission statements, store in dict
    Right now, this doesn't use the Budget Summary the page after the pie chart for 2017, 2018, 2019 though
    possible we could get some useful info out of it.
    For Revere PD, there is a big capital expenditure for line-item 'public safety.''"""

    def __init__(self):
        year_range = list(range(2016, 2021))
        PoliceDepartment.__init__(self, "Revere PD", "Revere PD", year_range)
        old_mission_statement = "to enforce the laws, preserve the peace, reduce the fear and provide for a safe environment."
        new_mission_statement = "We, the members of the Revere Police Department are Committed, take Pride,"
        self.totals_page_signifiers = ["TOTALAUXILIARY POLI CE", "TOTAL AUXILIARY POLICE"]
        self.mission_statement = {2016: old_mission_statement, 2017: old_mission_statement,
                                  2018: new_mission_statement, 2019: new_mission_statement, 2020: new_mission_statement,
                                  2021: new_mission_statement}
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["OT Recommended",
                                                                           "Payroll Recommended",
                                                                           "Total Recommended",
                                                                           "OT Adopted",
                                                                           "Payroll Adopted",
                                                                           "Total Adopted",
                                                                           "Total Expenditures"])
        self.capital_expenditures_by_year = get_ReverePD_Capital_Costs()
        self.scrape()
        self.pensions, self.PD_fraction = ReverePD_Pensions(
            self.budget_summary.loc["Payroll Adopted", list(range(2016, 2020))])
        self.fringe = ReverePD_Fringe(self.PD_fraction)
        self.get_final_costs()


    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Pensions_statewide shouldn't be passed in, better solution should be found
        Note that we take budgeted dollars for payroll because the budgeted dollars are broken down by
        payroll vs non-payroll in a more precise way"""
        self.operating_costs = self.budget_summary.loc["Total Expenditures", list(range(2016, 2020))]
        self.operating_costs[2019] = self.budget_summary.loc["Total Adopted", 2019]
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Adopted", list(range(2016,2020))]
        self.non_payroll_operating_expenditures_by_year = self.budget_summary.loc["Total Adopted"] - \
                                                  self.budget_summary.loc["Payroll Adopted"]
        self.non_payroll_operating_expenditures_by_year = \
            self.non_payroll_operating_expenditures_by_year.loc[list(range(2016, 2020))]
        self.payroll_by_year = self.payroll_expenditures_by_year
        if add_hidden_costs:
            return self.operating_costs + self.pensions + self.fringe + self.capital_expenditures_by_year
        else:
            return self.budget_summary.loc["Total Budget"]

    def from_PDF(self):
        """Last Updated by Sasha on June 26th to get data from FY 16 budget
        This will get expenditures and budget both, they come from the same code. Later could depreciate the
        add_budget_by_year() method and have it all run from one function call"""
        file_dict = {2016: "ReverePD/Revere_FY16", 2017: "ReverePD/Revere_FY17",
                     2018: "ReverePD/Revere_FY18", 2019: "ReverePD/Revere_FY19",
                     2020: "ReverePD/Revere_FY20", 2021: "ReverePD/Revere_FY21"}

        for y in self.year_range + [2021]:
            if y > 2016:
                self.post_2016_budget_scraper(y, PdfFileReader(data_dir_path + file_dict[y] + ".pdf"))
            if y == 2016:
                self.budget_scraper_2016()
        self.hardcode_FY20_totals()
        self.budget_summary = self.budget_summary.loc[:, self.year_range]
        self.to_float()

    def post_2016_budget_scraper(self, y, full_budget):
        """Last Updated July 6th"""
        police_section = False
        for p in range(75, full_budget.getNumPages()):
            if self.match_mission(self.mission_statement[y], full_budget.getPage(p).extractText()) is not None:
                police_section = True

            if police_section and sum([1 for x in self.totals_page_signifiers
                                       if x in full_budget.getPage(p).extractText().replace("\n", " ")]) > 0:
                bp = full_budget.getPage(p).extractText().replace("\n", " ")
                line_item = [x for x in self.totals_page_signifiers
                             if x in full_budget.getPage(p).extractText().replace("\n", " ")]
                dollar_amounts = self.bp_to_list(bp, line_item[0])
                self.update_budget_summary(y, dollar_amounts[6:], "Overall Alt")

            if police_section and "vertime" in full_budget.getPage(p).extractText() and \
                    "Uniformed Base" in full_budget.getPage(p).extractText():
                bp = full_budget.getPage(p).extractText().replace("\n", " ")
                OT_dollar_amounts = self.bp_to_list(bp, "Overtime")

                self.update_budget_summary(y, OT_dollar_amounts, "Overtime")
            if police_section and "police" in full_budget.getPage(p).extractText().lower() and \
                    "Total Department Expenses" in full_budget.getPage(p).extractText():
                bp = full_budget.getPage(p).extractText().replace("\n", " ")
                payroll_dollar_amounts = self.bp_to_list(bp, "Total Payroll Expenses")
                self.update_budget_summary(y, payroll_dollar_amounts, "Payroll")
                total_dollar_amounts = self.bp_to_list(bp, "Total Department Expenses")
                self.update_budget_summary(y, total_dollar_amounts, "Overall")
                break

    def budget_scraper_2016(self):
        """Created by Sasha June 26th
        Changed to hardcode on July 7th because I'm tired of working on this """

        self.budget_summary.loc["Total Recommended", 2016] = 10061723
        self.budget_summary.loc["OT Recommended", 2016] = 217775
        self.budget_summary.loc["Payroll Recommended", 2016] = 8997073

    def update_budget_summary(self, year, dollar_amounts, line_item):
        """As of July 6th, don't use big table under pie chart, only use data going back two years
        Old format is for 2016, 2020, 2021"""
        if line_item == "Overall":
            assert dollar_amounts != [], "No total line item found for " + year
            self.budget_summary.loc["Total Recommended", year] = dollar_amounts[2]
            self.budget_summary.loc["Total Adopted", year - 1] = dollar_amounts[0]
        if line_item == "Overall Alt":
            self.budget_summary.loc["Total Expenditures", year - 4] = dollar_amounts[0]
            self.budget_summary.loc["Total Expenditures", year - 3] = dollar_amounts[1]
            self.budget_summary.loc["Total Expenditures", year - 2] = dollar_amounts[2]
        elif line_item == "Payroll":
            self.budget_summary.loc["Payroll Recommended", year] = dollar_amounts[2]
            self.budget_summary.loc["Payroll Adopted", year - 1] = dollar_amounts[0]
        elif line_item == "Overtime":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " overtime pay not found"
            self.budget_summary.loc["OT Recommended", year] = dollar_amounts[2]
            self.budget_summary.loc["OT Adopted", year - 1] = dollar_amounts[0]

    def hardcode_FY20_totals(self):
        """Written July 8th"""
        self.budget_summary.loc["Total Expenditures", 2018] = 10724700


class WinthropPD(PoliceDepartment):
    """Last Updated by Sasha July 30th to pass ReverePD object"""

    def __init__(self, ReverePD_fraction):
        year_range = list(range(2016, 2022))
        PoliceDepartment.__init__(self, "Winthrop PD", "Winthrop PD", year_range)
        self.mission2017 = "The Winthrop Police Department is dedicated to"
        self.mission2021 = "Dedicated to providing the highest degree of law enforcement"
        self.payroll_line_items = {2017: "Sub-Total Personnel Services", 2019: "Personnel Services Subtotal"}
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Recommended",
                                                                           "OT Recommended",
                                                                           "Total Recommended",
                                                                           "Payroll Budget",
                                                                           "OT Budget",
                                                                           "Total Budget",
                                                                           "Payroll Expenditures",
                                                                           "OT Expenditures",
                                                                           "Total Expenditures"])
        self.scrape()
        self.payroll_final = self.budget_summary.loc["Payroll Expenditures", list(range(2016,2020))]
        self.payroll_final[2018] = self.budget_summary.loc["Payroll Budget", 2018]
        self.capital_expenditures_by_year = pd.Series(index=list(range(2016, 2020)), data=[0, 39393, 40000, 0])
        self.fringe, self.pensions = WinthropPD_Pensions_Benefits(ReverePD_fraction)
        self.get_final_costs()


    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Written August 12th"""
        self.operating_costs = self.budget_summary.loc["Total Expenditures", list(range(2016, 2020))]
        self.operating_costs.loc[2018] = self.budget_summary.loc["Total Budget", 2018] - self.capital_expenditures_by_year.loc[
            2018]
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Expenditures", list(range(2016, 2020))]
        self.payroll_expenditures_by_year[2018] = self.budget_summary.loc["Payroll Budget", 2018]
        self.non_payroll_operating_expenditures_by_year = self.operating_costs - self.payroll_expenditures_by_year - \
                                                  self.capital_expenditures_by_year.loc[list(range(2016, 2020))]
        self.payroll_by_year = self.payroll_expenditures_by_year
        return self.operating_costs + self.fringe + self.pensions + \
               self.capital_expenditures_by_year.loc[list(range(2016, 2020))]

    def from_PDF(self):
        """Written by Sasha on June 1st"""

        start_text_dict = {2017: self.mission2017, 2019: "Police Department Budget"}
        for y in [2017, 2019]:
            pdf_path = data_dir_path + "WinthropPD/winthrop_FY" + str(y)[2:]
            self.PDF_scraper(y, pdf_path, start_text_dict[y])
        for y in self.year_range:
            self.hardcode_budget_summary(y)
        self.budget_summary = self.budget_summary.loc[:, self.year_range]
        self.to_float()

    def PDF_scraper(self, year, path, start_text):
        """Written for 2019, will hopefully work for 2021 as well
        For code cleanup, make this save to .txt file instead of calling textract each time"""
        full_text = self.text_from_pdf(path)
        PD_start = re.search(start_text, full_text)
        PD_section = full_text[PD_start.start():]
        fire_start = re.search("Fire Department", PD_section)
        bp = PD_section[:fire_start.start()]
        OT_dollar_amounts = self.bp_to_list(bp, "vertime")
        self.update_budget_summary(year, OT_dollar_amounts, "OT")
        payroll_dollar_amounts = self.bp_to_list(bp, self.payroll_line_items[year])
        self.update_budget_summary(year, payroll_dollar_amounts, "Payroll")

    def update_budget_summary(self, year, dollar_amounts, line_item):
        """This is quite similar to Boston PD's equivalent method with the same name.
        For code cleanup I should take a stab at combining them"""
        if line_item == "OT":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD overtime pay not found"
            self.budget_summary.loc["OT Recommended", year] = dollar_amounts[4]
            self.budget_summary.loc["OT Budget", year - 1] = dollar_amounts[2]
            self.budget_summary.loc["OT Expenditures", year - 2] = dollar_amounts[1]
            self.budget_summary.loc["OT Expenditures", year - 3] = dollar_amounts[0]
        elif line_item == "Payroll":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD total pay not found"
            self.budget_summary.loc["Payroll Recommended", year] = dollar_amounts[4]
            self.budget_summary.loc["Payroll Budget", year - 1] = dollar_amounts[2]
            self.budget_summary.loc["Payroll Expenditures", year - 2] = dollar_amounts[1]
            self.budget_summary.loc["Payroll Expenditures", year - 3] = dollar_amounts[0]

    def hardcode_budget_summary(self, year):
        """Updated Aug 20 to put capital expenditures in new attribute
        Capital expenditures come from page 64 of 2019 budget pdf"""
        if year == 2016:
            capital_expenditures = 0
            self.budget_summary.loc["Total Recommended", year] = 2920019
            self.budget_summary.loc["Total Budget", year] = 2951893
            self.budget_summary.loc["Total Expenditures", year] = 3037686
            self.budget_summary.loc["OT Recommended", year] = 283250
            self.budget_summary.loc["OT Budget", year] = 283250
            self.budget_summary.loc["Payroll Recommended", year] = 2736819
            self.budget_summary.loc["Payroll Budget", year] = 2768693
        if year == 2017:
            capital_expenditures = 39393  # Added Aug 20
            self.budget_summary.loc["Total Recommended", year] = 3409299
            self.budget_summary.loc["Total Budget", year] = None  # Missing because no 2018 police budget
            self.budget_summary.loc["Total Expenditures", year] = 3191416 - capital_expenditures
            self.budget_summary.loc["OT Expenditures", year] = 376497
            self.budget_summary.loc["Payroll Expenditures", year] = 2927191
            self.capital_expenditures_by_year.loc[2017] = capital_expenditures
        if year == 2018:
            capital_expenditures = 40000
            self.budget_summary.loc["Total Recommended", year] = None  # Missing because no 2018 police budget
            self.budget_summary.loc["Total Budget", year] = 3500840
            self.budget_summary.loc["Total Expenditures", year] = None  # Missing because no 2020 budget
            self.budget_summary.loc["OT Recommended", year] = None  # Missing because no 2018 police budget
            # self.budget_summary.loc["OT Budget", year] = 290000
            self.budget_summary.loc["OT Expenditures", year] = None  # Missing because no 2020 budget
            self.budget_summary.loc["Payroll Recommended", year] = None  # Missing because no 2018 police budget
            # self.budget_summary.loc["Payroll Budget", year] = 3225884
            self.budget_summary.loc["Payroll Expenditures", year] = None  # Missing because no 2020 budget
            self.capital_expenditures_by_year.loc[2018] = capital_expenditures
        if year == 2019:
            capital_expenditures = 0
            self.budget_summary.loc["Total Recommended", year] = 3507071
            self.budget_summary.loc["Total Budget", year] = None  # Missing because no 2020 budget
            self.budget_summary.loc["Total Expenditures", year] = 4036935
            self.budget_summary.loc["OT Expenditures", year] = 319375
            self.budget_summary.loc["Payroll Expenditures", year] = 3803402
        if year == 2020:
            self.budget_summary.loc["Total Budget", year] = 3639987
            self.budget_summary.loc["OT Budget", year] = 320000
            self.budget_summary.loc["Payroll Budget", year] = 3396466
        if year == 2021:
            self.budget_summary.loc["Total Recommended", year] = 3676393
            self.budget_summary.loc["OT Recommended", year] = 327000
            self.budget_summary.loc["Payroll Recommended", year] = 3424927
