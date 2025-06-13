# schemas.py
from pydantic import BaseModel
from typing import Literal, List, Dict

"""
Pydantic schemas to define the structure of request and response bodies
for the FastAPI backend. This ensures type safety and provides automatic
data validation.
"""

class SalaryAdvanceRequestSchema(BaseModel):
    """
    Defines the structure for a salary advance request.
    """
    gross_salary: float  # User's gross monthly salary
    pay_frequency: Literal['monthly', 'bi-weekly', 'weekly'] # User's pay frequency
    requested_advance_amount: float # Amount the user wishes to advance


class SalaryAdvanceResponseSchema(BaseModel):
    """
    Defines the structure for the salary advance calculation response.
    """
    eligible: bool # True if the advance is approved, False otherwise
    max_advance_amount: float # The maximum amount the user could request
    approved_advance_amount: float # The actual approved amount (can be less than requested)
    fee_amount: float # The fee charged on the approved advance
    net_payout: float # The amount the user will receive after fees
    message: str # A message explaining the eligibility or outcome


class LoanRequestSchema(BaseModel):
    """
    Defines the structure for a loan request.
    """
    loan_amount: float # Total amount of the loan requested
    annual_interest_rate: float # Annual interest rate (e.g., 5.0 for 5%)
    loan_term_months: int # Duration of the loan in months


class AmortizationEntry(BaseModel):
    """
    Defines the structure for a single entry in the amortization schedule.
    """
    month: int # Month number
    starting_balance: float # Balance at the beginning of the month
    interest_payment: float # Portion of the payment applied to interest
    principal_payment: float # Portion of the payment applied to principal
    monthly_payment: float # Total monthly payment (principal + interest)
    ending_balance: float # Balance at the end of the month


class LoanResponseSchema(BaseModel):
    """
    Defines the structure for the loan calculation response, including
    the full amortization schedule.
    """
    total_repayable_amount: float # Total amount to be repaid over the loan term
    total_interest_paid: float # Total interest paid over the loan term
    monthly_payment: float # Regular monthly payment amount
    # List of AmortizationEntry objects representing the loan's schedule
    amortization_schedule: List[AmortizationEntry]
    message: str # A message regarding the loan approval or details
