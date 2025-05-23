import json
import os

import pandas as pd
from src.config import get_config
from selenium.webdriver.remote.webdriver import WebDriver
import logging
import time
import random
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.analytics.daily_report import generate_daily_report
from src.analytics.summary import calculate_bet_metrics
from src.analytics.graphs import generate_capital_growth_curve, win_loss_pie_chart, bet_size_histogram, profit_per_hour_heatmap

config = get_config()


@dataclass
class BetLog:
    round_id: int
    bet_amount: int
    result: str
    outcome: str
    balance: int


def delay():
    interval = random.randint(
        config.behaviour.pause_min, config.behaviour.pause_max)
    logging.info(f"Sleeping for {interval} seconds")
    time.sleep(interval)


def navigate(driver: WebDriver, url: str):
    driver.execute_script(f"""
        window.history.pushState(null, '', '{url}');
        window.dispatchEvent(new Event('popstate'));
    """)


def log_bet(bet_log: BetLog):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('data/betting_log.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            bet_log.round_id,
            bet_log.bet_amount,
            bet_log.result,
            bet_log.outcome,
            bet_log.balance
        ])

def is_now_in_range(start_str: str, end_str: str) -> bool:
    now = datetime.now().time()
    start = datetime.strptime(start_str, '%H:%M').time()
    end = datetime.strptime(end_str, '%H:%M').time()

    if start <= end:
        # Time range does NOT cross midnight
        return start <= now < end
    else:
        # Time range crosses midnight
        return now >= start or now < end

def is_eod() -> bool:
    return is_now_in_range('00:00', '00:03')

def save_daily_report():
    # today = datetime.now().date().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
    logging.info(f"Generating daily report for {yesterday}")
    report = generate_daily_report("data/betting_log.csv", yesterday)
    logging.info(f"Report: {report}")

    if not os.path.exists('data/daily_report.csv'):
        with open('data/daily_report.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['report_date', 'rounds_played', 'wins', 'losses', 'profit'])
            
    with open('data/daily_report.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            yesterday,
            report["total_rounds_played"],
            report["total_wins"],
            report["total_losses"],
            report["total_profit"]
        ])
    logging.info("Successfully saved daily report")

def is_daily_report_generated() -> bool:
    yesterday = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
    if os.path.exists(f"data/daily_report.csv"):
        with open('data/daily_report.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == yesterday:
                    return True
    return False

def save_summary():
    metrics = calculate_bet_metrics("data/betting_log.csv")
    with open('data/bets_summary.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['metric', 'value'])
        for key, value in metrics.items():
            writer.writerow([key, value])

def generate_graphs():
    logging.info("Generating graphs")
    df = pd.read_csv("data/betting_log.csv", parse_dates=["timestamp"])
    generate_capital_growth_curve(df)
    win_loss_pie_chart(df)
    bet_size_histogram(df)
    profit_per_hour_heatmap(df)
    logging.info("Successfully generated graphs")

if __name__ == "__main__":
    # save_daily_report()
    save_summary()