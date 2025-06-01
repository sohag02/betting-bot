import csv
import logging
import os
import time
from enum import Enum
from typing import cast

import undetected_chromedriver as uc

from src.actions import (place_bet, press_dragon_box, press_tiger_box,
                         wait_for_results)
from src.config import get_config
from src.info import get_current_balance, get_last_result, get_round_id
from src.tg import notify
from src.utils import (BetLog, delay, is_daily_report_generated, is_eod,
                       is_now_in_range, log_bet, save_daily_report, save_summary, generate_graphs)
from demo import init_status_panel, update_demo_balance

config = get_config()

# ANSI escape codes for coloring
RESET = "\033[0m"
BOLD_GREEN = "\033[1;32m"

if config.demo.enabled:
    format = f'{BOLD_GREEN}[DEMO]{RESET} %(asctime)s-[%(levelname)s] %(message)s'
    file_name = "bettingbot_demo.log"
else:
    format = '%(asctime)s-[%(levelname)s] %(message)s'
    file_name = "bettingbot.log"

logging.basicConfig(
    level=logging.INFO,
    format=format,
    handlers=[
        logging.FileHandler(file_name),
        logging.StreamHandler()
    ],
)

class BetType(str, Enum):
    DRAGON = 'D'
    TIGER = 'T'


class BetResult(str, Enum):
    WON = 'W'
    LOST = 'L'
    TIE = 'TIE'


def main():
    logging.info("Starting betting bot")

    # Make sure the log file exists
    os.makedirs("data", exist_ok=True)
    if not os.path.exists('data/betting_log.csv'):
        with open('data/betting_log.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['timestamp', 'round_id', 'bet_amount', 'result', 'outcome', 'balance'])
    
    driver = uc.Chrome()
    driver.get("https://myplay777.com")
    input("Login and Press Enter to continue...")
    driver.get(config.betting.game_link)

    bet_amt = config.betting.minimum_bet
    bet_placed_on : BetType | None = None
    last_bet_status : BetResult | None = None

    loss_streak = 0

    if config.demo.enabled:
        init_status_panel(driver)
        demo_balance = config.demo.assumed_balance
        update_demo_balance(driver, demo_balance)

    while True:
        if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
            break
        
        # Generate daily report if end of day
        if is_eod():
            if not is_daily_report_generated():
                save_daily_report()
                generate_graphs()

        if config.demo.enabled:
            balance = demo_balance
        else:
            balance = get_current_balance(driver)

        if balance and balance < bet_amt:
            logging.info("Not enough balance to bet")
            time.sleep(5)
            break

        if balance and balance < config.notification.balance_threshold:
            notify(f"Balance is below threshold: {balance}")

        last = get_last_result(driver)
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
                bet_placed_on = BetType.DRAGON
        delay()

        round_id = cast(int, get_round_id(driver))
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
        if not config.demo.enabled:
            status = place_bet(driver, bet_amt)
            if not status:
                logging.info("Bet failed, sleeping for 3 seconds")
                time.sleep(3)
                continue
        wait_for_results(driver)

        # check result
        current_result = cast(str, get_last_result(driver))
        if bet_placed_on is not None and current_result == bet_placed_on.value:
            last_bet_status = BetResult.WON
            loss_streak = 0
            logging.info(f"Won the bet of {bet_amt} points")
            if config.demo.enabled:
                demo_balance += bet_amt
                update_demo_balance(driver, demo_balance)
        elif current_result == "TIE":
            last_bet_status = BetResult.TIE
            loss_streak = 0
            logging.info(f"Tied with the last bet of {bet_amt} points")
        else:
            last_bet_status = BetResult.LOST
            loss_streak += 1
            logging.info(f"Lost the bet of {bet_amt} points. Streak: {loss_streak}")
            if loss_streak >= config.notification.loss_streak_threshold:
                notify(f"Loss streak threshold reached: {loss_streak}")
            if config.demo.enabled:
                demo_balance -= bet_amt
                update_demo_balance(driver, demo_balance, "decrease")
        
        if config.demo.enabled:
            final_balance = demo_balance
        else:
            final_balance = get_current_balance(driver)

        log_bet(
            BetLog(
                round_id=round_id,
                bet_amount=bet_amt,
                result=current_result,
                outcome=last_bet_status.value,
                balance=final_balance
            )
        )
        delay()
        save_summary()

    driver.quit()


def run():
    check_interval = 30 * 60  # 30 minutes
    while True:
        sleep = is_now_in_range(config.sleep.start_time, config.sleep.end_time)
        main()
        if not sleep:
            main()
        logging.info("Sleeping")
        time.sleep(check_interval)


if __name__ == "__main__":
    run()