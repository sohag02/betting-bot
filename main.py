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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bettingbot.log"),
        logging.StreamHandler()
    ],
)

config = get_config()


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

    while True:
        if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
            break
        
        # Generate daily report if end of day
        if is_eod():
            if not is_daily_report_generated():
                save_daily_report()
                generate_graphs()

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
        place_bet(driver, bet_amt)
        wait_for_results(driver)

        # check result
        current_result = cast(str, get_last_result(driver))
        if bet_placed_on is not None and current_result == bet_placed_on.value:
            last_bet_status = BetResult.WON
            loss_streak = 0
            logging.info(f"Won the bet of {bet_amt} points")
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

        log_bet(
            BetLog(
                round_id=round_id,
                bet_amount=bet_amt,
                result=current_result,
                outcome=last_bet_status.value,
                balance=cast(int, get_current_balance(driver))
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