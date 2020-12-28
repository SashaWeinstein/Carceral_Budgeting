from Agency_Classes_Big import StateAgency
from Statewide_Pensions import pensions_from_payroll_fraction


class DOC(StateAgency):
    """DOC get it's own class as it's pension function is different"""
    def __init__(self, alias, official_name, year_range, payroll_vendors, category, client, correction_function,
                 settlement_agencies):
        StateAgency.__init__(self, alias, official_name, year_range, category, correction_function, settlement_agencies,
                             payroll_vendors, None, client, pension_function=pensions_from_payroll_fraction)

