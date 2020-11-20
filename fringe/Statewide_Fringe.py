"""Created August 14th to implement calculation of fringe benefits for statewide agencies.
Methodology is that we take health insurance payments through Group Insurance Commission (GIC) and then
estimation portion of those benefits that go to each agency as % of total payroll that an agency makes up"""

import pandas as pd

def Total_Statewide_Payroll(client):
    total_payroll_2019 = pd.DataFrame(client.get("rxhc-k6iz", where="Year >= 2016 AND Year <= 2019", limit=999999))
    total_payroll_2019.loc[:, "pay_total_actual"] = total_payroll_2019.loc[:, "pay_total_actual"].astype(float)
    total_payroll_2019.loc[:, "year"] = total_payroll_2019.loc[:, "year"].astype(int)
    return total_payroll_2019.groupby("year").sum()["pay_total_actual"]

def Total_Statewide_Fringe(client):
    """Implemented August 14. Note that GIC doesn't seem to have unemployment insurance payments
    Important: take out trust money.
    """
    GIC = pd.DataFrame(client.get("pegc-naaa",
                                  where="Department = 'GROUP INSURANCE COMMISSION (GIC)' \
                                  AND budget_fiscal_year >= 2016 AND budget_fiscal_year <= 2019",
                                  limit=999999))
    GIC.loc[:, "amount"] = GIC.loc[:, "amount"].astype(float)
    GIC.loc[:, "budget_fiscal_year"] = GIC.loc[:, "budget_fiscal_year"].astype(int)
    return GIC.groupby("budget_fiscal_year").sum()["amount"]