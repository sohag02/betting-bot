from matplotlib.ticker import MaxNLocator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def generate_capital_growth_curve(df: pd.DataFrame, save=True):
    # convert round_id to serial number
    for i, _ in df.iterrows():
        df.at[i, "round_id"] = i + 1

    fig = plt.figure(figsize=(10, 5))
    plt.plot(df["round_id"], df["balance"],
             label="Wallet Balance", color="green")
    plt.title("Capital Growth Curve")
    plt.xlabel("Round")
    plt.ylabel("Wallet Balance (₹)")
    plt.grid(True)

    # Set x-axis to only show whole numbers
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()
    if save:
        plt.savefig("data/capital_over_time.png")
        plt.close()
    return fig


def win_loss_pie_chart(df: pd.DataFrame):
    win_count = (df["outcome"] == "W").sum()
    loss_count = (df["outcome"] == "L").sum()
    plt.figure(figsize=(6, 6))
    plt.pie([win_count, loss_count], labels=["Wins", "Losses"],
            autopct="%1.1f%%", colors=["green", "red"])
    plt.title("Win vs Loss Ratio")
    plt.tight_layout()
    plt.savefig("data/win_loss_ratio.png")
    plt.close()


def bet_size_histogram(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.hist(df["bet_amount"], bins=20, color="skyblue", edgecolor="black")
    plt.title("Distribution of Bet Sizes")
    plt.xlabel("Bet Amount (₹)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("data/bet_size_histogram.png")
    plt.close()


def profit_per_hour_heatmap(df: pd.DataFrame):
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["profit"] = df["balance"].diff().fillna(0)

    profit_per_hour = df.groupby("hour")["profit"].sum().reset_index()

    # Convert to pivot (though it's a 1D heatmap, we reshape)
    pivot = profit_per_hour.pivot_table(index="hour", values="profit")

    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5)
    plt.title("Profit per Hour")
    plt.ylabel("Hour")
    plt.tight_layout()
    plt.savefig("data/profit_per_hour_heatmap.png")
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv("data/betting_log.csv", parse_dates=["timestamp"])
    # generate_capital_growth_curve(df)
    # win_loss_pie_chart(df)
    # bet_size_histogram(df)
    profit_per_hour_heatmap(df)
