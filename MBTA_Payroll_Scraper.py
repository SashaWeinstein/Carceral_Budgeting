"""Created on July 21st, pytesseract's config='--psm 6' is the OCR I need to do this extraction"""

import pandas as pd
from sodapy import Socrata
import numpy as np
import textract
import pytesseract
import tempfile #Probably won't use
import pdf2image
import os
import json
from PyPDF2 import PdfFileReader, PdfFileWriter
pd.set_option('display.float_format', lambda x: '%.3f' % x)

abs_path_start = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"
temp_path = abs_path_start + "data/MBTA_pdfs/mbta_temp_page.pdf"

def scrape_payroll(existing_results_path=None):
    """For scraping 2017, 2015 payroll document I found online at https://www.mbta.com/financials/mbta-budget
    The reason I loop through pages one by one to make debugging easier"""
    if existing_results_path and os.path.exists(abs_path_start + existing_results_path):
        with open(abs_path_start+existing_results_path) as json_file:
            return json.load(json_file)
    else:
        out_dict = {2015: {"total_pay_actual": 0, "police_pay": 0},
                    2017: {"total_pay_actual": 0, "police_pay": 0}}
        split_on_dict = {2015:" ", 2017:"$"}
        for y in out_dict.keys():
            mbta_pdfObj = PdfFileReader(abs_path_start + "data/MBTA_pdfs/mbta-payroll-" + str(y) + ".pdf")
            total_pay = 0
            total_cop_pay = 0
            for page_counter in range(mbta_pdfObj.getNumPages()):
                try:
                    page_to_image(mbta_pdfObj, page_counter, temp_path)
                    images_from_path = pdf2image.convert_from_path(temp_path)
                    row_list = pytesseract.image_to_string(images_from_path[0], config='--psm 6').split("\n")
                    pay_from_page = get_pay(row_list, split_on_dict[y])
                    total_pay += pay_from_page[0]
                    total_cop_pay += pay_from_page[1]
                except:
                    print("bug at page", page_counter)
                    return None, None
            out_dict[y]["total_pay_actual"] = total_pay
            out_dict[y]["police_pay"] = total_cop_pay
        with open(existing_results_path, 'w') as out:
            json.dump(out_dict, out)
    return out_dict

def page_to_image(pdfObj, page, path):
    little = PdfFileWriter()
    little.addPage(pdfObj.getPage(page))
    with open(path, 'wb') as out_pdf: little.write(out_pdf)

def get_pay(row_list, split_on):
    total_pay = 0
    total_cop_pay = 0
    for row in row_list:
        try:
            pay = float(row.split(split_on)[-1].replace(",",""))
            total_pay += pay
            if "Police" in row:
                    total_cop_pay += pay
        except:
            pass
    return total_pay, total_cop_pay