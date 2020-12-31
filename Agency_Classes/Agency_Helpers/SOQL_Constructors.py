"""SOQL Constructors are for creating agency-specific queries to the Socrata API
"""


def construct_expenditures_SOQL(agency):
    return "Department = '" + agency.official_name + "' AND budget_fiscal_year >= 2016"


def construct_payroll_SOQL(agency):
    """Created by Sasha on June 22nd"""
    if agency.payroll_official_name is not None:
        official_name = agency.payroll_official_name
    else:
        official_name = agency.official_name
    return "department_division = '" + official_name + "' AND Year >= " + str(agency.year_range[0] - 1) + \
           "AND Year <= " + str(agency.year_range[-1])


def construct_budget_SOQL(agency):
    """Updated on July 14th to not filter based on year range attribute, because year range should be changed
    without having to requery. Instead hardcode in 2016"""
    return "department_name = '" + agency.official_budget_name + "' AND fiscal_year >= 2016"


def construct_settlements_SOQL(agency):
    """New August 10th"""
    SOQL = "("
    for a in agency.settlement_agencies:
        SOQL += "dept_paid_on_behalf_of = '" + agency.settlement_agencies[0] + "' OR "
    SOQL = SOQL[:-4] + ") AND bfy >= " + str(agency.year_range[0])
    return SOQL