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



