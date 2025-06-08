import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Literal
from src.config import get_config
import logging

config = get_config()

def init_status_panel(driver: webdriver.Chrome):
    driver.execute_script("""
        if (!document.getElementById('selenium-status-panel')) {
            const panel = document.createElement('div');
            panel.id = 'selenium-status-panel';
            panel.style.position = 'fixed';
            panel.style.bottom = '10px';
            panel.style.right = '10px';
            panel.style.backgroundColor = 'rgba(0,0,0,0.75)';
            panel.style.color = 'white';
            panel.style.padding = '10px';
            panel.style.borderRadius = '8px';
            panel.style.fontFamily = 'monospace';
            panel.style.fontSize = '14px';
            panel.style.zIndex = 99999;
            panel.textContent = 'Balance: Loading...';
            document.body.appendChild(panel);
        }
    """)

def update_demo_balance(driver, balance: int, change_type: Literal["increase", "decrease"] = "increase"):
    color = "#00b894" if change_type == "increase" else "#d63031"  # green or red

    driver.execute_script(f"""
        const panel = document.getElementById('selenium-status-panel');
        if (panel) {{
            panel.textContent = 'Balance: ${balance}';

            panel.style.transition = 'transform 0.2s ease, background-color 0.4s ease';
            panel.style.transform = 'scale(1.1)';
            panel.style.backgroundColor = '{color}';

            setTimeout(() => {{
                panel.style.transform = 'scale(1)';
                panel.style.backgroundColor = 'rgba(0,0,0,0.75)';
            }}, 300);
        }}
    """)
    save_last_balance(balance)

def is_input_balance_changed():
    if not os.path.exists("internal/input_balance.txt"):
        return True
    
    with open("internal/input_balance.txt", "r") as f:
        input_balance = int(f.read())
        return input_balance != config.demo.assumed_balance
    
def save_input_balance():
    logging.info("Saving demo input balance")
    with open("internal/input_balance.txt", "w") as f:
        f.write(str(config.demo.assumed_balance))

def save_last_balance(balance):
    with open("internal/last_balance.txt", "w") as f:
        f.write(str(balance))

def get_last_demo_balance():
    if os.path.exists("internal/last_balance.txt"):
        with open("internal/last_balance.txt", "r") as f:
            return int(f.read())
    return None

def click_video(driver: webdriver.Chrome):
    logging.debug("Clicking video")
    try:
        video = driver.find_element(By.TAG_NAME, "video")
        video.click()
        logging.debug("Video clicked")
        return True
    except Exception as e:
        logging.debug('Could not click video')