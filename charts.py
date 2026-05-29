"""
charts.py - data visualizations
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from analytics import get_revenue_by_source, get_orders_by_month, get_top_products, get_orders_by_status, get_total_summary

#Dashboard: all charts in one window

def plot_dashboard():
    plt.style.use("seaborn-v0_8-darkgrid")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    plt.subplots_adjust(hspace=0.6, wspace=0.4, top=0.88, bottom=0.1)
    fig.suptitle("E-Commerce Analytics Dashboard", fontsize=18, fontweight="bold")
    
    # Filter buttons on the left
    ax_filter = plt.axes([0.01, 0.45, 0.07, 0.12])
    radio = RadioButtons(ax_filter, ["All", "Shopify", "eBay"])
    
    def draw(source):
        # clear all charts
        for ax in axes.flat:
            ax.cla()
        
        # Chart 1
        data = [row for row in get_revenue_by_source() if source == "All" or row[0] == source]
        colors = []
        for r in data:
            if r[0] == "Shopify":
                colors.append("#005BBB")
            else:
                colors.append("#FFD500")
        axes[0, 0].bar([r[0] for r in data], [r[1] for r in data], color=colors)
        axes[0, 0].set_title("Revenue by source", fontweight="bold")
        
        

    radio.on_clicked(draw)
    draw("All")
    plt.subplots_adjust(hspace=0.7, wspace=0.4)
    plt.tight_layout(rect=[0, 0, 1, 0.95], pad=2)
    plt.show()