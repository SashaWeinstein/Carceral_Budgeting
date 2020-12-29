"""Created August 14th because Boston external funds budget includes some money that is federal, some that comes
from private foundations and some that comes from the state level, this py file has functions to return dataframes that
stores how much external funds that are non-state for each year.
For the earnings dataset, we will estimate that the % of those funds that come from
federal/private dollars is the same % of total police expenditures that year that came from federal money
Note that our sum of federal/private include some money towards 'Revolving Funds' that come
from other local agencies
If it's unclear where money comes from assume it's not state/local money to err on the side of under-counting"""

import pandas as pd


#This is data from FY18 Document but hold actual spending for 2016
federal_priv_grants_2018 = pd.Series()
federal_priv_grants_2018.loc["Abekam Foundation"] = 0
federal_priv_grants_2018.loc["Academy Revolving Fund"] = 86897
federal_priv_grants_2018.loc["BMSAP"] = 209701
federal_priv_grants_2018.loc["Boston Reentry Initiative"] = 1112055
federal_priv_grants_2018.loc["Canine Revolving Fund"] = 39999
federal_priv_grants_2018.loc["Cold Case Project"] = 0
federal_priv_grants_2018.loc["Community Based Violence Prevention Demonstration Program"] = 331874
federal_priv_grants_2018.loc["CHRP"] = 747138
federal_priv_grants_2018.loc["DNA Laboratory Initiative"] = 175283
federal_priv_grants_2018.loc["Hackney Revolving Fund"] = 74806
federal_priv_grants_2018.loc["JAG Equipment Grant"] = 28203
federal_priv_grants_2018.loc["Justice and Mental Health Expansion Project"] = 74140
federal_priv_grants_2018.loc["Justice Assistance Grant (JAG)"] = 623517
federal_priv_grants_2018.loc["National Crime Statistics Exchange"] = 0
federal_priv_grants_2018.loc["National Forum Capacity Building Demonstration"] = 239784
federal_priv_grants_2018.loc["National Violent Death Reporting Grant aka Injury Surveillance Project"] = 4511
federal_priv_grants_2018.loc["NUE ALERT - Active Shooter"] = 62091
federal_priv_grants_2018.loc["Nuestra Comunidad Development Corporation"] = 905
federal_priv_grants_2018.loc["Office of Violence Against Women"] = 0  # Can't find
federal_priv_grants_2018.loc["OJJDP Opportunities to Reduce Recidivism"] = 0
federal_priv_grants_2018.loc["Paul Coverdell National Forensic Grant"] = 96732
federal_priv_grants_2018.loc["Police Fitness Center Revolving Fund"] = 167275
federal_priv_grants_2018.loc["Port Security Grant"] = 50589
federal_priv_grants_2018.loc["Smart Policing Evidence-Based Law Enforcement Program"] = 165466
federal_priv_grants_2018.loc["Social Sciences Research in Forensic Science"] = 4059
federal_priv_grants_2018.loc["U.S. Marshals: Violence Retrofit"] = 0
federal_priv_grants_2018.loc["VAWA STOP Project"] = 54401


#Data from FY19 Document has actual spending for 2017
federal_priv_grants_2019 = pd.Series()
federal_priv_grants_2019.loc["Academy Revolving Fund"] = 35080
federal_priv_grants_2019.loc["BMASP"] = 32849
federal_priv_grants_2019.loc["Boston Reentry Initiative"] = 686178
federal_priv_grants_2019.loc["Canine Revolving Fund"] = 13012
federal_priv_grants_2019.loc["CHRP"] = 624
federal_priv_grants_2019.loc["DNA Laboratory Initiative"] = 300960
federal_priv_grants_2019.loc["Hackney Revolving Fund"] = 33407
federal_priv_grants_2019.loc["JAG Equipment Grant"] = 135899
federal_priv_grants_2019.loc["Justice and Mental Health Expansion Project"] = 32259
federal_priv_grants_2019.loc["Justice Assistance Grant (JAG)"] = 589129
federal_priv_grants_2019.loc["National Crime Statistics Exchange"] = 0
federal_priv_grants_2019.loc["National Forum Capacity Building Demonstration"] = 30496
federal_priv_grants_2019.loc["National Violent Death Reporting Grant aka Injury Surveillance Project"] = 5888
federal_priv_grants_2019.loc["NUE ALERT - Active Shooter"] = 0
federal_priv_grants_2019.loc["Nuestra Comunidad Development Corporation"] = 0
federal_priv_grants_2019.loc["OJJDP Opportunities to Reduce Recidivism"] = 54701
federal_priv_grants_2019.loc["Paul Coverdell National Forensic Grant"] = 25237
federal_priv_grants_2019.loc["Police Fitness Center Revolving Center"] = 156762
federal_priv_grants_2019.loc["Port Security Grant"] = 412391
federal_priv_grants_2019.loc["Smart Policing Evidence-Based Law Enforcement Program"] = 74506
federal_priv_grants_2019.loc["Social Sciences Research in Forensic Science"] = 0
federal_priv_grants_2019.loc["VAWA STOP Project"] = 69766

