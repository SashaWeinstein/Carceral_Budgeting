"""Created July 30th to take code from jupyter notebooks in pensions folder and put into callable modules
This link https://bmrb.org/wp-content/uploads/2016/05/SR03-3.pdf says all quinn money comes from state"""

import pandas as pd
to_float_cols = ["REGULAR", "RETRO", "OTHER", "OVERTIME",
                 "INJURED", "DETAIL","QUINN/EDUCATION INCENTIVE", "TOTAL EARNINGS"]

big_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"

school_titles = ["Teacher", "Substitute Teacher", "Principal Elementary", "Headmaster"]

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
            earnings.rename(columns={"DETAILS":"DETAIL"}, inplace=True)
        earnings[to_float_cols] = earnings[to_float_cols].applymap(string_to_float(year))
        boston_earnings = boston_earnings.append(earnings)
    boston_earnings = boston_earnings.rename(columns={"DEPARTMENT_NAME": "department"})
    return boston_earnings

def remove_schools(df, city):
    if city =="Boston":
        return df[(df["TITLE"].isin(school_titles) == False) &
                  (df["department"].str.contains("BPS") == False) &
                  (df["department"].str.contains("K-8") == False) &
                  (df["department"].str.contains("High") == False) &
                  (df["department"].str.contains("Middle") == False) &
                  (df["department"].str.contains("Elementary")==False)]
    elif city == "Chelsea":
        return df[df["entity"] != "School"]

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
    assert agency_alias in ["Boston PD", "Chelsea PD"], "True Earnings only available for Boston and Chelsea not " + agency_alias
    if agency_alias == "Boston PD":
        return PD_Fraction_of_Total(Boston_total_earnings(), "year", "Boston",
                                    "Boston Police Department", "TOTAL EARNINGS")
    elif agency_alias == "Chelsea PD":
        """Code to fill missing data added to this function on Aug 24"""
        total_earnings, PD_fraction_non_teacher, PD_fraction_total, PD_payroll = PD_Fraction_of_Total(Chelsea_Total_Earnings(),
                                                                                          "fiscalyear", "Chelsea",
                                                                                          "POLICE DEPARTMENT",
                                                                                          "totalpay")
        PD_fraction_non_teacher[2016] = PD_fraction_non_teacher[2017] - \
                                        (PD_fraction_non_teacher[2018] - PD_fraction_non_teacher[2017])
        return total_earnings, PD_fraction_non_teacher, PD_fraction_total, PD_payroll

def PD_Fraction_of_Total(total_earnings, year_col, city, dept_name, earnings_col):
    """Methodology for Chelsea is pretty confusing. For Chelsea we have 2016 FY data and calendar year payroll data
    for 2017, 2018, 2019. So Methodology is to use FY16 payroll data for 2016, 2017 calendar year data only for FY 2017,
    and usual methodology for 2018 and 2019"""
    if city == "Boston":
        yr = list(range(2016, 2020))
    elif city == "Chelsea":
        yr = list(range(2018, 2020))
    PD_total_earnings = total_earnings[total_earnings["department"] == dept_name]
    PD_by_calendar_year = PD_total_earnings.groupby(year_col).sum()[earnings_col]
    total_by_calendar_year = total_earnings.groupby(year_col).sum()[earnings_col]
    no_teachers = remove_schools(total_earnings, city)
    total_no_teachers_by_calendar_year = no_teachers.groupby(year_col).sum()[earnings_col]

    PD_by_year = pd.Series(index=yr)
    total_no_teachers_by_year = pd.Series(index=yr)
    total_by_year = pd.Series(index=yr)
    if city == "Chelsea":
        PD_by_year.loc[2017] = PD_by_calendar_year.loc[2017]
        total_no_teachers_by_year.loc[2017] = total_no_teachers_by_calendar_year.loc[2017]
        total_by_year.loc[2017] = total_by_calendar_year.loc[2017]
    for y in yr:
        PD_by_year.loc[y] = .5*PD_by_calendar_year.loc[y-1] + .5*PD_by_calendar_year.loc[y]
        total_no_teachers_by_year = .5*total_no_teachers_by_calendar_year.loc[y-1] + \
                                    .5*total_no_teachers_by_calendar_year[y]
        total_by_year = .5*total_by_calendar_year[y-1] + .5*total_by_calendar_year[y]

    return PD_by_year, PD_by_year/total_no_teachers_by_year, PD_by_year/total_by_year, PD_total_earnings



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