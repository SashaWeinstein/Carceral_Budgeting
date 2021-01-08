"""Version 2 Created by Sasha Oct 27th
New in version 2:
Change methodology in how cthru expenditures are split into payroll, non-payroll. Use vendor instead of object class
"""
import pandas as pd
import numpy as np
from sodapy import Socrata
from PyPDF2 import PdfFileReader, PdfFileWriter
import textract
import difflib
import re
import os
import sys

cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)
sys.path.insert(0, "%sFringe" % cost_type_dir)
sys.path.insert(0, "%spdf_scraper" % cost_type_dir)
sys.path.insert(0, "%sCapital_Costs" % cost_type_dir)
sys.path.insert(0, "%sPayroll" % cost_type_dir)
sys.path.insert(0, "%sNon-Payroll_Operating" % cost_type_dir)
from LocalPD_True_Payroll import True_Earnings
from LocalPD_Pensions import ChelseaPD_Pensions, ReverePD_Pensions, WinthropPD_Pensions_Benefits
from LocalPD_Fringe import ChelseaPD_Fringe, ReverePD_Fringe

from ReverePD_Capital_Costs import get_ReverePD_Capital_Costs



from Agency_Parent import Agency

exploratory_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"

data_dir_path = "%sdata/" % exploratory_dir
saved_scraped_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory" \
                     "/data/Scraped_Saved/"

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

# To-Do
# total_statewide_payroll = Total_Statewide_Payroll(client)

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

    def scrape(self):
        file_path = saved_scraped_path + self.alias + ".csv"

        if os.path.exists(file_path):
            self.budget_summary = pd.read_csv(file_path, index_col=0)
            self.budget_summary.columns = [int(x) for x in self.budget_summary.columns]
            if self.alias in ["Boston PD", "Chelsea PD"]:
                self.capital_expenditures_by_year = pd.read_json(
                    saved_scraped_path + self.alias + "_capital_expenditures.json",
                    typ='series', orient='records')
        else:
            self.from_PDF()
            self.budget_summary.to_csv(file_path)
            if self.alias in ["Boston PD", "Chelsea PD"]:
                self.capital_expenditures_by_year.to_json(
                    saved_scraped_path + self.alias + "_capital_expenditures.json")




    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Pensions_statewide shouldn't be passed in, better solution should be found but I'm up against deadline"""

        return self.non_payroll_operating_expenditures_by_year + self.payroll_by_year + self.pensions + self.fringe + self.capital_expenditures_by_year



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
        self.fringe, _ = ReverePD_Fringe(self.PD_fraction)
        self.get_final_costs()

    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Pensions_statewide shouldn't be passed in, better solution should be found
        Note that we take budgeted dollars for payroll because the budgeted dollars are broken down by
        payroll vs non-payroll in a more precise way"""
        self.operating_costs = self.budget_summary.loc["Total Expenditures", list(range(2016, 2020))]
        self.operating_costs[2019] = self.budget_summary.loc["Total Adopted", 2019]
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Adopted", list(range(2016, 2020))]
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
        self.payroll_final = self.budget_summary.loc["Payroll Expenditures", list(range(2016, 2020))]
        self.payroll_final[2018] = self.budget_summary.loc["Payroll Budget", 2018]
        #Capital expenditures should get it's own function. 2017-2019 numbers are from page 73 of FY21 budget
        # 2016 number is from page 134 in FY17 budget
        self.capital_expenditures_by_year = pd.Series(index=list(range(2016, 2020)), data=[0, 39393, 40000, 0])
        self.fringe, self.pensions = WinthropPD_Pensions_Benefits(ReverePD_fraction)
        self.get_final_costs()

    def get_final_costs(self, apply_correction=True, add_hidden_costs=True, pensions_statewide=None):
        """Written August 12th"""
        self.operating_costs = self.budget_summary.loc["Total Expenditures", list(range(2016, 2020))]
        # self.operating_costs.loc[2018] = self.budget_summary.loc["Total Budget", 2018] - self.capital_expenditures_by_year.loc[
        #     2018]
        self.payroll_expenditures_by_year = self.budget_summary.loc["Payroll Expenditures", list(range(2016, 2020))]
        # self.payroll_expenditures_by_year[2018] = self.budget_summary.loc["Payroll Budget", 2018]
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
            self.budget_summary.loc["Total Expenditures", year] = 3331505  # From FY21 Budget
            self.budget_summary.loc["OT Recommended", year] = None  # Missing because no 2018 police budget
            # self.budget_summary.loc["OT Budget", year] = 290000
            self.budget_summary.loc["OT Expenditures", year] = None  # Missing because no 2020 budget
            self.budget_summary.loc["Payroll Recommended", year] = None  # Missing because no 2018 police budget
            # self.budget_summary.loc["Payroll Budget", year] = 3225884
            self.budget_summary.loc["Payroll Expenditures", year] = 3066911  # From FY21 Budget
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