#Data From FY20 Document has actual spending for 2018
federal_priv_grants_2020 = pd.Series()
federal_priv_grants_2020.loc["Academy Revolving Fund"] = 82839
federal_priv_grants_2020.loc["BMASP"] = 0
federal_priv_grants_2020.loc["Boston Reentry Initiative"] = 0
federal_priv_grants_2020.loc["Canine Revolving Fund"] = 21017
federal_priv_grants_2020.loc["Community Based Violence Prevention Demonstration Program"] = 336973
federal_priv_grants_2020.loc["CHRP"] = 70764
federal_priv_grants_2020.loc["DNA Laboratory Initiative"] = 236362
federal_priv_grants_2020.loc["Hackney Revolving Fund"] = 13451
federal_priv_grants_2020.loc["JAG Equipment Grant"] = 0
federal_priv_grants_2020.loc["Justice and Mental Health Expansion Project"] = 34857
federal_priv_grants_2020.loc["National Crime Statistics Exchange"] = 29716
federal_priv_grants_2020.loc["National Violent Death Reporting Grant aka Injury Surveillance Project"] = 9773
federal_priv_grants_2020.loc["NUE ALERT - Active Shooter"] = 0
federal_priv_grants_2020.loc["OJJDP Opportunities to Reduce Recidivism"] = 0  # Can't find it in budget
federal_priv_grants_2020.loc["Paul Coverdell National Forensic Grant"] = 9438
federal_priv_grants_2020.loc["Port Security Grant"] = 118974
federal_priv_grants_2020.loc["Smart Policing Evidence-Based Law Enforcement Program"] = 20936
federal_priv_grants_2020.loc["VAWA STOP Project"] = 39347

#Data from FY21 Document is actual spending for 2019

federal_priv_grants_2021 = pd.Series()
federal_priv_grants_2021.loc["Academy Revolving Fund"] = 55563
federal_priv_grants_2021.loc["Canine Revolving Fund"] = 31905
federal_priv_grants_2021.loc["Imago Dei Fund"] = 0  # Can't find in budget
federal_priv_grants_2021.loc["Community Based Violence Prevention Demonstration Program"] = 0
federal_priv_grants_2021.loc["COAP Grant"] = 0
federal_priv_grants_2021.loc["CHRP"] = 0
federal_priv_grants_2021.loc["DNA Laboratory Initiative"] = 217742
federal_priv_grants_2021.loc["Hackney Revolving Fund"] = 14766
federal_priv_grants_2021.loc["JAG Equipment Grant"] = 0  # Can't find in budget
federal_priv_grants_2021.loc["Joe Gallant Memorial"] = 873
federal_priv_grants_2021.loc["Justice and Mental Health Expansion Project"] = 79157
federal_priv_grants_2021.loc["JAG Assistance Grant (JAG)"] = 32201
federal_priv_grants_2021.loc["MSP ICAC (Crimes Against Children)"] = 4969
federal_priv_grants_2021.loc["National Crime Statistics Exchange"] = 565552
federal_priv_grants_2021.loc["National Forum Capacity Building Demonstration"] = 0  # Can't find in budget
federal_priv_grants_2021.loc["National Violent Death Reporting Grant aka Injury Surveillance Project"] = 10201
federal_priv_grants_2021.loc["NUE ALERT - Active Shooter"] = 50193
federal_priv_grants_2021.loc["OCEDTF: Fugitive Unit Vehicles"] = 32248
federal_priv_grants_2021.loc["OJJDP- Opportunities to Reduce Recidivism"] = 0
federal_priv_grants_2021.loc["Paul Coverdell National Forensic Grant"] = 32790
federal_priv_grants_2021.loc["Police Fitness Center Revolving Fund"] = 118069
federal_priv_grants_2021.loc["Port Security Grant"] = 0
federal_priv_grants_2021.loc["Smart Policing Evidence-Based Law Enforcement Program"] = 0
federal_priv_grants_2021.loc["VAWA STOP Project"] = 140388





def BostonPD_External_Funds():
    """Each year uses actual expenditures"""
    df = pd.DataFrame(columns=list(range(2016,2020)),
                      index=["Total Federal/Private Grant Expenditures"] )
    df.loc["Total Federal/Private Grant Expenditures", 2016] = federal_priv_grants_2018.sum()
    df.loc["Total Federal/Private Grant Expenditures", 2017] = federal_priv_grants_2019.sum()
    df.loc["Total Federal/Private Grant Expenditures", 2018] = federal_priv_grants_2020.sum()
    df.loc["Total Federal/Private Grant Expenditures", 2019] = federal_priv_grants_2021.sum()

    return df.loc["Total Federal/Private Grant Expenditures"]
