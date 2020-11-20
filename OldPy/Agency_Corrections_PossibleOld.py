"""Created July 21st to hold functions for how we calculate what % of agencies spend thier budget on suffolk
county"""

def trial_court_correction(df):
    """From Bobby's spreadsheet where he calculates % of total criminal cases that come from suffolk county"""
    trial_court_correction = {2016: 30756 / 209791, 2017: 28264 / 197900,
                              2018: 27818 / 190661, 2019: 26576 / 187817}
    for year in trial_court_correction.keys():
        df.loc[:, year] = df.loc[:, year]*trial_court_correction[year]

def MBTA_correction(df):
    """I just made this up, hopefully Bobby will have idea of better way to go about this"""
    df.loc[:,:] = df.loc[:,:]*.75