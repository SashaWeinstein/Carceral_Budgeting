"""This file was created Jan 12th to hold functions for generating pie charts"""
import pandas as pd
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import palettable

home_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/"
sys.path.insert(0, "%sFinal_Results" % home_dir)
from Final_Results_Helpers import get_Result

# misc_viz_dir = "/Visualize/Misc_Viz_Helpers"
sys.path.insert(0, "%sVisualize/Misc_Viz_Helpers" % home_dir)

from Pretty_Names import pretty_agency_names, pretty_category_names

wedge_props={"edgecolor":"k", 'linewidth': 1, 'linestyle': 'solid'}

def Generate_Pie(full_costs, num_wedges, title, pal, linebreak_labels=False):
    """full_costs should be a series
    costs variable refers to costs with extra rows collapsed to 'other'"""
    fig, ax = plt.subplots(1, 1)

    if full_costs.shape[0] > num_wedges:
        costs = full_costs.iloc[:num_wedges, ]
        costs.loc["Other"] = full_costs.iloc[num_wedges:].values.sum()
    else:
        costs = full_costs
    if linebreak_labels:
        label_format = "{}\n(${} million)"
    else:
        label_format = "{} (${} million)"
    costs.index = [label_format.format(name, round(value/10**6, 1)) for name, value in costs.iteritems()]
    p = costs.plot.pie(y=costs, figsize=(14, 10), colors=pal, autopct='%1.1f%%', textprops={'fontsize': 14},
                       wedgeprops=wedge_props)
    plt.ylabel("")
    plt.title(title, fontdict={'fontsize': 18})
    return fig

agency_costs_mean = get_Result("Final_by_Agency.csv")\
    .mean(axis=1).sort_values(ascending=False).rename(index=pretty_agency_names)

def Agency_Costs_Pie(num_wedges, title):
    print("the top ", num_wedges, "agencies account for ",
          agency_costs_mean.iloc[:num_wedges, ].sum()/agency_costs_mean.sum(), "of total cost" )
    return Generate_Pie(agency_costs_mean, num_wedges, title,
                        pal=palettable.cartocolors.qualitative.Vivid_10.mpl_colors)

cost_types_mean = get_Result("Final_by_CostType.csv")\
        .mean(axis=1).sort_values(ascending=False)

def Cost_Types_Pie(title):
    return Generate_Pie(cost_types_mean, 5, title, pal=palettable.tableau.GreenOrange_6.mpl_colors)

category_mean = get_Result("Final_by_Category.csv")\
        .mean(axis=1).sort_values(ascending=False).rename(index=pretty_category_names)

def Category_Pie(title):
    display(category_mean)
    return Generate_Pie(category_mean, 4, title, pal=palettable.tableau.BlueRed_6.mpl_colors)

category_SH = get_Result("Final_by_Category_splitHidden.csv")
# category_SH.index = category_SH.index + category_SH["Hidden"].astype(str)
category_SH.replace({True:"Hidden", False:"Stated"}, inplace=True)
category_SH.rename(index=pretty_category_names, inplace=True)
category_SH.index = ["{} {} Costs".format(x[0], x[1]["Hidden"]) for x in category_SH.iterrows()]
category_SH.drop(columns="Hidden")
category_SH_mean = category_SH.mean(axis=1).sort_values(ascending=False)

def Category_Pie_SH(title):
    return Generate_Pie(category_SH_mean, 6, title, pal=palettable.tableau.BlueRed_12.mpl_colors, linebreak_labels=True)

cost_types_SP_mean = get_Result("Final_by_Cost_Type_splitPayroll.csv")\
    .mean(axis=1)

cost_types_SP_mean.loc["Stated Non-Payroll Expenditures"] = cost_types_SP_mean.loc["Stated Capital Costs"] +\
cost_types_SP_mean.loc["Stated Fringe Costs"] + cost_types_SP_mean.loc["Non-Payroll Operating Costs"]
cost_types_SP_mean = cost_types_SP_mean.reindex(['Stated Payroll Costs', 'Hidden Payroll Costs', 'Hidden Fringe Costs',
                                                     'Pension Costs', 'Hidden Capital Costs', 'Stated Non-Payroll Expenditures', ])
cost_types_SP_mean.rename({"Pension Costs":"Hidden Pension Costs"}, inplace=True)

def Cost_Types_splitPayroll_Pie(title):
    print("reminder: pair colors for both payrolls and outline stated costs")
    return Generate_Pie(cost_types_SP_mean, 6, title,
                        palettable.tableau.GreenOrange_12.mpl_colors[:2] +
                        palettable.tableau.GreenOrange_6.mpl_colors[1:],
                        linebreak_labels=True)