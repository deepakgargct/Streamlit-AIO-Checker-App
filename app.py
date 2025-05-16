import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# AIO Checker logic
def check_aio_presence(keyword, domain):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.google.com/search?q={keyword.replace(' ', '+')}")
    time.sleep(3)

    result = {"Keyword": keyword, "AIO Present": "No", "Brand Mentioned": "No"}
    try:
        aio_block = driver.find_element(By.XPATH, "//div[contains(@data-md, 'AI')]")
        result["AIO Present"] = "Yes"
        if domain.lower() in aio_block.text.lower():
            result["Brand Mentioned"] = "Yes"
    except:
        pass

    driver.quit()
    return result

# Streamlit UI
st.title("🔍 Google AI Overview (AIO) Checker")

input_type = st.radio("Choose input type:", ("Upload CSV", "Paste Google Sheet URL"))

df = None
if input_type == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV with 'keyword' column", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
else:
    sheet_url = st.text_input("Paste Google Sheet CSV Export URL")
    if sheet_url:
        try:
            df = pd.read_csv(sheet_url)
        except Exception as e:
            st.error(f"Error loading Google Sheet: {e}")

domain = st.text_input("Enter your domain (e.g., yoursite.com)")

if st.button("Check Keywords") and df is not None and domain:
    if "keyword" not in df.columns:
        st.error("CSV must contain a 'keyword' column.")
    else:
        results = []
        with st.spinner("Checking Google for AIO results..."):
            for kw in df["keyword"]:
                result = check_aio_presence(kw, domain)
                results.append(result)

        results_df = pd.DataFrame(results)
        st.success("✅ Done!")
        st.dataframe(results_df)

        csv = results_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, file_name="aio_results.csv", mime="text/csv")
