"""Created August 14th to implement calculation of fringe benefits for statewide agencies.
Methodology is that we take health insurance payments through Group Insurance Commission (GIC) and then
estimation portion of those benefits that go to each agency as % of total payroll that an agency makes up"""

from Agency_Classes.Agency_Helpers.Find_Data import find_data


def Total_Statewide_Fringe(client):
    """Implemented August 14. Note that GIC doesn't seem to have unemployment insurance payments
    Important: take out trust money.
    """
    GIC = find_data(False, client, "pegc-naaa", "Department = 'GROUP INSURANCE COMMISSION (GIC)' \
                                  AND budget_fiscal_year >= 2016 AND budget_fiscal_year <= 2019",
                                  "GroupInsuranceCommission_expenditures.csv")
    GIC.loc[:, "amount"] = GIC.loc[:, "amount"].astype(float)
    GIC.loc[:, "budget_fiscal_year"] = GIC.loc[:, "budget_fiscal_year"].astype(int)
    GIC = GIC[GIC["appropriation_type"].str.contains("(?i)federal") == False]
    GIC = GIC[GIC["object_code"] =="(D06) EMPLOYEE HEALTH & LIFE INSURANCE"]
    return GIC.groupby("budget_fiscal_year").sum()["amount"]
