"""This code will scrape a pdf of mbta payrolls for 2017 I found online to find total payroll and
money paid to cops
This should get called from agency class"""

import pandas as pd
from sodapy import Socrata
import numpy as np
import textract
import re

def scrape_MBTA_2017():
    with open("data/MBTA_pdfs/mbta-payroll-2017.txt", "r") as saved:
        mbta_OCR = saved.read()
    mbta_page_list = mbta_OCR.split("\\x0c")

    cop_pages = find_cop_pages(mbta_page_list)
    debug_dict = {}
    total_pay = 0
    total_cop_pay =0
    for page_counter in cop_pages:
        page = mbta_page_list[page_counter]
        print("got to page", page_counter)
        last_three_cols = []
        item_list = []
        try:
            item_list = [x for x in page.split("\\n") if x]
            item_list.remove(" ")
            item_list[0] = item_list[0].replace("b'", "")
            ncol = find_ncol(item_list)
            method = find_method(page_counter)
            total_pay, total_cop_pay = method(page_counter, item_list, ncol, total_pay, total_cop_pay, debug_dict)

        except:
            print("failed for page", page_counter)
            return page, debug_dict, item_list, last_three_cols


def method1(page_counter, item_list, ncol, total_pay, total_cop_pay, debug_dict):
    """For page 1, and probably others"""

    special_exceptions(page_counter, item_list, ncol)
    # Should probably decompose this into functions
    for i in range(ncol, len(item_list)):
        if any_numeric(item_list[i]):
            last_three_cols = item_list[i:]
            break
    for i in range(len(last_three_cols) - 1, ncol, -1):
        if "." not in last_three_cols[i]:
            last_three_cols[i + 1] = last_three_cols[i] + last_three_cols[i + 1]
            last_three_cols.pop(i)
    assert len(last_three_cols) % ncol == 0
    pay_col = [float(x.replace(",", "").replace(" ", "")) for x in last_three_cols[ncol * 2:]]
    cop_pos = [i for i in range(0, ncol) if "Police" in item_list[ncol * 3 + i]]
    cop_pay = []
    for c in cop_pos:
        cop_pay.append(pay_col[c])
    debug_dict["page" + str(page_counter)] = {"cop pay": sum(cop_pay), "total pay": sum(pay_col)}
    total_pay += sum(pay_col)
    total_cop_pay += sum(cop_pay)
    return total_pay, total_cop_pay

def method2(item_list):
    """For page 2, and probably others"""

def find_method(page_counter):
    method1_pages = [1]
    method2_pages = [2]
    if page_counter in method1_pages:
        return method1
    elif page_counter in method2_pages:
        return method2

def find_cop_pages(page_list):
    cop_pages = []
    for i in range(len(page_list)):
        if "Police" in page_list[i]:
            cop_pages.append(i)
    return cop_pages

def find_ncol(item_list):
    for n in range(len(item_list)):
        if not item_list[n].isnumeric():
            column_length = n
            break
    return column_length

def any_numeric(in_string):
    return any([x.isnumeric() for x in in_string])


def special_exceptions(page, item_list, ncol):
    """Some pages have a line break which fucks stuff up, so this page fixes those"""
    if page == 1:
        item_list.remove("Cont")
    if page ==2:
       item_list.remove("Al")