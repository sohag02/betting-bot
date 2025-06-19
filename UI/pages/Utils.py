from datetime import datetime
import streamlit as st
import os

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

st.markdown("#### Last Error Screenshot")
if os.path.exists("internal/screenshot.png"):
    mod_time = os.path.getmtime("internal/screenshot.png")
    st.write(f"Last Updated: {datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')}")
    st.image("internal/screenshot.png")
    with open("internal/screenshot.png", "rb") as file:
        st.download_button(
            label="Download Image",
            data=file,
            file_name="downloaded_image.png",
            mime="image/png"
        )
else:
    st.write("No Screenshot Available")

st.markdown("#### Download Data")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists("data/betting_log.csv"):
        file_size = os.path.getsize("data/betting_log.csv") / 1024  # KB
        mod_time = datetime.fromtimestamp(os.path.getmtime("data/betting_log.csv"))
        
        st.markdown(f"""
        <div class="download-section">
            <div class="file-info">
                📄 <strong>Betting Log CSV</strong><br>
                Size: {file_size:.1f} KB<br>
                Last Updated: {mod_time.strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with open("data/betting_log.csv", "rb") as file:
            st.download_button(
                label="Download Betting Log CSV",
                data=file,
                file_name="betting_log.csv",
                mime="text/csv"
            )
    else:
        st.write("Betting Log CSV Not Found")

with col2:
    if os.path.exists("data/daily_report.csv"):
        file_size = os.path.getsize("data/daily_report.csv") / 1024  # KB
        mod_time = datetime.fromtimestamp(os.path.getmtime("data/daily_report.csv"))
        
        st.markdown(f"""
        <div class="download-section">
            <div class="file-info">
                📄 <strong>Daily Report CSV</strong><br>
                Size: {file_size:.1f} KB<br>
                Last Updated: {mod_time.strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with open("data/daily_report.csv", "rb") as file:
            st.download_button(
                label="Download Daily Report CSV",
                data=file,
                file_name="daily_report.csv",
                mime="text/csv"
            )
    else:
        st.write("Daily Report CSV Not Found")

if os.path.exists("config.ini"):
    file_size = os.path.getsize("config.ini") / 1024  # KB
    mod_time = datetime.fromtimestamp(os.path.getmtime("config.ini"))
    
    st.markdown(f"""
    <div class="download-section">
        <div class="file-info">
            📄 <strong>Config</strong><br>
            Size: {file_size:.1f} KB<br>
            Last Updated: {mod_time.strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.download_button(
        label="Download Config",
        data=open("config.ini", "rb"),
        file_name="config.ini",
        mime="text/plain"
    )
else:
    st.write("Config Not Found")