"""
charts.py - data visualizations
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from analytics import get_revenue_by_source, get_orders_by_month, get_top_products, get_orders_by_status #get_total_summary - to be implemented

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
            ax.clear()
            ax.grid(True, color='white', linestyle='-', linewidth=1)
            ax.set_axisbelow(True) # Щоб сітка була під стовпчиками, а не поверх них
        
# Chart 1
        all_data = get_revenue_by_source()
        data = []
        for row in all_data:
            if source == "All" or row[0] == source:
                data.append(row)
        
        sources_list = []
        revenues = []
        colors = []
        for row in data:
            sources_list.append(row[0])
            revenues.append(row[1])
            if row[0] == "Shopify":
                colors.append("#1f77b4")
            else:
                colors.append("#ff7f0e")
        
        axes[0, 0].bar(sources_list, revenues, color=colors, width=0.4)
        axes[0, 0].set_title("Revenue by source", fontweight="bold", fontsize=12, pad=10)
        axes[0, 0].set_ylabel("Revenue (USD)", fontweight="semibold")

        
# Chart 2
        data = get_orders_by_month()
        shopify_months = []
        shopify_orders = []
        ebay_months = []
        ebay_orders = []
        
        for row in data:
            if row[1] == "Shopify":
                shopify_months.append(row[0])
                shopify_orders.append(row[2])
            if row[1] == "eBay":
                ebay_months.append(row[0])
                ebay_orders.append(row[2])        
        if source in ["All", "Shopify"]:
            axes[0, 1].plot(shopify_months, shopify_orders, marker="o", label="Shopify", color="#1f77b4", linewidth=2.5)
        if source in ["All", "eBay"]:
            axes[0, 1].plot(ebay_months, ebay_orders, marker="o", label="eBay", color="#ff7f0e", linewidth=2.5)
        axes[0, 1].set_title("Orders by month", fontweight="bold", fontsize=12, pad=10)
        axes[0, 1].set_ylabel("Orders count", fontweight="semibold")
        axes[0, 1].legend(frameon=True, facecolor='white', edgecolor='none')
        axes[0, 1].tick_params(axis="x", rotation=45)

        
        # Chart 3
        all_data = get_top_products()
        data = []
        for row in all_data:
            if source == "All" or row[1] == source:
                data.append(row)        
        titles = []
        revenues = []
        for row in data:
            titles.append(row[0][:20])
            revenues.append(row[3])
        
        axes[1, 0].barh(titles, revenues, color="#2ca02c")
        axes[1, 0].set_title("Top 5 products", fontweight="bold", fontsize=12, pad=10)
        axes[1, 0].set_xlabel("Revenue (USD)", fontweight="semibold")

    
        # Chart 4

        axes[1, 1].grid(False) 
        axes[1, 1].set_facecolor('#EAEAF2')

        data = get_orders_by_status()
        if source == "All":
            combined = {}
            for row in data:
                status = row[0]
                if status not in combined:
                    combined[status] = 0
                combined[status] += row[2]
            statuses = list(combined.keys())
            counts = list(combined.values())
        else:
            filtered = []
            for row in data:
                if row[1] == source:
                    filtered.append(row)
            statuses = []
            counts = []
            for row in filtered:
                statuses.append(row[0])
                counts.append(row[2])

        if counts:
            pie_colors = ["#2ca02c", "#d62728", "#bcbd22", "#17becf", "#9467bd"]
            
            # Тепер ми приймаємо всі 3 значення: wedges, texts, autotexts
            wedges, texts, autotexts = axes[1, 1].pie(
                            counts, 
                            autopct="%1.0f%%", 
                            colors=pie_colors, 
                            startangle=90, 
                            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                            pctdistance=0.8  # <--- ЦЕЙ ПАРАМЕТР КЕРУЄ ЦИФРАМИ
                        )
            
            # Додаємо легенду
            axes[1, 1].legend(
                wedges, 
                statuses, 
                title="Status",
                loc="center left", 
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize="small"
            )

            for autotext in autotexts:
                autotext.set_fontsize(9)

        axes[1, 1].set_title("Orders by status", fontweight="bold")
        fig.canvas.draw_idle()


    radio.on_clicked(draw)
    draw("All")
    plt.subplots_adjust(hspace=0.7, wspace=0.4)
    plt.tight_layout(rect=[0, 0, 1, 0.95], pad=2)
    plt.show()