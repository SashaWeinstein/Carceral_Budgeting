"""Created by Sasha on July 9th. Takes code written on July 8th to compare amount of moeny budgeted per year
to amount spent for different agencies"""

import pandas as pd
import seaborn as sns
from sodapy import Socrata
import matplotlib.pyplot as plt
import Initialize_Agencies

sns.set(rc={"figure.figsize": (20, 18), "lines.linewidth": 5})
sns.set_style("darkgrid")

year_range = list(range(2016, 2020))

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40


def visualize_all_Jul9():
    """Written July 9th"""
    final_df = pd.DataFrame(index=["Total Budget", "Total Expenditures"], columns=list(range(2016, 2020))).fillna(0)
    for agency in Initialize_Agencies.get_state_agencies(year_range):
        if agency.alias != "MBT":
            agency.get_expenditures_by_year(client)
            agency.add_budget_by_year(client)
            final_df = visualize_state_agencies(agency, final_df)

    for agency in Initialize_Agencies.get_PDs():
        if agency.alias != "Winthrop PD" and agency.alias != "Revere PD":
            agency.from_PDF()
            final_df = compare_budget_to_expen(agency, ["Total"], final_df)
    final_df_melted = melt_budget(final_df)
    budgeted_vs_expenditures(final_df_melted,
                             "Change from Budget to Expenditures for All Agencies")


def visualize_all_Jul10():
    """Written July 9th"""
    final_df = pd.DataFrame(index=["total enacted budget", "total available for spending",
                                   "Total Expenses from Budget Dataset",
                                   "Total Expenditures from Expenditures Dataset"],
                            columns=year_range).fillna(0)
    for agency in Initialize_Agencies.get_state_agencies(year_range):
        if agency.alias != "MBT":
            agency.get_expenditures_by_year(client)
            agency.add_budget_by_year(client)
            final_df = visualize_state_agencies_pt2(agency, final_df)

    final_df_melted = melt_budget(final_df)
    budgeted_vs_expenditures(final_df_melted,
                             "Difference between cthru budget columns for all state agencies")


def budgeted_vs_expenditures(df, title, legend_loc="lower right"):
    g_palette = sns.color_palette("Set1_r", df["year"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="index", y="value", hue="year", palette=g_palette, sort=False, data=df)
    p.set_title(title, fontsize=24)
    ax.legend(frameon=False, loc=legend_loc, fontsize=24)
    p.set_xlabel("")
    p.set_ylabel("Dollar Amount", fontsize=20)
    p.tick_params(labelsize=20)


def melt_budget(df):
    df = df.reset_index()
    df = df.melt(id_vars=["index"])
    df.rename(columns={df.columns[1]: "year"}, inplace=True)
    return df


def compare_budget_to_expen(PD, line_item_list, final_df=None):
    for line_item in line_item_list:

        plot_df = PD.budget_summary[PD.budget_summary.index.str.contains(line_item)].loc[:, [2017, 2018, 2019]]
        if PD.alias == "Chelsea PD":
            plot_df = plot_df.drop(index=line_item + " Proposed Budget")
        if PD.alias == "Winthrop PD":
            plot_df = plot_df.drop(index=line_item + " Budget")
        if PD.alias == "Revere PD":
            plot_df.rename(index={"Total Recommended": "Total Budget"}, inplace=True)
        if final_df is not None:
            final_df = final_df.add(plot_df)
        plot_df_melted = melt_budget(plot_df)
        budgeted_vs_expenditures(plot_df_melted,
                                 "Change in " + line_item + " Budget from" \
                                                            " Recommendation to Expenditures for " + PD.alias)
        return final_df


def visualize_state_agencies(agency, final_df):
    """New July 9th"""
    plot_df = agency.budget_by_year.append(agency.expenditures_by_year) \
        .loc[["total available for spending", "Total Expenditures"], list(range(2016, 2020))] \
        .rename(index={"total available for spending": "Total Budget"})
    plot_df_melted = melt_budget(plot_df)
    budgeted_vs_expenditures(plot_df_melted,
                             "Change from Budget to Expenditures for " + agency.alias)
    if final_df is not None:
        return final_df.add(plot_df)


def visualize_state_agencies_pt2(agency, include_expenditures, final_df):
    """Updated July 13th to include total original budget (GAA) on x axis"""
    if include_expenditures:
        plot_df = agency.budget_by_year.append(agency.expenditures_by_year)
        plot_df = plot_df.loc[["original enacted budget", "total enacted budget", "total available for spending",
                               "total expenses", "Total Expenditures"], :] \
            .rename(index={"total expenses": "Total Expenses \n from Budget Dataset",
                           "Total Expenditures": "Total Expenditures \n from Expenditures Dataset"})
    else:
        plot_df = agency.budget_by_year
        plot_df = plot_df.loc[["original enacted budget", "total enacted budget", "total available for spending",
                               "total expenses"], :]
    plot_df_melted = melt_budget(plot_df)
    # plot_df_melted.rename(columns={plot_df_melted.columns[1]: "year"}, inplace=True)
    budgeted_vs_expenditures(plot_df_melted,
                             "Comparison of different budget numbers from cthru for " + agency.alias)
    if final_df.empty:
        return plot_df
    else:
        return final_df.add(plot_df)


def visualize_state_agencies_pt3(agency, final_df):
    """Created July 13 for reportback to Bobby"""
    plot_df = agency.budget_by_year
    plot_df = plot_df.loc[["original enacted budget", "total enacted budget",
                           "All Appropriations \nPlus Revenues Minus 9c", "total available for spending",
                           "total expenses"], :].rename(index={"original enacted budget": "GAA Budget",
                                                               "total enacted budget": "Total Appropriations\n (GAA plus Supplemental)",
                                                               "total available for spending": "\"Total Available for Spending\" \n from cthru \n (not sure where this money comes from)",
                                                               "total expenses": "Total Expenses"})
    plot_df_melted = melt_budget(plot_df)
    # plot_df_melted.rename(columns={plot_df_melted.columns[1]: "year"}, inplace=True)
    budgeted_vs_expenditures(plot_df_melted,
                             "Comparison of different budget numbers from cthru for " + agency.alias)
    if final_df.empty:
        return plot_df
    else:
        return final_df.add(plot_df)
