"""Created by Sasha on August 3rd. This code returns all 17 agencies in dictionary """
import sys
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Agency_Classes/")

from State_Agency import StateAgency
from MBTA import MBTA
from BostonPD import BostonPD
from sodapy import Socrata
from CPCS import CPCS
from ChelseaPD import ChelseaPD
from ReverePD import ReverePD
from WinthropPD import WinthropPD

sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Agency_Corrections/")

from Agency_Corrections import trial_court_correction, DOC_correction, \
    appeals_court_correction, population_correction


cost_type_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Cost_Type_Code/"
sys.path.insert(0, "%sPensions" % cost_type_dir)
from Pensions_Final import pensions_from_payroll_fraction


app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

out_dict = {}


def get_agencies(yr):
    """New July 21: add MA sheriff's association"""
    out_dict["trial_court"] = StateAgency(alias="trial_court", official_name="TRIAL COURT (TRC)", year_range=yr,
                                          payroll_vendors=["TRC - SUMMARY PAYROLL"], client=client, category="Legal",
                                          correction_function=trial_court_correction,
                                          settlement_agencies=["TRIAL COURT"])

    out_dict["CPCS"] = CPCS(alias="CPCS", official_name="COMMITTEE FOR PUBLIC COUNSEL SERVICES (CPC)",
                                   year_range=yr, payroll_vendors=["CPC - SUMMARY PAYROLL"],
                                   client=client, category="Legal",
                                   correction_function=trial_court_correction,
                                   settlement_agencies=["COMMITTEE FOR PUBLIC COUNSEL SERVICES"])

    out_dict["DOC"] = StateAgency(alias="DOC", official_name="DEPARTMENT OF CORRECTION (DOC)", year_range=yr,
                                  payroll_vendors=["DOC - SUMMARY PAYROLL"], client=client, category="Jails",
                                  correction_function=DOC_correction,
                                  settlement_agencies=["DEPARTMENT OF CORRECTION", "PAROLE BOARD"],
                                  pension_function=pensions_from_payroll_fraction)
    out_dict["Suffolk DA"] = StateAgency(alias="Suffolk_DA", official_name="SUFFOLK DISTRICT ATTORNEY (SUF)",
                                         year_range=yr,
                                         payroll_vendors=["SUF - SUMMARY PAYROLL"], client=client, category="Legal",
                                         settlement_agencies=["SUFFOLK DISTRICT ATTORNEY"])
    out_dict["Suffolk Sheriff"] = StateAgency(alias="Suffolk_Sheriff", official_name="SHERIFF DEPARTMENT SUFFOLK (SDS)",
                                              year_range=yr, payroll_vendors=["SDS - SUMMARY PAYROLL"],
                                              client=client, category="Jails",
                                              settlement_agencies=["SHERIFF DEPARTMENT SUFFOLK"])
    out_dict["State_Police"] = StateAgency(alias="State_Police", official_name="DEPARTMENT OF STATE POLICE (POL)",
                                           year_range=yr, payroll_vendors=["POL - SUMMARY PAYROLL"],
                                           client=client, category="Police",
                                           correction_function=population_correction,
                                           settlement_agencies=["DEPARTMENT OF STATE POLICE",
                                                                "Municipal Police Training Committee"])

    out_dict["MBTA"] = MBTA(alias="MBTA", official_name="MASSACHUSETTS BAY TRANSPORTATION AUTHORITY (MBT)",
                            year_range=yr,
                            client=client,
                            category="Police",
                            correction_function=population_correction)  # As of August 12th took away MBTA correction function

    out_dict["DAA"] = StateAgency(alias="DAA", official_name="DISTRICT ATTORNEY ASSOCIATION (DAA)", year_range=yr,
                                  payroll_vendors=["DAA - SUMMARY PAYROLL"], client=client, category="Legal",
                                  correction_function=population_correction)
    out_dict["MA Sheriff's Association"] = StateAgency(alias="MA Sheriff's Association",
                                                        official_name="SHERIFFS DEPARTMENT ASSOCIATION (SDA)",
                                                        year_range=yr, payroll_vendors=["SDA - SUMMARY PAYROLL"],
                                                        client=client,
                                                        category="Police",
                                                        correction_function=population_correction)
    out_dict["Parole Board"] = StateAgency(alias="Parole_Board",
                                           official_name="PAROLE BOARD (PAR)",
                                           year_range=yr,
                                           client=client,
                                           category="Jails",
                                           correction_function=DOC_correction)
    out_dict["CJT"] = StateAgency(alias="CJT",
                                  official_name="MUNICIPAL POLICE TRAINING COMMITTEE (CJT)",
                                  payroll_official_name="Municipal Police Training Committee (CJT)",
                                  year_range=yr,
                                  client=client,
                                  category="Police",
                                  correction_function=population_correction)
    out_dict["Supreme_Judicial_Court"] = StateAgency(alias="Supreme_Judicial_Court",
                                                     official_name="SUPREME JUDICIAL COURT (SJC)",
                                                     year_range=yr, client=client,
                                                     category="Legal",
                                                     correction_function=trial_court_correction)
    out_dict["Appeals_Court"] = StateAgency(alias="Appeals_Court",
                                            official_name="APPEALS COURT (APC)",
                                            year_range=yr, client=client, category="Legal",
                                            correction_function=appeals_court_correction)

    out_dict["Boston PD"] = BostonPD(yr)
    out_dict["Chelsea PD"] = ChelseaPD(yr)
    out_dict["Revere PD"] = ReverePD(yr)

    out_dict["Winthrop PD"] = WinthropPD(yr, out_dict["Revere PD"].PD_fraction)

    return out_dict
