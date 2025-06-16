from pydantic import BaseModel
from datetime import datetime
import pandas as pd

class AdvanceSchema(BaseModel):
    timestamp: datetime = datetime.now()
    username: str
    gross_salary: float
    requested_amount: float

    @property
    def net_salary(self) -> float:
        return self.gross_salary * 0.9

    def compute_advance(self):
        eligible = self.requested_amount <= self.net_salary
        fee = self.requested_amount * 0.15 if eligible else 0
        approved = self.requested_amount if eligible else 0
        reason = "Request less than net salary" if eligible else "Request exceeds net salary."

        return {
            "timestamp": self.timestamp.isoformat(),
            "username": self.username, 
            "eligible": eligible,
            "requested_amount": self.requested_amount,
            "max_advance": round(self.net_salary, 2),
            "approved_amount": approved,
            "fee": round(fee, 2),
            "reason": reason
        }



class LoanSchema(BaseModel):
    timestamp: datetime = datetime.now()
    username: str
    gross_salary: float
    requested_amount: float
    loan_duration: int 
    loan_payment_frequency: str

    @property
    def net_salary(self) -> float:
        return self.gross_salary * 0.9

    def compute_loan(self):
        eligible = self.requested_amount <= (self.gross_salary * 5)
        if not eligible:
            return {
                "timestamp": self.timestamp.isoformat(),
                "username": self.username, 
                "eligible": False,
                "requested_amount": self.requested_amount,
                "reason": "Loan exceeds 5 × gross salary",
                "repayment_schedule": []
            }

        principal = self.requested_amount
        annual_interest_rate = 0.15
        months = self.loan_duration

        monthly_interest = (principal * annual_interest_rate) / 12
        monthly_principal = principal / months
        monthly_payment = monthly_principal + monthly_interest
        total_interest = monthly_interest * months
        total_payable = principal + total_interest

        schedule = []
        for i in range(1, months + 1):
            schedule.append({
                "month": i,
                "principal_component": round(monthly_principal, 2),
                "interest_component": round(monthly_interest, 2),
                "total_monthly_payment": round(monthly_payment, 2)
            })

        df_schedule = pd.DataFrame(schedule)

        return {
            "timestamp": self.timestamp.isoformat(),
            "username": self.username, 
            "eligible": True,
            "requested_amount": principal,
            "loan_duration": months,
            "loan_payment_frequency": self.loan_payment_frequency,
            "annual_interest_rate": annual_interest_rate,
            "total_interest": round(total_interest, 2),
            "total_payable": round(total_payable, 2),
            "monthly_payment": round(monthly_payment, 2),
            "repayment_schedule": schedule,
            "schedule_df": df_schedule
        }