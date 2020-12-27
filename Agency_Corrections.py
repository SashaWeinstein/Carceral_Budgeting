"""Updated August 6th to add correction for DOC"""
import pandas as pd
import numpy as np

def trial_court_correction(df):
    """Trial Court statistics from
     https://www.mass.gov/info-details/trial-court-statistical-reports-and-dashboards#statistics-2014-2020-"""
    trial_court_suffolk_correction, _ = trial_court_suffolk()
    trial_court_criminal_correction = trial_court_pcnt_criminal()
    return df*trial_court_suffolk_correction*trial_court_criminal_correction


def trial_court_pcnt_criminal():
    """Find % of all cases that fall under criminal matters each year
    Use "Year End Summary of All Court Activity Report" """
    all_cases = pd.Series(index=list(range(2016,2020)),
                          data=[912757, 887207, 846833, 807244])
    criminal_matters= pd.Series(index=list(range(2016,2020)),
                                data=[313393, 297502, 303026, 306802])
    return criminal_matters/all_cases

def trial_court_suffolk():
    """Get criminal cases in BMC,
    From BMC: criminal case, criminal show cause hearings hearings held, criminal warrants
    Chelsea,
    Juvenile from Suffolk: adult criminal, Delinquency, Youthful Offender
    superior from suffolk,
    The 2019 superior court document has this disclaimer:
    "Prior to FY2018, the "Criminal Case" category included only criminal indictments.
     In FY2019, this category was expanded to also include: bail petitions, criminal complaints, grand jury matters,
     SDP appeals, and youthful offender cases."
    So we don't have complete data for 2019, use 2018 number instead
    """
    df = pd.DataFrame(columns=list(range(2016, 2020)))

    # Commented out code are all criminal filings not just criminal cases
    df.loc["BMC Criminal Cases", 2016] = 23752 #+ 7467 + 1340
    df.loc["BMC Criminal Cases", 2017] = 22447 #+ 14377 + 1379
    df.loc["BMC Criminal Cases", 2018] = 21753 #+ 9087 + 1101
    df.loc["BMC Criminal Cases", 2019] = 20456 #+ 9066 + 1196

    df.loc["Superior Court Criminal Cases Suffolk", 2016] = 818
    df.loc["Superior Court Criminal Cases Suffolk", 2017] = 747
    df.loc["Superior Court Criminal Cases Suffolk", 2018] = 849
    df.loc["Superior Court Criminal Cases Suffolk", 2019] = 1451

    df.loc["District Court Criminal Defendants Chelsea", 2016] = 4108
    df.loc["District Court Criminal Defendants Chelsea", 2017] = 3383
    df.loc["District Court Criminal Defendants Chelsea", 2018] = 3668
    df.loc["District Court Criminal Defendants Chelsea", 2019] = 3144

    df.loc["Juvenile Court Criminal Cases Suffolk", 2016] = 0 + 1198 + 53
    df.loc["Juvenile Court Criminal Cases Suffolk", 2017] = 0 + 963 + 38
    df.loc["Juvenile Court Criminal Cases Suffolk", 2018] = 0 + 863 + 30
    df.loc["Juvenile Court Criminal Cases Suffolk", 2019] = 5 + 691 + 35

    total_criminal_cases = [209791, 197900, 190661, 187817]

    suff_fraction = df.sum()/total_criminal_cases
    suff_fraction.loc[2019] = suff_fraction.loc[2018]

    return suff_fraction, df.sum()
def DOC_correction(df):
    """Data is from https://www.mass.gov/lists/admissions-and-releases"""
    suffolk_pop_correction = DOC_pcnt_suffolk()
    criminal_cases_correction = DOC_pcnt_criminal()
    return df * (suffolk_pop_correction*criminal_cases_correction)

def DOC_pcnt_suffolk():
    """This is correction for % of population that is from suffolk. Methodology should be typed up in agency_corrections
    folder
    Data is from https://www.mass.gov/lists/admissions-and-releases"""

    df = DOC_pcnt_suffolkf_df()

    correction_series = pd.Series()
    for y in list(range(2016, 2020)):
        prev = df.loc[:, (df.columns.str.contains(str(y-1)) & df.columns.str.contains("Q3|Q4"))]
        current = df.loc[:, (df.columns.str.contains(str(y)) & df.columns.str.contains("Q1|Q2"))]
        s = prev.sum(axis=1) + current.sum(axis=1)
        correction_series.loc[y] = s[0] / s[1]

    return correction_series

