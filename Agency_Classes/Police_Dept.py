"""Police Dept class is between Agency parent and the 4 local PD"""

from Agency_Parent import Agency

class PoliceDepartment(Agency):
    """New July 7th
    To do: code where you iterate through pages until you've found mission can be moved here"""

    def __init__(self, alias, official_name, year_range):
        Agency.__init__(self, alias, official_name, year_range, "Police")
        self.correction_function = lambda x: x

    def pension_correction(self, apply_correction, correction):
        return self.pensions
