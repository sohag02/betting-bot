import csv
import datetime
import os
import time
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from src.config import get_config
import logging
from enum import Enum

from src.info import get_last_result, get_current_balance, get_round_id
from src.actions import press_dragon_box, press_tiger_box, place_bet, wait_for_results
from src.utils import BetLog, delay, log_bet, is_now_in_range

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bettingbot.log"),
        logging.StreamHandler()
    ],
)

config = get_config()

class BetType(Enum):
    DRAGON = 'D'
    TIGER = 'T'

class BetResult(Enum):
    WON = 'W'
    LOST = 'L'
    TIE = 'TIE'


def main():
    logging.info("Starting betting bot")

    # Make sure the log file exists
    if not os.path.exists('bettting_log.csv'):
        with open('bettting_log.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'round_id', 'bet_amount', 'result', 'outcome', 'balance'])
    return

    driver = uc.Chrome()
    driver.get("https://myplay777.com")
    input("Login and Press Enter to continue...")
    driver.get(config.betting.game_link)

    bet_amt = config.betting.minimum_bet
    bet_placed_on = None # BetType
    last_bet_status = None # BetResult

    while True:
        if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
            break

        balance = get_current_balance(driver)

        if balance < bet_amt:
            logging.info("Not enough balance to bet")
            time.sleep(5)
            break
        
        last = get_last_result(driver)
        print(last)
        time.sleep(5)

        if last == "D":
            press_dragon_box(driver)
            bet_placed_on = BetType.DRAGON
        elif last == "T":
            press_tiger_box(driver)
            bet_placed_on = BetType.TIGER
        else:
            # Last result is tie
            if bet_placed_on:
                if bet_placed_on == BetType.DRAGON:
                    press_dragon_box(driver)
                elif bet_placed_on == BetType.TIGER:
                    press_tiger_box(driver)
            else:
                # If this is first bet, bet on dragon
                press_dragon_box(driver)
                
        round_id = get_round_id(driver)
        logging.info(f"Round ID : {round_id}")

        # calculte bet amount
        if last_bet_status == BetResult.WON:
            # Reset bet amount
            bet_amt = config.betting.minimum_bet
        elif last_bet_status == BetResult.TIE:
            # keep bet amount same
            bet_amt = bet_amt
        elif last_bet_status == BetResult.LOST:
            bet_amt = bet_amt * 2

        # place bet
        place_bet(driver, bet_amt)
        wait_for_results(driver)

        # check result
        current_result = get_last_result(driver)
        if current_result == bet_placed_on.value:
            last_bet_status = BetResult.WON
            logging.info(f"Won the bet of {bet_amt} points")
        elif current_result == "TIE":
            last_bet_status = BetResult.TIE
            logging.info(f"Tied with the last bet of {bet_amt} points")
        else:
            last_bet_status = BetResult.LOST
            logging.info(f"Lost the bet of {bet_amt} points")

        
        log_bet(
            BetLog(
                round_id=round_id,
                bet_amount=bet_amt,
                result=current_result,
                outcome=last_bet_status.value,
                balance=get_current_balance(driver)
            )
        )
        delay()

    driver.quit()


if __name__ == "__main__":
    check_interval = 30*60 # 30 minutes
    while True:
        sleep = is_now_in_range(config.sleep.start_time, config.sleep.end_time)
        if not sleep:
            main()
        logging.info("Sleeping")
        time.sleep(check_interval)