def DOC_pcnt_suffolkf_df():
    """Uses State Criminally Sentenced New Court Commitments Figure"""
    df = pd.DataFrame()

    #Following data is from 2017 first quarter report, fig 2.7
    df.loc["Suffolk Admits", "2015 Q3"] = 50
    df.loc["Total Admits", "2015 Q3"] = 391
    df.loc["Suffolk Admits", "2015 Q4"] = 81
    df.loc["Total Admits", "2015 Q4"] = 437
    df.loc["Suffolk Admits", "2016 Q1"] = 72
    df.loc["Total Admits", "2016 Q1"] = 439
    df.loc["Suffolk Admits", "2016 Q2"] = 79
    df.loc["Total Admits", "2016 Q2"] = 416
    df.loc["Suffolk Admits", "2016 Q3"] = 41
    df.loc["Total Admits", "2016 Q3"] = 385
    df.loc["Suffolk Admits", "2016 Q4"] = 74
    df.loc["Total Admits", "2016 Q4"] = 387
    df.loc["Suffolk Admits", "2017 Q1"] = 71
    df.loc["Total Admits", "2017 Q1"] = 500

    #Following data is from 2019 third quarter report fig 2.7
    df.loc["Suffolk Admits", "2017 Q2"] = 83
    df.loc["Total Admits", "2017 Q2"] = 440
    df.loc["Suffolk Admits", "2017 Q3"] = 61
    df.loc["Total Admits", "2017 Q3"] = 372
    df.loc["Suffolk Admits", "2017 Q4"] = 77
    df.loc["Total Admits", "2017 Q4"] = 426
    df.loc["Suffolk Admits", "2018 Q1"] = 83
    df.loc["Total Admits", "2018 Q1"] = 437
    df.loc["Suffolk Admits", "2018 Q2"] = 84
    df.loc["Total Admits", "2018 Q2"] = 433
    df.loc["Suffolk Admits", "2018 Q3"] = 72
    df.loc["Total Admits", "2018 Q3"] = 359
    df.loc["Suffolk Admits", "2018 Q4"] = 76
    df.loc["Total Admits", "2018 Q4"] = 384
    df.loc["Suffolk Admits", "2019 Q1"] = 70
    df.loc["Total Admits", "2019 Q1"] = 431
    df.loc["Suffolk Admits", "2019 Q2"] = 90
    df.loc["Total Admits", "2019 Q2"] = 433
    df.loc["Suffolk Admits", "2019 Q3"] = 64
    df.loc["Total Admits", "2019 Q3"] = 364

    #Following data is from 2020 first quarter
    df.loc["Suffolk Admits", "2019 Q4"] = 77
    df.loc["Total Admits", "2019 Q4"] = 426



    return df

def DOC_pcnt_criminal_df():
    """This is correction for % of population that is in on criminal cases
    Uses Average Quarterly Jurisdiction Population by Commitment Type
    """

    pop_df = pd.DataFrame()

    #From 2017 First Quarter Report on Admissions and Releases Fig 1.2
    pop_df.loc["Civil Pop", "2015 Q3"] = 607
    pop_df.loc["Total Pop", "2015 Q3"] = 10721
    pop_df.loc["Civil Pop", "2015 Q4"] = 582
    pop_df.loc["Total Pop", "2015 Q4"] = 10252
    pop_df.loc["Civil Pop", "2016 Q1"] = 607
    pop_df.loc["Total Pop", "2016 Q1"] = 10027
    pop_df.loc["Civil Pop", "2016 Q2"] = 604
    pop_df.loc["Total Pop", "2016 Q2"] = 9872
    pop_df.loc["Civil Pop", "2016 Q3"] = 630
    pop_df.loc["Total Pop", "2016 Q3"] = 9789
    pop_df.loc["Civil Pop", "2016 Q4"] = 581
    pop_df.loc["Total Pop", "2016 Q4"] = 9596
    pop_df.loc["Civil Pop", "2017 Q1"] = 572
    pop_df.loc["Total Pop", "2017 Q1"] = 9527
    pop_df.loc["Civil Pop", "2017 Q2"] = 578
    pop_df.loc["Total Pop", "2017 Q2"] = 9468

    #From 2019 Second Quarter Report Fig 1.2
    pop_df.loc["Civil Pop", "2017 Q3"] = 594
    pop_df.loc["Total Pop", "2017 Q3"] = 9454
    pop_df.loc["Civil Pop", "2017 Q4"] = 562
    pop_df.loc["Total Pop", "2017 Q4"] = 9310
    pop_df.loc["Civil Pop", "2018 Q1"] = 543
    pop_df.loc["Total Pop", "2018 Q1"] = 9167
    pop_df.loc["Civil Pop", "2018 Q2"] = 571
    pop_df.loc["Total Pop", "2018 Q2"] = 9125
    pop_df.loc["Civil Pop", "2018 Q3"] = 551
    pop_df.loc["Total Pop", "2018 Q3"] = 9032
    pop_df.loc["Civil Pop", "2018 Q4"] = 489
    pop_df.loc["Total Pop", "2018 Q4"] = 8855
    pop_df.loc["Civil Pop", "2019 Q1"] = 499
    pop_df.loc["Total Pop", "2019 Q1"] = 8807

    #From 2020 First Quarter Report Fig 1.2
    pop_df.loc["Civil Pop", "2019 Q2"] = 567
    pop_df.loc["Total Pop", "2019 Q2"] = 8800
    pop_df.loc["Civil Pop", "2019 Q3"] = 644
    pop_df.loc["Total Pop", "2019 Q3"] = 8754
    pop_df.loc["Civil Pop", "2019 Q4"] = 614
    pop_df.loc["Total Pop", "2019 Q4"] = 8427

    return pop_df

