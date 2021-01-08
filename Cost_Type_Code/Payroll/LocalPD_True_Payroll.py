"""Created July 30th to take code from jupyter notebooks in pensions folder and put into callable modules
This link https://bmrb.org/wp-content/uploads/2016/05/SR03-3.pdf says all quinn money comes from state
Note on methodology to remove employees covered by MTRS: some MTRS employees are still in the "no teachers" group as
the combination of department/title isn't clear enough. One must have a title that clearly indicates that they have a
role covered by MTRS and a department that is clearly. If the school an employee works at is called "BTU Pilot" or "East Boston EEC"
then that employee isn't counted as an MTRS as it's not 100% clear. This means the fraction of BPD of non-MTRS payroll is
a slight undercount. (Which is intentional, we have to miss in some direction cause we can't know each employee's
pension coverage plan so better to be to strict on who we count as MTRS).

"""

import pandas as pd
import sys

helper_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Agency_Classes/Agency_Helpers"
sys.path.insert(0, helper_dir)
from CY_To_FY import convert_CY_to_FY


to_float_cols = ["REGULAR", "RETRO", "OTHER", "OVERTIME",
                 "INJURED", "DETAIL", "QUINN/EDUCATION INCENTIVE", "TOTAL EARNINGS"]

big_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"

"""
School titles list is from
From https://mtrs.state.ma.us/service/mtrs-membership-eligibility/
Another thing to think about: do principals and headmasters get MSTR accounts? 
Position titles that are eligible for membership by definition are:

School psychologist
School psychiatrist
School adjustment counselor
School social worker appointed under Chapter 71, §46G
Director of occupational guidance and placement appointed under Chapter 71, §38A or §38D
Principal (also, assistant principal)
Supervisor* or superintendent in any public school (also, assistant superintendent)
Supervisor* or teacher of adult civic education
 *A “supervisor” is generally considered to be a person who supervises other “teachers.”
"""
school_titles = ["Teacher", "Principal", "Headmaster", "Superintendent", "Counselor", "Social Worker"]
school_departments = ["BPS", "K-8", "High", "Middle", "Elementary", "Academy", "School"]
title_regex = '(?i)' + '|(?i)'.join(school_titles)
dept_regex = '(?i)' + '|(?i)'.join(school_departments)

def Boston_total_earnings():
    """Data is from https://data.boston.gov/dataset/employee-earnings-report """
    path = big_path + "BostonPD/Boston_Earnings_2019.csv"
    boston_earnings_2019 = pd.read_csv(path)
    boston_earnings_2019[to_float_cols] = boston_earnings_2019[to_float_cols].applymap(string_to_float(2019))
    boston_earnings_2019["year"] = 2019
    boston_earnings = boston_earnings_2019
    for year in (2018, 2017, 2016, 2015):
        path = big_path + "BostonPD/Boston_Earnings_" + str(year) + ".csv"
        earnings = pd.read_csv(path, engine="python")
        earnings["year"] = year
        if year == 2017:
            earnings.rename(columns={"DEPARTMENT NAME": "DEPARTMENT_NAME"}, inplace=True)
        if year == 2015:
            earnings.rename(columns={"DETAILS": "DETAIL"}, inplace=True)
        earnings[to_float_cols] = earnings[to_float_cols].applymap(string_to_float(year))
        boston_earnings = boston_earnings.append(earnings)
    boston_earnings = boston_earnings.rename(columns={"DEPARTMENT_NAME": "department"})
    return boston_earnings


def remove_schools(df, city, title_column):
    """This link https://mtrs.state.ma.us/service/mtrs-membership-eligibility/#:~:text=Charter%20school%20employees&text=Charter%20school%20teachers%20are%20eligible,to%20be%20ESE%20certified%20%5BM.G.L.&text=71%2C%20%C2%A789(y)%5D,as%20a%20charter%20school%20teacher.
    says that charter school employees are eligible for MRTS so they should be excluded here"""
    #During refactor this should be pared down to one block of code
    MTRS = (df[title_column].str.contains(title_regex) &
            df["department"].str.contains(dept_regex))
    df["MTRS"] = MTRS
    MTRS_employees = df[df["MTRS"] == True]
    return df[df["MTRS"] == False], MTRS_employees

