import pandas as pd
import matplotlib.pyplot as plt


def read_data(file_path):
    return pd.read_excel(file_path, sheet_name="Sheet1")


def plot_heatmap(data, periods):
    """
    需求二
    :param data:
    :param periods:
    :return:
    """
    plt.figure(figsize=(10, 6))
    for key, values in data.items():
        plt.plot(periods, values, marker="o", label=key)

    plt.xlabel("Period")
    plt.ylabel("Heat")
    plt.title("Heatmap of Lottery Numbers")
    plt.legend()
    plt.savefig("../data/heatmap.png")
    plt.show()


def plot_heatmaps_fourth_requirement(results, num_periods):
    """
    需求四
    :param results:
    :param num_periods:
    :return:
    """
    for key, rates in results.items():
        plt.figure()
        plt.plot(range(1, num_periods + 1), rates, marker="o", linestyle="-")
        plt.title(f"Heatmap for {key}")
        plt.xlabel("Number of Periods Back")
        plt.ylabel("Heat (Occurrences / Periods)")
        plt.grid(True)
        plt.savefig(f"../data/plot_heatmaps_fourth_requirement/{key}.png")
        plt.show()
