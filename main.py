import csv
import logging
import os
import time
from enum import Enum
from typing import Optional

import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver

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

# Configure logging based on demo mode
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


class BetType(Enum):
    """Enum for bet types with string values."""
    DRAGON = 'D'
    TIGER = 'T'


class BetResult(Enum):
    """Enum for bet results."""
    WON = 'W'
    LOST = 'L'
    TIE = 'TIE'


class BettingBot:
    """Main betting bot class to encapsulate bot logic."""
    
    def __init__(self):
        self.driver: Optional[WebDriver] = None
        self.bet_amt: int = config.betting.minimum_bet
        self.bet_placed_on: Optional[BetType] = None
        self.last_bet_status: Optional[BetResult] = None
        self.loss_streak: int = 0
        self.demo_balance: float = 0.0
        self.on_break = False

        self.start_time = time.time()
        
    def setup_directories_and_files(self) -> None:
        """Create necessary directories and files."""
        os.makedirs("internal", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        if is_input_balance_changed():
            logging.info("Input Demo balance changed in config")
            save_input_balance()
        
        # Create betting log CSV if it doesn't exist
        if not os.path.exists('data/betting_log.csv'):
            with open('data/betting_log.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'round_id', 'bet_amount', 'result', 'outcome', 'balance'])
    
    def initialize_driver(self) -> WebDriver:
        """Initialize and configure Chrome driver."""
        options = uc.ChromeOptions()
        options.add_argument("--log-level=3")
        return uc.Chrome(options=options)
    
    def login(self) -> None:
        """Login to the site."""
        self.driver.get(config.betting.site_link)
        login(self.driver)
        self.driver.get(config.betting.game_link)
    
    def setup_demo_mode(self) -> None:
        """Setup demo mode if enabled."""
        if not config.demo.enabled or not self.driver:
            return
            
        init_status_panel(self.driver)
        self.demo_balance = (config.demo.assumed_balance 
                           if is_input_balance_changed() 
                           else get_last_demo_balance())
        update_demo_balance(self.driver, self.demo_balance)
        logging.info(f"Using Demo balance: {self.demo_balance}")
    
    def get_current_balance(self) -> Optional[float]:
        """Get current balance (demo or real)."""
        if not self.driver:
            return None
            
        return (self.demo_balance 
                if config.demo.enabled 
                else get_current_balance(self.driver))
    
    def check_balance_threshold(self, balance: float) -> None:
        """Check if balance is below threshold and send notification."""
        if balance < config.notification.balance_threshold:
            try:
                send_sync(f"Balance is below threshold: {balance}")
            except Exception as e:
                logging.error(f'Failed to send balance notification: {e}')
    
    def determine_bet_choice(self, last_result: str) -> BetType:
        """Determine which bet to place based on last result and strategy."""
        if last_result == "D":
            return BetType.DRAGON
        elif last_result == "T":
            return BetType.TIGER
        else:  # Last result was a Tie
            # If no previous bet or first bet after tie, default to Dragon
            return self.bet_placed_on or BetType.DRAGON
    
    def place_bet_action(self, bet_choice: BetType) -> None:
        """Place the actual bet based on choice."""
        if not self.driver:
            return
            
        if bet_choice == BetType.DRAGON:
            press_dragon_box(self.driver)
        else:
            press_tiger_box(self.driver)
        
        self.bet_placed_on = bet_choice
    
    def calculate_bet_amount(self) -> None:
        """Calculate bet amount based on last result."""
        if self.last_bet_status == BetResult.LOST:
            self.bet_amt *= 2
        elif self.last_bet_status == BetResult.WON:
            self.bet_amt = config.betting.minimum_bet
    
    def process_bet_result(self, current_result: str) -> None:
        """Process the result of the current bet."""
        if not self.bet_placed_on:
            return
            
        if current_result == self.bet_placed_on.value:
            self._handle_win()
        elif current_result == "TIE":
            self._handle_tie()
        else:
            self._handle_loss()
    
    def _handle_win(self) -> None:
        """Handle winning bet."""
        self.last_bet_status = BetResult.WON
        self.loss_streak = 0
        logging.info(f"WON bet of {self.bet_amt} points.")
        
        if config.demo.enabled and self.driver:
            self.demo_balance += self.bet_amt
            update_demo_balance(self.driver, self.demo_balance)
            click_video(self.driver)
    
    def _handle_tie(self) -> None:
        """Handle tie result."""
        self.last_bet_status = BetResult.TIE
        logging.info(f"TIE on bet of {self.bet_amt} points.")
    
    def _handle_loss(self) -> None:
        """Handle losing bet."""
        self.last_bet_status = BetResult.LOST
        self.loss_streak += 1
        logging.info(f"LOST bet of {self.bet_amt} points. Streak: {self.loss_streak}")
        
        # Send notification if loss streak threshold reached
        if self.loss_streak >= config.notification.loss_streak_threshold:
            try:
                send_sync(f"Loss streak reached: {self.loss_streak}")
            except Exception as e:
                logging.error(f'Failed to send loss streak notification: {e}')
        
        if config.demo.enabled and self.driver:
            self.demo_balance -= self.bet_amt
            update_demo_balance(self.driver, self.demo_balance, "decrease")
    
    def run_betting_cycle(self) -> bool:
        """Run a single betting cycle. Returns False if should break main loop."""
        if not self.driver:
            return False
            
        # Check if in sleep period
        if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
            logging.info("Entering sleep period.")
            return False
        
        # Generate daily report if needed
        if is_eod() and not is_daily_report_generated():
            save_daily_report()
            generate_graphs()
        
        reconnect(self.driver)
        balance = self.get_current_balance()
        
        if config.demo.enabled:
            click_video(self.driver)
        
        # Check if sufficient balance
        if balance is None or balance < self.bet_amt:
            logging.warning("Insufficient balance for the next bet. Waiting...")
            time.sleep(30)
            return True
        
        self.check_balance_threshold(balance)
        
        # Get last result and determine bet
        last_result = get_last_result(self.driver)
        time.sleep(5)
        
        bet_choice = self.determine_bet_choice(last_result)
        self.place_bet_action(bet_choice)
        delay()
        
        # Get round ID
        round_id = get_round_id(self.driver)
        if round_id is None:
            logging.warning("Could not get round ID, skipping round.")
            return True
        
        logging.info(f"Round ID: {round_id}")
        
        # Calculate and place bet
        self.calculate_bet_amount()
        
        if not config.demo.enabled and not place_bet(self.driver, self.bet_amt):
            logging.warning("Bet failed, skipping round.")
            time.sleep(3)
            return True
        
        # Wait for results and process
        wait_for_results(self.driver)
        current_result = get_last_result(self.driver)
        
        if current_result is None:
            logging.warning("Could not get current result, skipping round.")
            return True
        
        self.process_bet_result(current_result)
        
        # Log bet and save summary
        reconnect(self.driver)
        final_balance = self.get_current_balance()
        
        if final_balance is not None and self.last_bet_status:
            log_bet(
                BetLog(
                    round_id=round_id,
                    bet_amount=self.bet_amt,
                    result=current_result,
                    outcome=self.last_bet_status.value,
                    balance=final_balance
                )
            )
        
        delay()
        save_summary()

        # Check if we should take a break
        if time.time() - self.start_time > config.break_options.interval and config.break_options.enabled:
            # Take a break if there is no loss streak
            if self.loss_streak == 0:
                self.on_break = True
                return False

        return True
    
    def run_main_session(self) -> None:
        """Run the main betting session."""
        logging.info("Starting a new bot session.")

        try:
            self.setup_directories_and_files()
            self.driver = self.initialize_driver()
            self.login()
            self.setup_demo_mode()

            # Main betting loop
            while self.run_betting_cycle():
                pass  # Continue until run_betting_cycle returns False

        except Exception as e:
            logging.error("Error in main session", exc_info=True)
            raise
        finally:
            if self.driver:
                logging.info("Closing browser instance.")
                self.driver.quit()
                self.driver = None
                if self.on_break:
                    logging.info("Taking a break...")
                    time.sleep(config.break_options.duration)
                    self.on_break = False


def run_bot() -> None:
    """Main entry point to run the betting bot with error handling and restarts."""
    check_interval = 2 * 60  # 2 minutes
    
    while True:
        try:
            if is_now_in_range(config.sleep.start_time, config.sleep.end_time):
                logging.info(f"Currently in sleep period. Checking again in {check_interval // 60} minutes.")
                time.sleep(check_interval)
                continue
            
            # Create new bot instance and run
            bot = BettingBot()
            bot.run_main_session()
            
        except Exception as e:
            # logging.critical(f"A critical error occurred: {e}", exc_info=True)
            logging.error("Restarting the bot in 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    run_bot()