def Chelsea_Total_Earnings():
    "Data is from https://chelseama.payroll.socrata.com/#!/year/2017/full_time_employees,others/pay1,pay2,pay3/explore/1-0-0/segment2?x-return-url=https:%2F%2Fchelseama.finance.socrata.com%2F%23!%2Fdashboard&x-return-description=Return%20to%20Open%20Finance"
    path_2017 = big_path + "ChelseaPD/Chelsea_Paycheck_2017.csv"
    chelsea_paycheck_2017 = pd.read_csv(path_2017)
    chelsea_paycheck = chelsea_paycheck_2017.copy()
    pay_cols = ["basepay", "overtimepay", "otherpay", "benefitsamount", "totalpay"]
    for year in list(range(2018, 2020)):
        path = big_path + "ChelseaPD/Chelsea_Paycheck_" + str(year) + ".csv"
        paycheck = pd.read_csv(path)
        chelsea_paycheck = chelsea_paycheck.append(paycheck)
    chelsea_paycheck[pay_cols] = chelsea_paycheck[pay_cols].astype(float)
    chelsea_paycheck["fiscalyear"] = chelsea_paycheck["fiscalyear"].astype(int)
    return chelsea_paycheck


def True_Earnings(agency_alias):
    """Town must be Boston or Chelsea"""
    assert agency_alias in ["Boston PD",
                            "Chelsea PD"], "True Earnings only available for Boston and Chelsea not " + agency_alias
    if agency_alias == "Boston PD":
        return PD_Fraction_of_Total(Boston_total_earnings(), "year", "Boston",
                                    "Boston Police Department", "TOTAL EARNINGS", "TITLE")
    elif agency_alias == "Chelsea PD":
        """Code to fill missing data added to this function on Aug 24"""

        return PD_Fraction_of_Total( Chelsea_Total_Earnings(),
                                        "fiscalyear", "Chelsea",
                                        "POLICE DEPARTMENT",
                                        "totalpay", "position")


def PD_Fraction_of_Total(total_earnings, year_col, city, dept_name, earnings_col, title_col):
    """Methodology for Chelsea is pretty confusing. For Chelsea we have 2016 FY data and calendar year payroll data
    for 2017, 2018, 2019. So Methodology is to use FY16 payroll data for 2016, 2017 calendar year data only for FY 2017,
    and usual methodology for 2018 and 2019
    Important note: earnings for Boston are by calendar year and earnings for Chelsea are by fiscal year.
    When police, citywide non-teacher, and citywide are grouped by year they are assigned to something_by_year
    The variables something_by_FY hold the fiscal year data. For Chelsea they are same as original group by
    """
    yr = list(range(2016,2020))
    PD_total_earnings = total_earnings[total_earnings["department"] == dept_name]
    PD_by_year = PD_total_earnings.groupby(year_col).sum()[earnings_col]
    total_by_year = total_earnings.groupby(year_col).sum()[earnings_col]
    no_teachers, _ = remove_schools(total_earnings, city, title_col)
    total_no_teachers_by_year = no_teachers.groupby(year_col).sum()[earnings_col]
    # Need to fix this during refactor to not be ugly
    if city == "Chelsea":
        # 2016 data is assumed to be 2017 minus difference between 2018 and 2017
        PD_by_year[2016] = PD_by_year[2017] - (PD_by_year[2018] - PD_by_year[2017])
        total_by_year[2016] = total_by_year[2017] - (total_by_year[2018] - total_by_year[2017])
        total_no_teachers_by_year[2016] = total_no_teachers_by_year[2017] - \
                                          (total_no_teachers_by_year[2018] - total_no_teachers_by_year[2017])
        return PD_by_year, PD_by_year / total_no_teachers_by_year, PD_by_year / total_by_year, PD_total_earnings
    elif city=="Boston":
        # Following code should be extracted to function that averages calendar years
        return BostonPD_by_FY(PD_by_year, PD_total_earnings, total_by_year, total_no_teachers_by_year, yr)


def BostonPD_by_FY(PD_by_CY, PD_total_earnings, citywide_payroll_by_CY, citywide_noMTRS_payroll_by_CY, yr):
    """Series passed are by calendar year. Convert to fiscal year and then return:
     police pay by FY,
     fraction of citywide payroll to cops by FY,
     fraction of non-MTRS payroll to cops by FY,
     df of raw police earnings
     """
    PD_by_FY = convert_CY_to_FY(PD_by_CY, yr)
    total_no_teachers_by_FY = convert_CY_to_FY(citywide_noMTRS_payroll_by_CY, yr)
    total_by_FY = convert_CY_to_FY(citywide_payroll_by_CY, yr)

    PD_fraction_noMTRS_by_FY = PD_by_FY / total_no_teachers_by_FY
    PD_fraction_by_FY = PD_by_FY / total_by_FY

    return PD_by_FY, PD_fraction_noMTRS_by_FY, PD_fraction_by_FY, PD_total_earnings
def get_numeric(x):
    if isinstance(x, float) or isinstance(x, int):
        return x
    out = ""
    for letter in x:
        if letter.isnumeric() or letter == ".":
            out += letter
    if not out or out == ".":
        return 0
    return out


def string_to_float(year):
    if year == 2019:
        return lambda x: float(get_numeric(x)) if "-" not in x else 0
    else:
        return lambda x: float(get_numeric(x)) if x != "nan" else 0
