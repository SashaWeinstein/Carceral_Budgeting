"""To generate simple plost of costs over time"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import palettable

def Total_Cost_By_Year(costs, plot_title, ylabel_fontsize=20, figsize=(100, 100), yaxis_text=True,
                       cases = None):

    """Generates a single line for total costs"""
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    if max(costs) < 10**9:
        adj_costs = costs.values/10**6
        yaxis_title = "Dollars in Millions" if yaxis_text else ""
    else:
        adj_costs= costs.values / 10 ** 9
        yaxis_title = "Dollars in Billions" if yaxis_text else ""
    ax = sns.lineplot(x=costs.index, y=adj_costs, color="orange")
    make_pretty(ax, plot_title, yaxis_title, ylabel_fontsize)
    if cases is not None:
        ax2 = ax.twinx()
        sns.lineplot(x=cases.index, y=cases.values, color="blue", ax=ax2)
        ax2.set_ylabel(yaxis_title, fontsize=ylabel_fontsize)
        ax2.set_ylabel("Number of Cases\n Brought by SCDAO",
                       rotation=0, labelpad=300)
        ax2.tick_params(labelsize=48)
        ax2.grid(False)
        # plt.yticks(list(range(25000, 35000, 2000)))
    return fig


def make_pretty(ax, plot_title, yaxis_title, ylabel_fontsize, figsize= (100, 100), change_xticks=True):
    sns.set_style("whitegrid")
    sns.set(rc={"figure.figsize": figsize, "lines.linewidth": 5})
    ax.set_title(plot_title, fontsize=58)
    if change_xticks:
        plt.xticks(list(range(2016, 2020)))
    ax.set_ylabel(yaxis_title, fontsize=ylabel_fontsize)
    ax.set_ylabel("Cost of \n Criminal Legal System\n in Billions",
                  rotation=0, labelpad=300)
    ax.tick_params(labelsize=48)
    ax.set_xlabel("")
    ax.legend(loc="upper left", fontsize=42)
    plt.tight_layout()

def Total_Costs_by_Year_splitHidden():
    """Written Feb 18th"""
    total_costs_SH = pd.read_csv("../../Final_Results/Final_by_Year_splitHidden.csv").set_index("Hidden")  # .squeeze()
    total_costs_SH.loc["Total"] = total_costs_SH.sum()
    print("fraction of total spending  that is stated",
          total_costs_SH.loc[False].sum()/total_costs_SH.loc["Total"].sum())
    sns.set_style("whitegrid")

    to_melt = total_costs_SH.reset_index()
    to_melt = to_melt[to_melt["Hidden"] != True]
    to_melt["Hidden"] = to_melt["Hidden"].replace({False:"Stated"})

    melted = to_melt.melt(id_vars="Hidden")
    melted.rename(columns={"variable": "Year"}, inplace=True)
    fig, ax = plt.subplots(1, 1)

    palette = palettable.tableau.TableauMedium_10.mpl_colors[1:3][::-1]
    ax = sns.barplot(x="Year", y="value", hue="Hidden", data=melted, palette = palette)
    make_pretty(ax, "Criminal Legal System Costs by Year Stated and Total", "Amount",
                ylabel_fontsize=48, figsize=(55, 30),
                change_xticks=False)
    return fig

