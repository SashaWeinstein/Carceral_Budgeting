"""Last updated by Sasha on July 9th"""
import pandas as pd
from sodapy import Socrata
from PyPDF2 import PdfFileReader, PdfFileWriter
import requests
import textract
import difflib
import re
import os

data_dir_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"
saved_scraped_path =  "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory"\
                      "/data/Scraped_Saved/"

class Agency():
    """For keeping track of info associated with a government agency
    To do: year_range attributes
    Last updated by Sasha on June 23rd to add local agencies, which are municipal police departments for now"""

    def __init__(self, alias, official_name, year_range):
        self.alias = alias
        self.official_name = official_name
        self.year_range = year_range
        self.calender_year_data = False
        self.requery = False

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

    def __init__(self, alias, official_name, year_range, payroll_vendors=[], payroll_official_name=None, client=None):
        Agency.__init__(self, alias, official_name, year_range)
        self.client = client
        self.payroll_official_name = payroll_official_name  # MBTA is lowercase in payroll system for some reason
        self.payroll_vendors = payroll_vendors  # Should be a list of vendors.
        self.expenditures = None
        self.calender_year_data = True  # New June 24th
        self.payroll = None  # New on June 22nd
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


    def add_expenditures(self, client):
        """Adds expenditures for agency over the given year range
        Uses this dataset https://cthru.data.socrata.com/dataset/Comptroller-of-the-Commonwealth-Spending/pegc-naaa
        client is Socrata object
        year_range is list of years to do analysis over"""
        file_name = self.alias + "_expenditures.csv"
        self.expenditures = self.find_data(file_name, client, "pegc-naaa", self.construct_expenditures_SOQL)
        self.expenditures["amount"] = self.expenditures["amount"].astype(float)

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
        self.expenditures_by_year = self.expenditures.groupby("budget_fiscal_year").agg({"amount": "sum",
                                                                                    "payroll_amount": "sum"}).T
        self.expenditures_by_year.rename(index = {"amount": "Total Expenditures",
                                                    "payroll_amount":"Payroll Expenditures"}, inplace=True)
        self.expenditures_by_year.columns = [int(x) for x in self.expenditures_by_year.columns]
        self.expenditures_by_year = self.expenditures_by_year.loc[:, self.year_range]



    def add_payroll(self, total_OT_only):
        """Created by Sasha on June 22nd to get payroll data from cthru endpoint
        Dataset is here https://cthru.data.socrata.com/dataset/Commonwealth-Of-Massachusetts-Payrollv2/rxhc-k6iz
        client is Socrata object
        year_range is list of years to get data for
        New July 6th: total_OT_only is bool for whether we want all pay categories or just OT, total payroll
        """
        file_name =  self.alias + "_payroll.csv"
        self.payroll = self.find_data(file_name, self.client, "rxhc-k6iz", self.construct_payroll_SOQL)
        assert not self.payroll.empty, "no payroll info found for " + self.alias
        if total_OT_only:
            self.pay_col = ["pay_total_actual", "pay_overtime_actual"]
        else:
            self.pay_col = [i for i in self.payroll.columns if i[:3] == "pay"]
        self.payroll[self.pay_col] = self.payroll[self.pay_col].astype(float)

    def add_payroll_by_year(self, client, total_OT_only):
        """Written by Sasha on June 24th to take code from exploratory main"""
        self.add_payroll(client, total_OT_only)
        payroll_by_year = self.payroll.groupby("year")[self.pay_col].sum().T
        self.clean_labels(payroll_by_year)
        return payroll_by_year[payroll_by_year.index.str.contains("to date") == False]

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
            self.budget_by_year.loc[["total enacted budget", "retained revenue collected"], :].sum() -\
            self.budget_by_year.loc["planned savings 9c spending"]


    def construct_expenditures_SOQL(self):
        return "Department = '" + self.official_name + "' AND budget_fiscal_year >= 2016"

    def construct_payroll_SOQL(self, yr):
        """Created by Sasha on June 22nd"""
        if self.payroll_official_name:
            official_name = self.payroll_official_name
        else:
            official_name = self.official_name
        return "department_division = '" + official_name + "' AND Year >= " + str(yr[0]) + \
               "AND Year <= " + str(yr[-1])

    def construct_budget_SOQL(self):
        """Updated on July 14th to not filter based on year range attribute, because year range should be changed
        without having to requery. Instead hardcode in 2016"""
        return "department_name = '" + self.official_budget_name + "' AND fiscal_year >= 2016"

