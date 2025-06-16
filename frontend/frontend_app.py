import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import os

# FastAPI backend URL from environment variable
BASE_URL = os.getenv("BASE_URL", "http://backend:8000")

st.title("Loan and Advance Calculator")

tab1, tab2, tab3, tab4 = st.tabs(["Calculate Loan", "Calculate Advance", "View History", "View Loan Plot"])

with tab1:
    st.header("Calculate Loan")
    with st.form("loan_form"):
        username_loan = st.text_input("Username", value="", key="username_loan")
        gross_salary_loan = st.number_input("Gross Salary ($)", min_value=0.0, key="gross_salary_loan")
        requested_amount_loan = st.number_input("Requested Loan Amount ($)", min_value=0.0, key="requested_amount_loan")
        loan_duration = st.number_input("Loan Duration (Months)", min_value=1, step=1, key="loan_duration")
        loan_payment_frequency = st.selectbox("Payment Frequency", ["monthly", "biweekly"], key="loan_payment_frequency")
        loan_submit = st.form_submit_button("Calculate Loan")

        if loan_submit:
            payload = {
                "username": username_loan,
                "gross_salary": gross_salary_loan,
                "requested_amount": requested_amount_loan,
                "loan_duration": loan_duration,
                "loan_payment_frequency": loan_payment_frequency
            }
            try:
                response = requests.post(f"{BASE_URL}/calculate_loan", json=payload)
                response.raise_for_status()
                result = response.json()
                st.subheader("Loan Calculation Result")
                if result.get("eligible", False):
                    st.success("Loan is eligible!")
                    st.write(f"**Requested Amount**: ${result['requested_amount']}")
                    st.write(f"**Monthly Payment**: ${result['monthly_payment']}")
                    st.write(f"**Total Interest**: ${result['total_interest']}")
                    st.write(f"**Total Payable**: ${result['total_payable']}")
                    st.write("**Repayment Schedule**:")
                    for payment in result["repayment_schedule"]:
                        st.write(f"Month {payment['month']}: Principal=${payment['principal_component']}, Interest=${payment['interest_component']}, Total=${payment['total_monthly_payment']}")
                else:
                    st.error(f"Loan not eligible: {result['reason']}")
            except requests.RequestException as e:
                st.error(f"Error: {e}")

with tab2:
    st.header("Calculate Advance")
    with st.form("advance_form"):
        username_advance = st.text_input("Username", value="", key="username_advance")
        gross_salary_advance = st.number_input("Gross Salary ($)", min_value=0.0, key="gross_salary_advance")
        requested_amount_advance = st.number_input("Requested Advance Amount ($)", min_value=0.0, key="requested_amount_advance")
        advance_submit = st.form_submit_button("Calculate Advance")

        if advance_submit:
            payload = {
                "username": username_advance,
                "gross_salary": gross_salary_advance,
                "requested_amount": requested_amount_advance
            }
            try:
                response = requests.post(f"{BASE_URL}/calculate_advance", json=payload)
                response.raise_for_status()
                result = response.json()
                st.subheader("Advance Calculation Result")
                if result.get("eligible", False):
                    st.success("Advance is eligible!")
                    st.write(f"**Requested Amount**: ${result['requested_amount']}")
                    st.write(f"**Approved Amount**: ${result['approved_amount']}")
                    st.write(f"**Max Advance**: ${result['max_advance']}")
                    st.write(f"**Fee**: ${result['fee']}")
                    st.write(f"**Reason**: {result['reason']}")
                else:
                    st.error(f"Advance not eligible: {result['reason']}")
            except requests.RequestException as e:
                st.error(f"Error: {e}")

with tab3:
    st.header("View User History")
    username_history = st.text_input("Username", value="", key="username_history")
    if st.button("View Loans and Advances", key="view_history_button"):
        try:
            response = requests.get(f"{BASE_URL}/user_loans/{username_history}")
            response.raise_for_status()
            loans = response.json()
            st.subheader("Loan History")
            if loans:
                for loan in loans:
                    st.write(f"**Timestamp**: {loan['timestamp']}")
                    st.write(f"**Eligible**: {loan['eligible']}")
                    st.write(f"**Requested Amount**: ${loan['requested_amount']}")
                    if loan["eligible"]:
                        st.write(f"**Monthly Payment**: ${loan['monthly_payment']}")
                        st.write(f"**Total Payable**: ${loan['total_payable']}")
                    else:
                        st.write(f"**Reason**: {loan['reason']}")
                    st.write("---")
            else:
                st.info("No loans found.")
        except requests.RequestException as e:
            st.error(f"Error fetching loans: {e}")

        try:
            response = requests.get(f"{BASE_URL}/user_advances/{username_history}")
            response.raise_for_status()
            advances = response.json()
            st.subheader("Advance History")
            if advances:
                for advance in advances:
                    st.write(f"**Timestamp**: {advance['timestamp']}")
                    st.write(f"**Eligible**: {advance['eligible']}")
                    st.write(f"**Requested Amount**: ${advance['requested_amount']}")
                    st.write(f"**Max Advance**: ${advance['max_advance']}")
                    if advance["eligible"]:
                        st.write(f"**Approved Amount**: ${advance['approved_amount']}")
                        st.write(f"**Fee**: ${advance['fee']}")
                    st.write(f"**Reason**: {advance['reason']}")
                    st.write("---")
            else:
                st.info("No advances found.")
        except requests.RequestException as e:
            st.error(f"Error fetching advances: {e}")

with tab4:
    st.header("View Loan Repayment Plot")
    username_plot = st.text_input("Username", value="", key="username_plot")
    if st.button("View Loan Plot", key="view_plot_button"):
        try:
            response = requests.get(f"{BASE_URL}/plot_loan/{username_plot}")
            response.raise_for_status()
            result = response.json()
            if "plot" in result:
                base64_string = result["plot"].split(",")[1]
                image_data = base64.b64decode(base64_string)
                image = Image.open(BytesIO(image_data))
                st.image(image, caption=f"Loan Repayment Schedule for {username_plot}")
            else:
                st.error(result.get("error", "Failed to retrieve plot"))
        except requests.RequestException as e:
            st.error(f"Error fetching plot: {e}")