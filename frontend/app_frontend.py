# app_frontend.py
import streamlit as st
import pandas as pd
import requests

# Define the backend URL. In a Docker Compose environment,
# 'backend' is the service name defined in docker-compose.yml.
BACKEND_URL = "http://backend:8000"

st.set_page_config(layout="wide", page_title="FinTech Calculator")

st.title("📊 Advanced Salary & Loan Calculator")
st.markdown("---")

# Instructions & Rules
st.header("Understanding Our Services")
st.markdown("""
Our financial tool helps you plan your salary advances and loans with clear terms.

**💰 Salary Advance Rules:**
-   **Eligibility:** Your requested advance amount cannot exceed your gross monthly salary.
-   **Fee:** A 5% fee is applied to the approved advance amount.
-   **Payout:** You receive the approved amount minus the fee.

**📈 Loan Calculation Rules:**
-   **Interest:** Interest is compounded monthly based on the annual interest rate.
-   **Repayment:** Fixed monthly payments are calculated to amortize the loan over the term.
-   **Schedule:** A detailed amortization schedule is generated, showing principal and interest portions for each payment.
""")
st.markdown("---")

# Use Streamlit tabs to organize the two main sections
tab1, tab2 = st.tabs(["💵 Salary Advance", "🏦 Loan Calculator"])

with tab1:
    # Salary Advance Section
    st.header("💵 Request a Salary Advance")
    with st.form("salary_advance_form"):
        st.subheader("Your Salary Details")
        gross_salary_advance = st.number_input(
            "Enter your Gross Monthly Salary ($)",
            min_value=100.0,
            step=50.0,
            value=1000.0,
            format="%.2f",
            help="Your total salary before deductions per month."
        )
        pay_frequency_advance = st.selectbox(
            "Select your Pay Frequency",
            ['monthly', 'bi-weekly', 'weekly'],
            help="This is for informational purposes for the advance request."
        )

        st.subheader("Advance Request")
        requested_advance_amount = st.number_input(
            "How much advance do you need? ($)",
            min_value=1.0,
            step=10.0,
            value=100.0,
            format="%.2f",
            help="The amount of salary advance you are requesting."
        )

        advance_submitted = st.form_submit_button("Calculate Salary Advance")

        if advance_submitted:
            # Prepare data for the API call
            advance_request_data = {
                "gross_salary": gross_salary_advance,
                "pay_frequency": pay_frequency_advance,
                "requested_advance_amount": requested_advance_amount
            }
            st.spinner("Calculating advance...")
            try:
                # Make POST request to the backend API
                response = requests.post(f"{BACKEND_URL}/calculate_advance", json=advance_request_data)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                advance_response = response.json()

                if advance_response["eligible"]:
                    st.success("✅ Salary Advance Approved!")
                    st.markdown(f"""
                    -   **Approved Amount:** ${advance_response['approved_advance_amount']:.2f}
                    -   **Service Fee (5%):** ${advance_response['fee_amount']:.2f}
                    -   **Net Payout:** ${advance_response['net_payout']:.2f}
                    """)

                    # Display Payout vs Fee using Streamlit's metric and a simple bar chart
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Net Payout", f"${advance_response['net_payout']:.2f}")
                    with col2:
                        st.metric("Service Fee", f"${advance_response['fee_amount']:.2f}")

                    df_advance_summary = pd.DataFrame({
                        'Category': ['Net Payout', 'Service Fee'],
                        'Amount': [advance_response['net_payout'], advance_response['fee_amount']]
                    })
                    # For a visual breakdown like a pie chart, a bar chart is a good alternative
                    st.subheader("Advance Payout Breakdown")
                    st.bar_chart(df_advance_summary.set_index('Category'))

                else:
                    st.error(f"❌ Advance Not Approved: {advance_response['message']}")

            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not reach the backend service. Please ensure the backend is running.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred during the request: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

with tab2:
    # Loan Calculation Section
    st.header("🏦 Apply for a Loan")
    with st.form("loan_form"):
        st.subheader("Loan Details")
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=100.0,
            step=100.0,
            value=5000.0,
            format="%.2f",
            help="The total amount you wish to borrow."
        )
        annual_interest_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.01,
            max_value=50.0,
            step=0.1,
            value=10.0,
            format="%.2f",
            help="The annual interest rate for the loan (e.g., 5.0 for 5%)."
        )
        loan_term_months = st.slider(
            "Loan Term (Months)",
            min_value=1,
            max_value=60, # Up to 5 years
            value=12,
            step=1,
            help="The duration of the loan in months."
        )

        loan_submitted = st.form_submit_button("Calculate Loan Repayment")

        if loan_submitted:
            # Prepare data for the API call
            loan_request_data = {
                "loan_amount": loan_amount,
                "annual_interest_rate": annual_interest_rate,
                "loan_term_months": loan_term_months
            }
            st.spinner("Calculating loan amortization...")
            try:
                # Make POST request to the backend API
                response = requests.post(f"{BACKEND_URL}/calculate_loan", json=loan_request_data)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                loan_response = response.json()

                st.success("✅ Loan Calculation Complete!")
                st.markdown(f"""
                -   **Monthly Payment:** ${loan_response['monthly_payment']:.2f}
                -   **Total Repayable Amount:** ${loan_response['total_repayable_amount']:.2f}
                -   **Total Interest Paid:** ${loan_response['total_interest_paid']:.2f}
                """)

                # Display amortization schedule as a DataFrame
                amortization_df = pd.DataFrame(loan_response['amortization_schedule'])
                amortization_df.columns = [
                    'Month', 'Starting Balance', 'Interest Payment',
                    'Principal Payment', 'Monthly Payment', 'Ending Balance'
                ]
                st.subheader("Amortization Schedule")
                st.dataframe(amortization_df, use_container_width=True)

                # Plot outstanding balance over time using Streamlit's native line chart
                st.subheader("Outstanding Loan Balance Over Time")
                st.line_chart(amortization_df[['Month', 'Ending Balance']].set_index('Month'))

                # Plot principal vs interest over time using Streamlit's native area chart
                st.subheader("Principal vs. Interest Paid Over Time")
                st.area_chart(amortization_df[['Month', 'Principal Payment', 'Interest Payment']].set_index('Month'))


            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not reach the backend service. Please ensure the backend is running.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred during the request: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.info("Developed as a microservice application using Streamlit and FastAPI.")
