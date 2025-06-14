import csv
import logging
import os
import time
from enum import Enum
from typing import cast

import undetected_chromedriver as uc

# Assuming src imports are in the correct path
from src.demo import (get_last_demo_balance, init_status_panel,
                      is_input_balance_changed, save_input_balance,
                      save_last_balance, update_demo_balance, click_video)
from src.actions import (place_bet, press_dragon_box, press_tiger_box,
                       wait_for_results)
from src.config import get_config
from src.info import get_current_balance, get_last_result, get_round_id
from src.tg import notify, send_sync
from src.utils import (BetLog, delay, generate_graphs,
                       is_daily_report_generated, is_eod, is_now_in_range,
                       log_bet, save_daily_report, save_summary, reconnect)
from src.login import login

config = get_config()

# Suppress Selenium and undetected_chromedriver logs
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

# ANSI escape codes for coloring
RESET = "\033[0m"
BOLD_GREEN = "\033[1;32m"

if config.demo.enabled:
    log_format = f'{BOLD_GREEN}[DEMO]{RESET} %(asctime)s-[%(levelname)s] %(message)s'
    file_name = "bettingbot_demo.log"
else:
    log_format = '%(asctime)s-[%(levelname)s] %(message)s'
    file_name = "bettingbot.log"

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
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
    """Main function to initialize and run the betting bot."""
    logging.info("Starting a new bot session.")
    
    # Initialize driver to None to ensure it exists for the finally block
    driver = None
    try:
        os.makedirs("internal", exist_ok=True)
        if is_input_balance_changed():
            logging.info("Input Demo balance changed in config")
            save_input_balance()

        os.makedirs("data", exist_ok=True)
        if not os.path.exists('data/betting_log.csv'):
            with open('data/betting_log.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'round_id', 'bet_amount', 'result', 'outcome', 'balance'])

        options = uc.ChromeOptions()
        options.add_argument("--log-level=3")
        driver = uc.Chrome(options=options)
        driver.get(config.betting.site_link)
        login(driver)
        driver.get(config.betting.game_link)

        bet_amt = config.betting.minimum_bet
        bet_placed_on: BetType | None = None
        last_bet_status: BetResult | None = None
        loss_streak = 0
        demo_balance = 0

        if config.demo.enabled:
            init_status_panel(driver)
            demo_balance = config.demo.assumed_balance if is_input_balance_changed() else get_last_demo_balance()
            update_demo_balance(driver, demo_balance)
            logging.info(f"Using Demo balance: {demo_balance}")

        while True:
            if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
                logging.info("Entering sleep period.")
                break # Break the inner loop to proceed to finally block and quit driver

            if is_eod() and not is_daily_report_generated():
                save_daily_report()
                generate_graphs()

            reconnect(driver)
            balance = demo_balance if config.demo.enabled else get_current_balance(driver)
            
            if config.demo.enabled:
                click_video(driver)

            if balance and balance < bet_amt:
                logging.warning("Insufficient balance for the next bet. Waiting...")
                time.sleep(30) # Wait longer if balance is low
                continue

            if balance and balance < config.notification.balance_threshold:
                try:
                    send_sync(f"Balance is below threshold: {balance}")
                except Exception as e:
                    logging.error(f'Failed to send balance notification: {e}')

            last_result = get_last_result(driver)
            time.sleep(5)

            if last_result == "D":
                press_dragon_box(driver)
                bet_placed_on = BetType.DRAGON
            elif last_result == "T":
                press_tiger_box(driver)
                bet_placed_on = BetType.TIGER
            else: # Last result was a Tie
                if not bet_placed_on: # First bet after a Tie
                    bet_placed_on = BetType.DRAGON
                
                if bet_placed_on == BetType.DRAGON:
                    press_dragon_box(driver)
                else: # Bet on Tiger
                    press_tiger_box(driver)
            delay()

            round_id = cast(int, get_round_id(driver))
            logging.info(f"Round ID: {round_id}")

            if last_bet_status == BetResult.LOST:
                bet_amt *= 2
            elif last_bet_status == BetResult.WON:
                bet_amt = config.betting.minimum_bet

            if not config.demo.enabled and not place_bet(driver, bet_amt):
                logging.warning("Bet failed, skipping round.")
                time.sleep(3)
                continue
            
            wait_for_results(driver)
            current_result = cast(str, get_last_result(driver))

            if bet_placed_on and current_result == bet_placed_on.value:
                last_bet_status = BetResult.WON
                loss_streak = 0
                logging.info(f"WON bet of {bet_amt} points.")
                if config.demo.enabled:
                    demo_balance += bet_amt
                    update_demo_balance(driver, demo_balance)
                    click_video(driver)
            elif current_result == "TIE":
                last_bet_status = BetResult.TIE
                logging.info(f"TIE on bet of {bet_amt} points.")
            else:
                last_bet_status = BetResult.LOST
                loss_streak += 1
                logging.info(f"LOST bet of {bet_amt} points. Streak: {loss_streak}")
                if loss_streak >= config.notification.loss_streak_threshold:
                    try:
                        send_sync(f"Loss streak reached: {loss_streak}")
                    except Exception as e:
                        logging.error(f'Failed to send loss streak notification: {e}')
                if config.demo.enabled:
                    demo_balance -= bet_amt
                    update_demo_balance(driver, demo_balance, "decrease")
            
            reconnect(driver)
            final_balance = demo_balance if config.demo.enabled else get_current_balance(driver)
            log_bet(
                BetLog(
                    round_id=round_id, bet_amount=bet_amt, result=current_result,
                    outcome=last_bet_status.value, balance=final_balance
                )
            )
            delay()
            save_summary()

    finally:
        # The finally block ensures this runs, even if an error occurs above.
        if driver:
            logging.info("Closing browser instance.")
            driver.quit()

def run():
    """Wrapper function to manage execution, sleep, and restarts."""
    check_interval = 2 * 60  # 2 minutes
    while True:
        try:
            if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
                logging.info(f"Currently in sleep period. Checking again in {check_interval // 60} minutes.")
                time.sleep(check_interval)
                continue
            
            # If not in sleep period, run the main bot logic.
            # main() will now handle its own setup and guaranteed cleanup.
            main()

        except Exception as e:
            # This will catch errors from main() after its finally block has run.
            logging.critical(f"A critical error occurred in the main session: {e}", exc_info=True)
            logging.error("Restarting the bot in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    run()