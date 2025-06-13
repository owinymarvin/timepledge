import pandas as pd
import math

# --- Helper Functions for Calculations ---
def calculate_monthly_net_salary(gross_salary: float, pay_frequency: str) -> float:
    """
    Calculates the monthly salary based on how often someone is paid. Gross has no taxes yet.
    """
    if pay_frequency.lower() == 'monthly':
        monthly_gross = gross_salary
    elif pay_frequency.lower() == 'bi-weekly':
        # twice a month (after every 2 weeks)
        monthly_gross = gross_salary * (2)
    elif pay_frequency.lower() == 'weekly':
        # 4 times a month (after 1 week)
        monthly_gross = gross_salary * (4)
    else:
        raise ValueError("Invalid pay frequency. Must be 'monthly', 'bi-weekly', or 'weekly'.")
    # Simplified net calculation: 70% of gross
    return monthly_gross * 0.70


def calculate_monthly_payment(
    principal: float,
    annual_rate: float,
    loan_term_months: int
) -> float:
    """
    Calculates the fixed monthly payment for a loan using the amortization formula.
    """
    if annual_rate <= 0:
        return principal / loan_term_months if loan_term_months > 0 else 0

    monthly_rate = (annual_rate / 100) / 12
    # Formula: M = P [ i(1 + i)^n ] / [ (1 + i)^n – 1]
    # Where:
    # M = Monthly payment
    # P = Principal loan amount
    # i = Monthly interest rate
    # n = Number of payments (loan term in months)
    try:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**loan_term_months) / \
                          (((1 + monthly_rate)**loan_term_months) - 1)
    except ZeroDivisionError:
        # This can happen if loan_term_months is 0 or monthly_rate is effectively zero
        monthly_payment = principal / loan_term_months if loan_term_months > 0 else 0
    return monthly_payment


def generate_amortization_schedule(
    principal: float,
    annual_rate: float,
    loan_term_months: int
) -> pd.DataFrame:
    """
    Generates a detailed amortization schedule using Pandas DataFrame.
    """
    schedule_data = []
    remaining_balance = principal
    monthly_rate = (annual_rate / 100) / 12
    monthly_payment = calculate_monthly_payment(principal, annual_rate, loan_term_months)

    if monthly_payment <= 0 and loan_term_months > 0: # Handle edge case where no interest and payment is just principal division
        monthly_payment = principal / loan_term_months

    for month_num in range(1, loan_term_months + 1):
        if remaining_balance <= 0: # Stop if loan is paid off early (due to rounding)
            break

        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment

        # Adjust last payment to precisely clear the remaining balance if necessary
        if month_num == loan_term_months:
            principal_payment = remaining_balance
            monthly_payment = interest_payment + principal_payment

        remaining_balance -= principal_payment

        schedule_data.append({
            "Month": month_num,
            "Starting Balance": round(remaining_balance + principal_payment, 2), # Calculate starting balance for current month
            "Monthly Payment": round(monthly_payment, 2),
            "Interest Paid": round(interest_payment, 2),
            "Principal Paid": round(principal_payment, 2),
            "Ending Balance": round(remaining_balance, 2) if remaining_balance > 0 else 0.00
        })

    df = pd.DataFrame(schedule_data)
    return df