def DOC_pcnt_criminal():
    pop_df = DOC_pcnt_criminal_df()
    correction_series = pd.Series()
    for y in list(range(2016,2020)):
        prev = pop_df.loc[:,(pop_df.columns.str.contains(str(y-1)) &
                             pop_df.columns.str.contains("Q3|Q4"))]
        current = pop_df.loc[:,(pop_df.columns.str.contains(str(y)) &
                     pop_df.columns.str.contains("Q1|Q2"))]

        s = prev.sum(axis=1) + current.sum(axis=1)
        correction_series.loc[y] = 1-( s[0] / s[1])
    return correction_series

def state_police_correction(df):
    """Use dataset of state police civil tickets from FOIA request
    https://www.muckrock.com/foi/massachusetts-1/state-police-tickets-massdot-26473/"""
    tickets = pd.read_csv("/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory"
                          "/data/Agency_Corrections/state_police/state_police_tickets.csv")
    tickets["Boston Ticket"] = [bos_ticket(x) for x in tickets["Location"]]

    return df*(tickets["Boston Ticket"].sum()/tickets.shape[0])

def population_correction(df):
    """Written September 1st by Sasha. This is general correction which can be used for any agency for which
     we don't have a good way to measure what % of their resources go to suffolk county
     Returns series for 2016-2019 that is % of MA county population that is in suffolk county based on data from ACS
     Suffolk County numbers from
     https://www.opendatanetwork.com/entity/0500000US25025/Suffolk_County_MA/demographics.population.count?year=2018
     MA numbers from
     https://www.opendatanetwork.com/entity/0400000US25/Massachusetts/demographics.population.count?year=2018

     """
    yr = list(range(2016, 2020))
    suffolk_pop = pd.Series(index= [2015] + yr,
                            data= [756919, 767719, 780685, 791766,798559])
    MA_pop = pd.Series(index=[2015] + yr,
                       data=[6705586, 6742143, 6789319, 6830193, 6865639])
    correction_by_FY = pd.Series(index=yr)
    for y in yr:
        correction_by_FY.loc[y] = np.mean([suffolk_pop.loc[y-1]/MA_pop.loc[y-1],
                                           suffolk_pop.loc[y]/MA_pop.loc[y]])
    return df*(correction_by_FY)

def bos_ticket(x):
    """Called in state_police_correction"""
    boston_hoods = ["brighton", "charlestown", "dorchester", "roxbury", "boston", "chelsea", "revere", "winthrop"]
    for h in boston_hoods:
        if h in x.lower():
            return True
    return False

def appeals_court_correction(df):

    trial_court_suffolk_correction, _ = trial_court_suffolk()
    appeals_court_criminal_correction = appeals_court_pcnt_criminal()
    return df * trial_court_suffolk_correction * appeals_court_criminal_correction


def appeals_court_pcnt_criminal():
    """Uses data from https://www.mass.gov/service-details/appeals-court-case-statistics"""
    all_panel_decisions = pd.Series(index=list(range(2016, 2020)),
                          data=[1337, 1443, 1154, 1064])
    criminal_panel_decisions = pd.Series(index=list(range(2016, 2020)),
                                 data=[728, 734, 600, 511])
    return criminal_panel_decisions / all_panel_decisions
