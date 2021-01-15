"""Created on Dec 29th to replace scraper"""
import pandas as pd
from LocalPD_External_Funds import BostonPD_External_Funds

def get_BostonPD_Non_Payroll_Operating(agency):
    """Passes series of non-payroll operating back to Boston PD Class
    Fringe expend is Worker's Comp Medical under "Current Charges and Obligations"
    Note annoying mistmatch between terminology: in methodology "operating budget" refers to expenditure record. Here it
    refers to expenditures that are non-external.
    """
    #Have to do yr stupid way as boston still has dumb year range attr. Replace with agency.year_range once it's fixed
    yr = agency.year_range
    out_df = pd.DataFrame(index=["Total Operating Expend",
                                 "Payroll Expend",
                                 "Fringe Expend",
                                 "Total External Expend",
                                 "External Payroll Expend"], columns=yr)


    #From 2019 Document
    out_df.loc["Total Operating Expend", 2016] = 348887844
    out_df.loc["Payroll Expend", 2016] = 319608659
    out_df.loc["Fringe Expend", 2016] = 120503
    out_df.loc["Total External Expend", 2016] = 9538737
    out_df.loc["External Payroll Expend", 2016] = 4387452

    #From 2020 Document
    out_df.loc["Total Operating Expend", 2017] = 364594820
    out_df.loc["Payroll Expend", 2017] = 332157566
    out_df.loc["Fringe Expend", 2017] = 132926
    out_df.loc["Total External Expend", 2017] = 9710199
    out_df.loc["External Payroll Expend", 2017] = 3919606

    #From 2021 Document
    out_df.loc["Total Operating Expend", 2018] = 399924493
    out_df.loc["Payroll Expend", 2018] = 357456096
    out_df.loc["Fringe Expend", 2018] = 123164
    out_df.loc["Total External Expend", 2018] = 8961691
    out_df.loc["External Payroll Expend", 2018] = 3677969

    out_df.loc["Total Operating Expend", 2019] = 416762371
    out_df.loc["Payroll Expend", 2019] = 371536139
    out_df.loc["Fringe Expend", 2019] = 101000
    out_df.loc["Total External Expend", 2019] = 7519387
    out_df.loc["External Payroll Expend", 2019] = 3194567

    external_federal = BostonPD_External_Funds()

    #This is money from "operating budget" section that goes to non-payroll operating costs attr
    total_operating_non_payroll = out_df.loc["Total Operating Expend"] - out_df.loc["Payroll Expend"] - \
                                  out_df.loc["Fringe Expend"]

    #Frind what fraction of total external dollars are federal
    fraction_external_federal = external_federal/out_df.loc["Total External Expend"]

    #Take out payroll dollars from external budget too
    external_non_payroll = out_df.loc["Total External Expend"] - out_df.loc["External Payroll Expend"]

    #Estimate fraction of remaining external dollars that are NOT federal
    external_non_payroll_non_federal = external_non_payroll*(1-fraction_external_federal)


    total_non_payroll = total_operating_non_payroll + external_non_payroll_non_federal

    #Fraction all non-federal isn't used in this func. Is is used to remove federal dollars from earnings record
    fraction_all_federal = external_federal/(out_df.loc["Total Operating Expend"]+\
                                                 out_df.loc["External Payroll Expend"])




    return total_non_payroll, fraction_all_federal, \
           out_df.loc["Fringe Expend"], out_df.loc["Payroll Expend"] #Return fringe to be added in fringe calculation

