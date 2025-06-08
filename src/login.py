import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.config import get_config
from src.utils import delay
import time

config = get_config()

def close_modal(driver: uc.Chrome):
    try:
        close_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "close-home-modal"))
        )
        close_btn.click()
        delay()
    except Exception as e:
        pass


def login(driver: uc.Chrome):
    logging.info(f"Logging in with username: {config.login.username}")
    login_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-box"))
    )
    login_btn = login_box.find_element(
        By.XPATH, "//button[@class='btn btn-primary ml-1' and normalize-space(text())='Login']")
    login_btn.click()
    delay()
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Username']"))
    )
    username.send_keys(config.login.username)
    delay()
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Password']"))
    )
    password.send_keys(config.login.password)
    delay()
    login_sub = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and normalize-space(text())='Login']"))
    )
    login_sub.click()
    delay()
    # input("Login and Press Enter to continue...")
    logging.info("Login successful")
    close_modal(driver)