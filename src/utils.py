from src.config import get_config
from selenium.webdriver.remote.webdriver import WebDriver
import logging
import time
import random
import csv
from dataclasses import dataclass
from datetime import datetime

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
    with open('bettting_log.csv', 'a', newline='') as csvfile:
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
