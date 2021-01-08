"""Created on Dec 31st to have a single function that goes from calendar year to fiscal year data.
Current methodology has each FY as half the previous calendar year and half the curreent"""

import pandas as pd
import numpy as np
def convert_CY_to_FY(CY, yr):
    """Written Dec 31st"""
    FY = pd.Series(index=yr)
    for y in yr:
        FY.loc[y] = np.mean([CY.loc[y-1], CY.loc[y]])
    return FY

def convert_CY_to_FY_df(cy_df, yr):
    """Special function for dataframe conversion"""
    FY = pd.DataFrame(columns=yr, index= cy_df.index )
    for y in yr:
        FY.loc[:, y] = cy_df.loc[:, y-1:y].mean(axis=1)
    return FY