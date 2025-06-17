import pandas as pd
from datetime import datetime


def generate_daily_report(csv_file_path: str, report_date_str: str) -> dict:
    """
    Generates a daily report from a CSV file for a specific date.

    The CSV file must have headers: timestamp, round_id, bet_amount, outcome, balance.
    'timestamp' should be convertible to datetime objects.
    'outcome' is expected to be 'win' or 'loss'.
    'bet_amount' is the amount won (if win) or lost (if loss).
    'balance' is the balance after the bet is complete.

    Args:
        csv_file_path (str): The path to the CSV file.
        report_date_str (str): The date for the report in 'YYYY-MM-DD' format.

    Returns:
        dict: A dictionary containing the daily report metrics:
              - report_date
              - total_rounds_played
              - total_wins
              - total_losses
              - total_profit
              Returns an empty dict or a dict with zeros if errors occur or no data.
    """
    default_report = {
        "report_date": report_date_str,
        "total_rounds_played": 0,
        "total_wins": 0,
        "total_losses": 0,
        "total_profit": 0.0,
        "max_bet_placed": 0,
        "max_losing_streak": 0,
        "start_balance": 0.0,
        "final_balance": 0.0,
    }

    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return default_report  # Or raise error/return {}
    except pd.errors.EmptyDataError:
        print(f"Error: The file {csv_file_path} is empty.")
        return default_report
    except Exception as e:
        print(f"Error reading CSV file {csv_file_path}: {e}")
        return default_report

    if df.empty:
        return default_report

    try:
        # Convert timestamp column to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Convert report_date_str to a date object for comparison
        report_date = pd.to_datetime(report_date_str).date()
    except Exception as e:
        print(f"Error processing date/timestamp: {e}")
        return default_report

    # Filter DataFrame for the given report_date
    # Ensure comparison is between date objects (df['timestamp'].dt.date)
    # Use .copy() to avoid SettingWithCopyWarning
    daily_df = df[df['timestamp'].dt.date == report_date].copy()

    if daily_df.empty:
        print(f"No data found for date: {report_date_str}")
        return default_report

    # Ensure 'outcome' column is treated as string and lowercased for comparison
    daily_df['outcome'] = daily_df['outcome'].astype(str).str.lower()
    daily_df['bet_amount'] = pd.to_numeric(
        daily_df['bet_amount'], errors='coerce').fillna(0)
    daily_df['balance'] = pd.to_numeric(
        daily_df['balance'], errors='coerce').fillna(0)

    # Calculate daily metrics
    total_rounds_played = len(daily_df)
    total_wins = daily_df[daily_df['outcome'] == 'w'].shape[0]
    total_losses = daily_df[daily_df['outcome'] == 'l'].shape[0]

    # Calculate Total Profit for the day
    # Method: End_Balance_of_Day - Start_Balance_of_Day
    # 1. Determine Start Balance for the day
    first_daily_row = daily_df.iloc[0]
    start_balance_for_day = 0.0
    if first_daily_row['outcome'] == 'w':
        # balance_after = balance_before + bet_amount_won
        start_balance_for_day = first_daily_row['balance'] - \
            first_daily_row['bet_amount']
    elif first_daily_row['outcome'] == 'l':
        # balance_after = balance_before - bet_amount_lost
        start_balance_for_day = first_daily_row['balance'] + \
            first_daily_row['bet_amount']
    else:
        # Fallback for other outcomes (e.g., push/draw if bet_amount is 0 or represents stake returned)
        # Assumes for non win/loss, the balance_before is the same as balance_after if bet_amount is 0.
        start_balance_for_day = first_daily_row['balance']

    # 2. Determine End Balance for the day
    end_balance_for_day = daily_df.iloc[-1]['balance']

    # 3. Calculate Total Profit
    total_profit = end_balance_for_day - start_balance_for_day

    # 4. Calculate max loss streak
    max_losing_streak = 0
    current_losing_streak = 0
    for outcome in daily_df['outcome']:
        if outcome in ['l', 'tie']:
            current_losing_streak += 1
        else:
            if current_losing_streak > max_losing_streak:
                max_losing_streak = current_losing_streak
            current_losing_streak = 0
    if current_losing_streak > max_losing_streak:  # Check for a streak ending at the last round
        max_losing_streak = current_losing_streak

    # 5. Calculate max bet placed
    max_bet_placed: int = 0 if daily_df.empty else daily_df['bet_amount'].max()

    return {
        "report_date": report_date_str,
        "total_rounds_played": total_rounds_played,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "total_profit": float(total_profit),
        "max_bet_placed": max_bet_placed,
        "max_losing_streak": max_losing_streak,
        "start_balance": start_balance_for_day,
        "final_balance": end_balance_for_day,
    }


if __name__ == '__main__':
    report = generate_daily_report("data/betting_log.csv", "2025-06-12")
    print(report)
