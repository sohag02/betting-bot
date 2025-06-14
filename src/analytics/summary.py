import pandas as pd
import json
from typing import Hashable


def calculate_bet_metrics(csv_file_path: str) -> dict:
    """
    Calculates betting metrics from a CSV file.

    The CSV file must have the following headers:
    timestamp, round_id, bet_amount, outcome, balance

    'balance' is the balance after the bet is complete.
    'outcome' is expected to be 'win' or 'loss'.

    Metrics calculated:
    - Total Rounds
    - Wins
    - Losses
    - Final Wallet Balance
    - Maximum Losing Streak
    - Max Bet Placed
    - Total Profit
    - Profit Percentage
    """
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return {}
    except pd.errors.EmptyDataError:
        print(f"Error: The file {csv_file_path} is empty.")
        # Return default values for an empty report
        return {
            "Total Rounds": 0,
            "Wins": 0,
            "Losses": 0,
            "Final Wallet Balance": 0.0,
            "Maximum Losing Streak": 0,
            "Max Bet Placed": 0.0,
            "Total Profit": 0.0,
            "Profit Percentage": 0.0
        }
    except Exception as e:
        print(f"Error reading CSV file {csv_file_path}: {e}")
        return {}

    if df.empty:
        return {
            "Total Rounds": 0,
            "Wins": 0,
            "Losses": 0,
            "Final Wallet Balance": 0.0,
            "Maximum Losing Streak": 0,
            "Max Bet Placed": 0.0,
            "Total Profit": 0.0,
            "Profit Percentage": 0.0
        }

    # Ensure 'outcome' column is treated as string and lowercased for comparison
    df['outcome'] = df['outcome'].astype(str).str.lower()
    df['bet_amount'] = pd.to_numeric(
        df['bet_amount'], errors='coerce').fillna(0).astype(int)
    df['balance'] = pd.to_numeric(
        df['balance'], errors='coerce').fillna(0).astype(int)

    # 1. Initial Wallet Balance calculation (needed for Total Profit, Profit Percentage)
    initial_balance = 0.0
    first_row: pd.Series = df.iloc[0]
    first_bet_amount = first_row['bet_amount']
    first_balance_after_bet = first_row['balance']
    first_outcome = first_row['outcome']

    if first_outcome == 'w':
        # balance_after = balance_before + bet_amount_won
        # Assuming bet_amount is the amount won (profit), not total return
        initial_balance = first_balance_after_bet - first_bet_amount
    elif first_outcome == 'l':
        # balance_after = balance_before - bet_amount_lost
        initial_balance = first_balance_after_bet + first_bet_amount
    else:
        # Tie
        initial_balance = first_balance_after_bet

    # Metrics Calculation
    total_rounds = len(df)
    wins = df[df['outcome'] == 'w'].shape[0]
    losses = df[df['outcome'] == 'l'].shape[0]
    final_wallet_balance = 0.0 if df.empty else df.iloc[-1]['balance']

    max_losing_streak = 0
    current_losing_streak = 0
    for outcome in df['outcome']:
        if outcome in ['l', 'tie']:
            current_losing_streak += 1
        else:
            if current_losing_streak > max_losing_streak:
                max_losing_streak = current_losing_streak
            current_losing_streak = 0
    if current_losing_streak > max_losing_streak:  # Check for a streak ending at the last round
        max_losing_streak = current_losing_streak

    max_bet_placed: int = 0 if df.empty else df['bet_amount'].max()

    total_profit = final_wallet_balance - initial_balance

    if initial_balance != 0:
        profit_percentage = (total_profit / initial_balance) * 100
    else:
        profit_percentage = 0.0  # Or "N/A" or handle as infinite if total_profit > 0

    return {
        "Total Rounds": total_rounds,
        "Wins": wins,
        "Losses": losses,
        "Final Wallet Balance": float(final_wallet_balance),
        "Maximum Losing Streak": max_losing_streak,
        "Max Bet Placed": float(max_bet_placed),
        "Total Profit": float(total_profit),
        "Profit Percentage": float(profit_percentage),
    }


if __name__ == '__main__':
    # main()
    # metrics = calculate_bet_metrics("data/betting_log.csv")
    # print(metrics)
    # with open("betting_metrics.json", "w") as f:
    #     json.dump(metrics, f, indent=4)
    df = pd.read_csv("data/betting_log.csv", parse_dates=["timestamp"])
    print(df.dtypes)