class PoliceDepartment(Agency):
    """New July 7th
    To do: code where you iterate through pages until you've found mission can be moved here"""

    def __init__(self, alias, official_name, year_range):
        Agency.__init__(self, alias, official_name, year_range)

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


    def bp_to_list(self, bp, line_item, line_item_len = None):
        """Moved to Police Department class on July 7th Generalizable code to get list of budget items from bp
        line_item_len is for when line item string is regular expression"""
        if line_item_len is None:
            line_item_len = len(line_item)
        line_item_start = re.search(line_item, bp)
        bp = bp[line_item_start.start() + line_item_len:]
        line_item_end = re.search("[A-Za-z]", bp)
        if line_item_end:
            final = bp[:line_item_end.end()]
        else:
            final = bp
        return [x for x in final.split(" ") if x]

    def get_dollar_amounts_payroll(self, bp, total_payroll_line_item):
        """Written by Sasha July 1st to get payroll from Boston PD
        Should use new bp_to_list eventually
        May be depcreciated if bp_to_list is all I need"""

        return self.bp_to_list(bp, "vertime"), self.bp_to_list(bp, total_payroll_line_item)

    def scrape(self):
        file_path = saved_scraped_path + self.alias + ".csv"
        if os.path.exists(file_path):
            self.budget_summary = pd.read_csv(file_path, index_col=0)
            self.budget_summary.columns = [int(x) for x in self.budget_summary.columns]
        else:
            self.from_PDF()
            self.budget_summary.to_csv(file_path)


