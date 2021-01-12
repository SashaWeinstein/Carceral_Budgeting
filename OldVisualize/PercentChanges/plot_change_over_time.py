"""Created July 16"""

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def plot_change_over_time(melted, title, year_range, y_label="Percent Change", lw=None, legend_loc="lower right"):
    """Created July 16th"""
    palette = sns.color_palette("Paired", melted["index"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="year", y="value", hue="index", palette=palette, sort=False, data=melted)
    p.set_title(title, fontsize=24)
    ax.legend(frameon=False, loc=legend_loc, fontsize=16)
    if lw:
        plt.setp(ax.lines, linewidth=lw)
    plt.xticks(year_range)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    p.set_ylabel(y_label, fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)