"""Created Jan 12th to store pretty names for visualizations"""

pretty_agency_names = {"Suffolk_Sheriff": "Suffolk Sheriff",
                "MBTA":"MBTA Police",
                "Suffolk_DA": "SCDAO",
                "State_Police":"State Police",
                "trial_court": "Trial Court"}

def Prettify_AN(name):
    """AN stands for agency name"""
    if name in pretty_agency_names.keys():
        return pretty_agency_names[name]
    else: return name
