"""For January Slidedeck I want number of suffolk county admits per year"""

import pandas as pd
import sys

home_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Agency_Corrections"
sys.path.insert(0, home_dir)
from Agency_Corrections import DOC_pcnt_criminal, DOC_pcnt_suffolk

def get_Num_Suff_Incarcerated():
    suffolk_pop_correction, criminal_pop = DOC_pcnt_criminal()
    suffolk_pop_correction, suffolk_count = DOC_pcnt_suffolk()
    print("correction code says ", criminal_pop, " people incarcerated on criminal charges")
    print("correction code says fraction of thse folks on suffolk county charges:", suffolk_pop_correction)
    return criminal_pop*suffolk_pop_correction
