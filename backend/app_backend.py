# app_backend.py
from fastapi import FastAPI, HTTPException
from schemas import (
    SalaryAdvanceRequestSchema, SalaryAdvanceResponseSchema,
    LoanRequestSchema, LoanResponseSchema, AmortizationEntry
)
import pandas as pd
import math
from datetime import date

# Initialize the FastAPI application
app = FastAPI(
    title="Financial Calculator Backend",
    description="API for calculating salary advances and loan amortizations."
)

@app.post("/calculate_advance", response_model=SalaryAdvanceResponseSchema)
async def calculate_advance(request: SalaryAdvanceRequestSchema):
    """
    Calculates salary advance eligibility and details based on the request.

    - Determines eligibility based on requested amount vs. gross salary.
    - Applies a 5% fee on the approved advance amount.
    - Note: For simplicity, the 'before 25th of month' rule is not
            enforced here as the request date is not part of the schema,
            and pay frequency is not used for this simple advance rule.
    """
    gross_salary = request.gross_salary
    requested_amount = request.requested_advance_amount

    # Basic eligibility check: requested amount cannot exceed gross salary
    if requested_amount > gross_salary:
        return SalaryAdvanceResponseSchema(
            eligible=False,
            max_advance_amount=gross_salary,
            approved_advance_amount=0.0,
            fee_amount=0.0,
            net_payout=0.0,
            message="Requested advance amount cannot exceed your gross salary."
        )

    # All checks passed, approve the requested amount
    approved_amount = requested_amount
    fee_percentage = 0.05  # 5% fee
    fee_amount = round(approved_amount * fee_percentage, 2)
    net_payout = round(approved_amount - fee_amount, 2)

    return SalaryAdvanceResponseSchema(
        eligible=True,
        max_advance_amount=gross_salary, # Max advance is assumed to be gross salary for simplicity
        approved_advance_amount=approved_amount,
        fee_amount=fee_amount,
        net_payout=net_payout,
        message="Salary advance approved."
    )

@app.post("/calculate_loan", response_model=LoanResponseSchema)
async def calculate_loan(request: LoanRequestSchema):
    """
    Calculates loan amortization schedule using Pandas.

    - Computes monthly payment, total repayable, and total interest.
    - Generates a detailed amortization schedule month by month.
    """
    loan_amount = request.loan_amount
    annual_interest_rate = request.annual_interest_rate
    loan_term_months = request.loan_term_months

    # Validate inputs
    if loan_amount <= 0 or annual_interest_rate < 0 or loan_term_months <= 0:
        raise HTTPException(status_code=400, detail="Invalid loan parameters. Amount, rate, and term must be positive.")

    # Convert annual interest rate to monthly decimal rate
    monthly_interest_rate = (annual_interest_rate / 100) / 12

    # Calculate monthly payment using the fixed-rate loan formula
    # M = P [ i(1 + i)^n ] / [ (1 + i)^n – 1]
    # If monthly interest rate is 0, simple division for principal
    if monthly_interest_rate == 0:
        monthly_payment = loan_amount / loan_term_months
    else:
        # Avoid division by zero if (1 + i)^n – 1 is very close to zero
        denominator = ((1 + monthly_interest_rate)**loan_term_months - 1)
        if abs(denominator) < 1e-9: # Check if denominator is effectively zero
            raise HTTPException(status_code=400, detail="Loan calculation impossible with provided parameters (near-zero denominator).")
        monthly_payment = (loan_amount * monthly_interest_rate *
                           (1 + monthly_interest_rate)**loan_term_months) / \
                          denominator

    monthly_payment = round(monthly_payment, 2)

    # Generate amortization schedule using Pandas
    amortization_data = []
    current_balance = loan_amount

    for month in range(1, loan_term_months + 1):
        # Calculate interest for the current month
        interest_payment = round(current_balance * monthly_interest_rate, 2)

        # Calculate principal payment for the current month
        # Ensure principal payment doesn't exceed remaining balance on the last payment
        principal_payment = round(monthly_payment - interest_payment, 2)

        # Adjust last payment to clear exact remaining balance, accounting for rounding
        if month == loan_term_months:
             principal_payment = current_balance


        # Calculate new ending balance
        ending_balance = round(current_balance - principal_payment, 2)
        # Ensure ending balance doesn't go below zero
        if ending_balance < 0 and month == loan_term_months:
            ending_balance = 0.0
        elif ending_balance < 0 and month < loan_term_months: # This shouldn't happen with correct calculation
            raise HTTPException(status_code=500, detail="Loan calculation error: Negative balance before last month.")


        # Append to amortization data
        amortization_data.append({
            "month": month,
            "starting_balance": round(current_balance, 2),
            "interest_payment": interest_payment,
            "principal_payment": principal_payment,
            "monthly_payment": monthly_payment,
            "ending_balance": ending_balance
        })
        current_balance = ending_balance # Update balance for next month

    # Create a Pandas DataFrame from the amortization data
    df_amortization = pd.DataFrame(amortization_data)

    # Ensure last ending balance is exactly zero due to potential floating point inaccuracies
    if not df_amortization.empty:
        df_amortization.loc[df_amortization.index[-1], 'ending_balance'] = 0.0


    # Calculate total interest paid and total repayable amount
    total_interest_paid = round(df_amortization['interest_payment'].sum(), 2)
    total_repayable_amount = round(loan_amount + total_interest_paid, 2)

    # Convert DataFrame records back to Pydantic models for response
    amortization_schedule_response = [AmortizationEntry(**row) for row in df_amortization.to_dict(orient='records')]


    return LoanResponseSchema(
        total_repayable_amount=total_repayable_amount,
        total_interest_paid=total_interest_paid,
        monthly_payment=monthly_payment,
        amortization_schedule=amortization_schedule_response,
        message="Loan calculation complete."
    )
