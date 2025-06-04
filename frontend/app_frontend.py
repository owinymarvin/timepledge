import streamlit as st
import requests

st.set_page_config(page_title="FastAPI + Streamlit App", layout="centered")

st.title("📡 Streamlit ↔ FastAPI Interface")

st.subheader("Send a message to the FastAPI backend")

# Text input
user_input = st.text_input("Enter an item to add to the list:")

# Send data to backend
if st.button("Send to Backend"):
    if user_input:
        try:
            response = requests.post(
                "http://backend:8000/api/send_data",
                json={"item": user_input}
            )
            if response.ok:
                res_json = response.json()
                st.success(res_json["message"])
                st.write("📋 Current Items List:")
                st.write(res_json["items"])
            else:
                st.error("❌ Failed to send data to the backend.")
        except Exception as e:
            st.error(f"🔌 Connection error: {e}")
    else:
        st.warning("⚠️ Please enter an item before sending.")

st.markdown("---")


if st.button("Fetch All Items"):
    try:
        response = requests.get("http://backend:8000/api/data")
        if response.ok:
            st.write("📋 Items from backend:", response.json()["data"])
        else:
            st.error("❌ Failed to fetch data.")
    except Exception as e:
        st.error(f"🔌 Error fetching data: {e}")