class BostonPD(PoliceDepartment):
    """Last updated July 7th.
    Most up to date code reads data from pdfs. There is also code to get info from API but it's less complete
    Currently uses API to link to
    https://data.boston.gov/organization/office-of-budget-management
    Possible cleanup idea: set budget summary attribute in parent for police departments"""

    def __init__(self, url_dict=None):
        year_range = list(range(2016, 2022))
        PoliceDepartment.__init__(self, "Boston PD", "Boston PD", year_range)
        self.url_dict = url_dict  # Maps dataset alias to API url
        self.operating_budget = None  # From API
        self.mission = "The mission of the Police Department is Neighborhood Policing"
        if self.url_dict:
            self.add_operating_budget()
        self.budget_summary = pd.DataFrame(columns=self.year_range, index=["Payroll Budget",
                                                                           "OT Budget",
                                                                           "Total Budget",
                                                                           "Payroll Appropriation",
                                                                           "OT Appropriation",
                                                                           "Total Appropriation",
                                                                           "Payroll Expenditures",
                                                                           "OT Expenditures",
                                                                           "Total Expenditures"])
        self.scrape()


    def from_PDF(self):
        """Written by Sasha on Jun 29th to get data from pdf instead of API
        New July 7th: move code for extractble and non-extractable pdfs into different functions"""
        payroll_signifier = "51000 Permanent Employees"
        for y in [2016, 2017, 2020, 2021]:
            pdf_path = data_dir_path + "bostonPD/boston_FY" + str(y)[2:] + ".pdf"
            self.PDF_scraper_extractable(y, pdf_path, payroll_signifier)
        for y in [2018, 2019]:
            path = data_dir_path + "bostonPD/boston_FY" + str(y)[2:]
            self.PDF_scraper_non_extractable(y, path, payroll_signifier)
        self.budget_summary.drop(columns=[2014,2015], inplace=True)
        self.to_float()

    def PDF_scraper_extractable(self, year, path, payroll_signifier):
        """Written by Sasha on June 29th to get data from a particular pdf and get it budget summary df
        As of July 2nd: added 2021 budget, otherwise seems clean"""


        budget_obj = PdfFileReader(path)
        overall_found = False
        PD_section = False
        for i in range(budget_obj.getNumPages()):
            if "/Contents" in budget_obj.getPage(i).keys() and \
                    self.match_mission(self.mission, budget_obj.getPage(i).extractText()) is not None:
                PD_section = True
            if PD_section and not overall_found and "Operating Budget" in budget_obj.getPage(i).extractText():
                bp = budget_obj.getPage(i).extractText().replace("\n", " ")
                dollar_amounts_overall = self.bp_to_list(bp, "Total\s+\d+", 5)
                self.update_budget_summary(year, dollar_amounts_overall, "Overall")
                overall_found = True
            if PD_section and payroll_signifier in budget_obj.getPage(i).extractText():
                bp = budget_obj.getPage(i).extractText().replace("\n", " ")
                OT_dollar_amounts = self.bp_to_list(bp, "vertime")
                self.update_budget_summary(year, OT_dollar_amounts, "OT")
                payroll_dollar_amounts = self.bp_to_list(bp, "Total Personnel Services")
                self.update_budget_summary(year, payroll_dollar_amounts, "Payroll")
                break

    def PDF_scraper_non_extractable(self, year, path, payroll_signifier):
        """This code was given it's own function on July 7th"""
        full_text = self.text_from_pdf(path)
        mission_position = [x for x in re.finditer(self.mission, full_text)]
        assert len(mission_position) == 1, "Found multiple mission statements for cops"
        PD_text = full_text[mission_position[0].start():]
        dollar_amounts_overall = self.bp_to_list(PD_text, "Total\s+\d+", 5)
        self.update_budget_summary(year, dollar_amounts_overall, "Overall")
        payroll_position = [x for x in re.finditer(payroll_signifier, PD_text)]
        payroll_text = PD_text[payroll_position[0].start():]
        if year == 2018:
            self.alt_get_dollar_amounts_payroll(payroll_text, year)
        else:
            OT_dollar_amounts = self.bp_to_list(payroll_text, "vertime")
            self.update_budget_summary(year, OT_dollar_amounts, "OT")
            payroll_dollar_amounts = self.bp_to_list(payroll_text, "Total Personnel Services")
            self.update_budget_summary(year, payroll_dollar_amounts, "Payroll")


    def get_dollar_amounts_overall(self, bp, year):
        """Written by Sasha on June 30th to use regular expressions instead of iterating through letter by letter
        Should be depreciated if above solution works"""

        total_start = re.search("Total\s+\d+,", bp)
        bp = bp[total_start.start() + 5:]
        total_end = re.search("[A-Za-z]", bp)
        if total_end:
            final = bp[:total_end.end() - 1]
        else:
            final = bp
        dollar_amounts = [x for x in final.split(" ") if x]
        self.update_budget_summary(year, dollar_amounts, "Overall")


    def alt_get_dollar_amounts_payroll(self, bp, year):
        """Need workaround for 2018 because OCR doesn't read it in right"""
        line_item_end = re.search("Total Personnel Services", bp)
        next_section = re.search("Supplies & Materials", bp)
        final = bp[line_item_end.end():next_section.start()]
        dollar_amounts = [x for x in final.split(" ") if x]
        self.budget_summary.loc["Payroll Budget", year] = dollar_amounts[-7]
        self.budget_summary.loc["Payroll Appropriation", year - 1] = 328663838
        self.budget_summary.loc["Payroll Expenditures", year - 2] = 319608659
        self.budget_summary.loc["OT Budget", year] = dollar_amounts[-10]
        self.budget_summary.loc["OT Appropriation", year - 1] = 55660719
        self.budget_summary.loc["OT Expenditures", year - 2] = 57479518

    def update_budget_summary(self, year, dollar_amounts, line_item):
        """Updated by Sasha on July 1st to take OT, payroll as well
        For cleanup this should be moved to police department parent agency"""
        if line_item == "Overall":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston operating budget not found"
            self.budget_summary.loc["Total Budget", year] = dollar_amounts[3]
            self.budget_summary.loc["Total Appropriation", year - 1] = dollar_amounts[2]
            self.budget_summary.loc["Total Expenditures", year - 2] = dollar_amounts[1]
        elif line_item == "OT":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD overtime pay not found"
            self.budget_summary.loc["OT Budget", year] = dollar_amounts[3]
            self.budget_summary.loc["OT Appropriation", year - 1] = dollar_amounts[2]
            self.budget_summary.loc["OT Expenditures", year - 2] = dollar_amounts[1]
        elif line_item == "Payroll":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Boston PD total pay not found"
            self.budget_summary.loc["Payroll Budget", year] = dollar_amounts[3]
            self.budget_summary.loc["Payroll Appropriation", year - 1] = dollar_amounts[2]
            self.budget_summary.loc["Payroll Expenditures", year - 2] = dollar_amounts[1]

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

    def add_budget_by_year(self, client=None):
        """Written by Sasha on June 23rd to get to 2020 budget from operating budget dataset from Boston's office of
        budget accountability"""
        budget_cols = ["20 Budget"]
        budget_by_year = self.operating_budget[["Expense Category"] + budget_cols].groupby("Expense Category").sum()
        budget_by_year.loc[self.alias + " Total Budget"] = budget_by_year.sum()
        budget_by_year.rename(columns={"20 Budget": 2020},
                              index={"Personnel Services": "Boston PD Budget for Personnel Services"},
                              inplace=True)
        return budget_by_year.loc[["Boston PD Budget for Personnel Services", self.alias + " Total Budget"]]


