"""For creating pie charts for caseflow section of January slidedeck"""

import pandas as pd
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import palettable

wedge_props={"edgecolor":"grey", 'linewidth': 1, 'linestyle': 'solid'}

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

def pie_plot(s, title, custom_autopcnt=False, c_r=range(8), alt_palette=False):
    fig, ax = plt.subplots(1, 1)
    if custom_autopcnt:
        autopnct_func = make_autopct
        values = s.values
    else:
        autopnct_func = lambda x: '%1.1f%%'
        values = None
    if alt_palette:
        palette = [palettable.cartocolors.qualitative.Prism_6.mpl_colors[x] for x in c_r]
    else:
        palette = [palettable.tableau.TableauMedium_10.mpl_colors[x] for x in c_r]
    s.plot.pie(figsize=(20, 10),colors = palette,
                      autopct=autopnct_func(values), textprops={'fontsize': 14},
                      wedgeprops=wedge_props)
    # plt.rcParams['patch.edgecolor'] = 'grey'
    plt.title(title, fontdict={'fontsize': 18})
    plt.ylabel("")
    return fig