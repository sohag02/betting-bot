from selenium import webdriver
from typing import Literal

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