class ChelseaPD(PoliceDepartment):
    """Created by Sasha on June 25th. As of right now I don't have access to API for Chelsea's open data site
    here https://chelseama.finance.socrata.com/#!/view-data so instead I'm manually downloading csv's
    New July 6th: take out 'appropriations column' and replace with 'proposed budget column' which
    will only be populated with 2021 data"""

    def __init__(self):
        year_range = list(range(2016, 2021))
        PoliceDepartment.__init__(self, "Chelsea PD", "Chelsea PD", year_range)
        self.dept_title = "Police Department Program Budget"
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
                dollar_amounts_overall = self.bp_to_list(bp, "Department Total")
                self.update_budget_summary_2020(2020, dollar_amounts_overall, "Overall")
                dollar_amounts_payroll = self.bp_to_list(bp, "Salaries, Wages and Benefits")
                self.update_budget_summary_2020(2020, dollar_amounts_payroll, "Payroll")
                break

    def PDF_scraper_2021(self, path):
        budget_obj = PdfFileReader(path)
        PD_section = False
        for p in range(budget_obj.getNumPages()):
            if "Police Salaries" in budget_obj.getPage(p).extractText():
                bp = budget_obj.getPage(p).extractText().replace("\n", " ")
                PD_section = True
                OT_dollar_amounts = self.bp_to_list(bp, "vertime")
                self.update_budget_summary_2021(2021, OT_dollar_amounts, "OT")
                payroll_dollar_amounts = self.bp_to_list(bp, "Group Total:")
                self.update_budget_summary_2021(2021, payroll_dollar_amounts, "Payroll")
            if PD_section and "Department Total" in budget_obj.getPage(p).extractText():
                bp = budget_obj.getPage(p).extractText().replace("\n", " ")
                total_dollar_amounts = self.bp_to_list(bp, "Department Total:")
                self.update_budget_summary_2021(2021, total_dollar_amounts, "Overall")
                break

    def update_budget_summary_2021(self, year, dollar_amounts, line_item):
        """On July 7th the name of this function was changed"""
        if line_item == "Overall":
            assert dollar_amounts != [], "No total line item found for " + str(year)
            self.budget_summary.loc["Total Expenditures", year - 2] = dollar_amounts[2]
            self.budget_summary.loc["Total Expenditures", year - 3] = dollar_amounts[1]
            self.budget_summary.loc["Total Expenditures", year - 4] = dollar_amounts[0]
            self.budget_summary.loc["Total Budget", year-1] = dollar_amounts[3]
            self.budget_summary.loc["Total Proposed Budget", year] = dollar_amounts[4]
        elif line_item == "OT":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Chelsea PD overtime pay not found"
            self.budget_summary.loc["OT Expenditures", year - 2] = dollar_amounts[2]
            self.budget_summary.loc["OT Expenditures", year - 3] = dollar_amounts[1]
            self.budget_summary.loc["OT Expenditures", year - 4] = dollar_amounts[0]
            self.budget_summary.loc["OT Budget", year - 1] = dollar_amounts[3]
            self.budget_summary.loc["OT Proposed Budget", year] = dollar_amounts[4]
        elif line_item == "Payroll":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " Chelsea PD total pay not found"
            self.budget_summary.loc["Payroll Expenditures", year - 2] = dollar_amounts[2]
            self.budget_summary.loc["Payroll Expenditures", year - 3] = dollar_amounts[1]
            self.budget_summary.loc["Payroll Expenditures", year - 4] = dollar_amounts[0]
            self.budget_summary.loc["Payroll Budget", year - 1] = dollar_amounts[3]
            self.budget_summary.loc["Payroll Proposed Budget", year] = dollar_amounts[4]

    def update_budget_summary_2020(self, year, dollar_amounts, line_item):
        """Written on July 7th during update"""
        if line_item == "Overall":
            for i in range(5):
                self.budget_summary.loc["Total Budget", year - i] = dollar_amounts[4-i]

        if line_item == "Payroll":
            for i in range(5):
                self.budget_summary.loc["Payroll Budget", year - i] = dollar_amounts[4-i]

