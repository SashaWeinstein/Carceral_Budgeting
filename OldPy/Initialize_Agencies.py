"""Created by Sasha on June 18th. This code will create agencies and set most or all of our methodology of how
we collect data on them. Attributes of agency class determine how we split up data associated with them
Last updated July 17th to add category"""

from Agency_Classes import StateAgency, MBTA, BostonPD, ChelseaPD, ReverePD, WinthropPD
from sodapy import Socrata
from Agency_Corrections import trial_court_correction, MBTA_correction
app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

def get_state_agencies(yr, skip_MBT=False):
    """New July 21: add MA sheriff's association"""
    out_list = []
    out_list.append(StateAgency(alias="trial_court", official_name="TRIAL COURT (TRC)", year_range=yr,
                           payroll_vendors=["TRC - SUMMARY PAYROLL"], client=client, category="Legal",
                                correction_function = trial_court_correction))
    out_list.append(StateAgency(alias="CPCS", official_name="COMMITTEE FOR PUBLIC COUNSEL SERVICES (CPC)",
                                year_range=yr, payroll_vendors=["CPC - SUMMARY PAYROLL"],
                                client=client, category="Legal",
                                correction_function=trial_court_correction))
    out_list.append(StateAgency(alias="DOC", official_name="DEPARTMENT OF CORRECTION (DOC)", year_range=yr,
                           payroll_vendors=["DOC - SUMMARY PAYROLL"], client=client, category="Jails",
                                correction_function=trial_court_correction))
    out_list.append(StateAgency(alias="Suffolk_DA", official_name="SUFFOLK DISTRICT ATTORNEY (SUF)", year_range=yr,
                           payroll_vendors=["SUF - SUMMARY PAYROLL"], client=client, category="Legal"))
    out_list.append(StateAgency(alias="Suffolk_Sheriff", official_name="SHERIFF DEPARTMENT SUFFOLK (SDS)", year_range=yr,
                           payroll_vendors=["SDS - SUMMARY PAYROLL"], client=client, category="Jails"))
    out_list.append(StateAgency(alias="State_Police", official_name="DEPARTMENT OF STATE POLICE (POL)", year_range=yr,
                           payroll_vendors=["POL - SUMMARY PAYROLL"], client=client, category="Police",
                                correction_function=trial_court_correction))
    if not skip_MBT:
        out_list.append(MBTA(alias="MBTA", official_name="MASSACHUSETTS BAY TRANSPORTATION AUTHORITY (MBT)",
                             year_range=yr,
                             client=client,
                             category="Police",
                             correction_function=MBTA_correction))
        # Note: for MTBA, summary payroll appears to be the only vendor in the dataset, which is unusual
    out_list.append(StateAgency(alias="DAA", official_name="DISTRICT ATTORNEY ASSOCIATION (DAA)", year_range=yr,
                           payroll_vendors=["DAA - SUMMARY PAYROLL"], client=client, category="Legal",
                                correction_function=trial_court_correction))
    out_list.append(StateAgency(alias="MA Sheriff's Association", official_name="SHERIFFS DEPARTMENT ASSOCIATION (SDA)",
                                year_range=yr, payroll_vendors=["SDA - SUMMARY PAYROLL"], client=client,
                                category="Police",
                                correction_function=trial_court_correction))
    return out_list

def get_PDs(skip_winthrop=False):
    out_list = []
    out_list.append(BostonPD())
    out_list.append(ChelseaPD())
    out_list.append(ReverePD())
    if not skip_winthrop:
        print(out_list[-1])
        out_list.append(WinthropPD(out_list[-1]))
    return out_list
