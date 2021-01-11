"""Trial Court get a subclass as it's agency correction is applied differently"""

from State_Agency import StateAgency
import sys

agency_corrections_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting" \
                         "/Exploratory/Agency_Corrections/"
sys.path.insert(0, agency_corrections_dir)
from Agency_Corrections import trial_court_pcnt_criminal

class Trial_Court(StateAgency):
    """CPCS needs it's own class as it's R24 dollars are counted towards payroll instead of operating costs"""
    def __init__(self, alias, official_name, year_range, payroll_vendors, category, client, correction_function,
                 settlement_agencies):
        StateAgency.__init__(self, alias, official_name, year_range, category, correction_function, settlement_agencies,
                             payroll_vendors, None, client)

    def pension_correction(self, apply_correction, correction):
        """Apply correction is used in TRC version"""
        if not apply_correction:
            return self.local_pensions + self.pensions

        pcnt_criminal_correction = trial_court_pcnt_criminal()
        return self.correction_function(self.pensions) + pcnt_criminal_correction * self.local_pensions