class ReverePD(PoliceDepartment):
    """Created by Sasha June 25th
    Revere has no API, so this code will iterate over pdfs I manually downloaded from Revere's site
    To do: summarize 2016 budget, get $ spend on weapons and weapons related expenses
    New July 6th: different documents have different mission statements, store in dict
    Right now, this doesn't use the Budget Summary the page after the pie chart for 2017, 2018, 2019 though
    possible we could get some useful info out of it."""

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
        self.scrape()


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
            self.budget_summary.loc["Payroll Adopted", year-1] = dollar_amounts[0]
        elif line_item == "Overtime":
            assert dollar_amounts is not None, "Dollar amounts for " + str(year) + " overtime pay not found"
            self.budget_summary.loc["OT Recommended", year] = dollar_amounts[2]
            self.budget_summary.loc["OT Adopted", year - 1] = dollar_amounts[0]

    def hardcode_FY20_totals(self):
        """Written July 8th"""
        self.budget_summary.loc["Total Expenditures", 2018] = 10724700


class WinthropPD(PoliceDepartment):
    """Last Updated by Sasha July 8th"""

    def __init__(self):
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
        """Written on July 2nd because much of the data from winthrop PD I can't get my hands on via
        PyPDF2 nor textract, didn't have time to try new methods"""
        if year == 2016:
            self.budget_summary.loc["Total Recommended", year] = 2920019
            self.budget_summary.loc["Total Budget", year] = 2951893
            self.budget_summary.loc["Total Expenditures", year] = 3037686
            self.budget_summary.loc["OT Recommended", year] = 283250
            self.budget_summary.loc["OT Budget", year] = 283250
            self.budget_summary.loc["Payroll Recommended", year] = 2736819
            self.budget_summary.loc["Payroll Budget", year] = 2768693
        if year == 2017:
            self.budget_summary.loc["Total Recommended", year] = 3409299
            self.budget_summary.loc["Total Budget", year] = None  # Missing because no 2018 police budget
            self.budget_summary.loc["Total Expenditures", year] = 3191416
            self.budget_summary.loc["OT Expenditures", year] = 376497
            self.budget_summary.loc["Payroll Expenditures", year] = 2927191
        if year == 2018:
            self.budget_summary.loc["Total Recommended", year] = None # Missing because no 2018 police budget
            self.budget_summary.loc["Total Budget", year] = 3500840
            self.budget_summary.loc["Total Expenditures", year] = None # Missing because no 2020 budget
            self.budget_summary.loc["OT Recommended", year] = None # Missing because no 2018 police budget
            # self.budget_summary.loc["OT Budget", year] = 290000
            self.budget_summary.loc["OT Expenditures", year] = None # Missing because no 2020 budget
            self.budget_summary.loc["Payroll Recommended", year] = None # Missing because no 2018 police budget
            # self.budget_summary.loc["Payroll Budget", year] = 3225884
            self.budget_summary.loc["Payroll Expenditures", year] = None # Missing because no 2020 budget
        if year == 2019:
            self.budget_summary.loc["Total Recommended", year] = 3507071
            self.budget_summary.loc["Total Budget", year] = None # Missing because no 2020 budget
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

