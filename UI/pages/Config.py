import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
from src.config import get_config

config = get_config()

st.set_page_config(page_title="Betting Bot")
st.title("Betting Bot")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        .stAppHeader {display:none;}
        .stMainBlockContainer {padding-top: 0;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

with st.form("config"):
    st.markdown("#### Login")
    use_demo = st.toggle("Use Demo Login", value=config.login.use_demo)

    cola, colb = st.columns(2)
    with cola:
        username = st.text_input("Username", value=config.login.username)
    with colb:
        password = st.text_input("Password", value=config.login.password)

    st.markdown("#### Betting")
    minimum_bet = st.text_input("Minimum Bet Amount", value=config.betting.minimum_bet)
    game_link = st.text_input("Game Link", value=config.betting.game_link)
    st.write("")

    st.markdown("#### Demo Mode")
    enabled = st.toggle("Enabled", value=config.demo.enabled)
    assumed_balance = st.text_input("Assumed Balance", value=config.demo.assumed_balance)

    st.markdown("#### Sleep")
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Start Time", value=config.sleep.start_time)
    with col2:
        end_time = st.time_input("End Time", value=config.sleep.end_time)
    st.write("")

    st.markdown("#### Behaviour")
    col3, col4 = st.columns(2)
    with col3:
        pause_min = st.slider("Pause Secounds", min_value=0, max_value=10, value=config.behaviour.pause_min, key="pause_min")
    with col4:
        pause_max = st.slider("Pause Max Secounds", min_value=0, max_value=10, value=config.behaviour.pause_max, key="pause_max")
    # st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("")


    st.markdown("#### Notification")
    col5, col6 = st.columns(2)
    with col5:
        balance_threshold = st.number_input("Balance Threshold", value=config.notification.balance_threshold, key="balance_threshold", step=100)
    with col6:
        loss_streak_threshold = st.number_input("Loss Streak Threshold", value=config.notification.loss_streak_threshold, key="loss_streak_threshold")
    st.write("")

    st.markdown("#### Telegram")
    api_id = st.text_input("API ID", value=config.telegram.api_id)
    api_hash = st.text_input("API Hash", value=config.telegram.api_hash)
    bot_token = st.text_input("Bot Token", value=config.telegram.bot_token)
    admin_username = st.text_input("Admin Username", value=config.telegram.admin_username)


    submitted = st.form_submit_button("Run")

    if submitted:
        st.write("Configuration saved")
        