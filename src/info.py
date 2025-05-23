import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

result_map = {
    'a': 'D',
    'b': 'T',
    'tie': 'TIE'
}


def get_last_result(driver: uc.Chrome):
    logging.info("Getting last result")

    try:
        last_res = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'casino-video-last-results')]//span[1]"))
        )
        classname = last_res.get_attribute("class")
        classname = classname.replace('result', '')
        return result_map[classname]
    except Exception as e:
        logging.error('Could not get last result')
        logging.error(e)
        return None
    
def get_current_balance(driver: uc.Chrome):
    logging.info("Getting current balance")
    try:
        balance = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[contains(@class, "balance-value") and contains(text(), "pts")]'))
        )
        return int(balance.text.replace("pts: : ", ""))
    except Exception as e:
        logging.error('Could not get current balance')
        logging.error(e)
        return None

def get_round_id(driver: uc.Chrome):
    logging.info("Getting round id")
    try:
        round_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "casino-video-rid")]'))
        )
        return int(round_id.text.replace("Round ID: ", ""))
    except Exception as e:
        logging.error('Could not get round id')
        logging.error(e)
        return None