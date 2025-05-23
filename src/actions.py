import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.info import result_map
from typing import cast
from src.utils import delay

def press_dragon_box(driver: uc.Chrome):
    logging.info("Pressing dragon box")
    try:
        btn = driver.find_element(By.XPATH, "//div[contains(@class, 'dragon-box')]")
        if 'suspended' in cast(str, btn.get_attribute('class')):
            time.sleep(1)
            press_dragon_box(driver)
        else:
            btn.click()
    except Exception as e:
        logging.error('Could not press dragon box')
        # logging.error(e)
        raise e

def press_tiger_box(driver: uc.Chrome):
    logging.info("Pressing tiger box")
    try:
        btn = driver.find_element(By.XPATH, "//div[contains(@class, 'tiger-box')]")
        if 'suspended' in cast(str, btn.get_attribute('class')):
            time.sleep(1)
            press_tiger_box(driver)
        else:
            btn.click()
    except Exception as e:
        logging.error('Could not press tiger box')
        # logging.error(e)
        raise e
    
def verify_bet(driver: uc.Chrome):
    logging.info("Verifying bet")
    try:
        toast = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="toast-body"]'))
        )
        if 'Bet placed Sucessfully' in toast.text:
            return True
        else:
            return False
    except Exception as e:
        logging.error('Could not verify bet')

def place_bet(driver: uc.Chrome, amount: int):
    logging.info(f"Placing bet of amount : {amount}")
    try:
        bet = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@id="placebetAmountWeb"]'))
        )
        bet.send_keys(str(amount))
        time.sleep(1)
        submit = driver.find_element(By.XPATH, '//div[@class="casino-place-bet-action-buttons"]//button[@class="btn btn-primary"]')
        delay()
        submit.click()
        if verify_bet(driver):
            logging.info(f"Bet placed successfully of amount : {amount}")
        else:
            logging.error("Could not place bet")
    except Exception as e:
        logging.error('Could not place bet')
        # logging.error(e)
        raise e

def extract_results(driver: uc.Chrome) -> list[str] | None:
    """Extract the current results from the page"""
    try:
        wait = WebDriverWait(driver, 10)
        results_container = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "casino-video-last-results"))
        )
        
        # Find all result spans
        result_spans = results_container.find_elements(By.CSS_SELECTOR, "span.resulta, span.resultb, span.resulttie")
        
        results = []
        for span in result_spans:
            # Get the text content and the class to determine type
            text = cast(str, span.get_attribute('class')).replace('result', '')
            result_type = result_map[text]
            results.append(result_type)
        
        return results
        
    except TimeoutException:
        print("Timeout waiting for results container")
        return None
    except NoSuchElementException:
        print("Could not find results elements")
        return None
    
def wait_for_results(driver: uc.Chrome):
    logging.info("Waiting for results")
    try:
        # WebDriverWait(driver, 25).until(
        #     EC.presence_of_element_located(
        #         (By.CLASS_NAME, "base-timer__label green"))
        # )
        prev_results: list[str] | None = None
        while True:
            results = extract_results(driver)
            if prev_results and prev_results != results:
                logging.info(f'Got results : {results}')
                break
            time.sleep(1)
            prev_results = results

    except Exception as e:
        logging.error('Could not wait for results')