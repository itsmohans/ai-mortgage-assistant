import numpy_financial as npf
import pandas as pd
from dataclasses import dataclass,field
from typing import Optional

@dataclass
class LoanInputs:
    """
    Container for all loan parameters.
    Use this instead of passing individual arguments to every function.
    """
    principal: float = 360000.00         # Total loan amount (e.g., 400000.0)
    annual_rate: float = 0.0389        # Decimal form — 6.5% = 0.065
    term_years: int = 25          # 15 or 30
    extra_monthly_payment: float = 0.0   # Optional accelerated payoff
    prepayment: float = 0.0

    @property
    def effective_principal(self) -> float:
        """Principal after upfront prepayment is applied."""
        return self.principal - self.prepayment

def calculate_monthly_payment(inputs: LoanInputs) -> float:
    """
    Calculates the fixed monthly payment (principal + interest only).
    Equivalent to Excel's =PMT(rate/12, term*12, -principal)

    npf.pmt() returns a negative value (cash outflow convention).
    We negate it to return a positive dollar amount.
    """
    monthly_rate = inputs.annual_rate / 12
    n_payments = inputs.term_years * 12
    return -npf.pmt(monthly_rate, n_payments, inputs.effective_principal)

def build_amortization_schedule(inputs: LoanInputs) -> pd.DataFrame:
    """
    Generates a full amortization table, one row per payment period.
    Accounts for extra monthly payments (early payoff).

    Returns a DataFrame with columns:
        period, payment, principal_paid, interest_paid, ending_balance
    """
    monthly_rate = inputs.annual_rate / 12
    base_payment = calculate_monthly_payment(inputs)
    total_payment = base_payment + inputs.extra_monthly_payment

    rows = []
    balance = inputs.effective_principal

    for period in range(1, inputs.term_years * 12 + 1):
        interest_paid = balance * monthly_rate
        principal_paid = total_payment - interest_paid

        # Guard: final payment may be less than a full payment
        if principal_paid > balance:
            principal_paid = balance
            total_payment = principal_paid + interest_paid

        balance -= principal_paid

        rows.append({
            "period": period,
            "payment": round(total_payment, 2),
            "principal_paid": round(principal_paid, 2),
            "interest_paid": round(interest_paid, 2),
            "ending_balance": round(balance, 2),
        })

        if balance <= 0:
            break  # Paid off early due to extra payments

    return pd.DataFrame(rows)

def summarize_loan(inputs: LoanInputs) -> dict:
    """
    Returns key loan metrics as a dictionary.
    Composes the functions above — no duplicated logic.
    """
    schedule = build_amortization_schedule(inputs)
    monthly_payment = calculate_monthly_payment(inputs)

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(schedule["payment"].sum(), 2),
        "total_interest_paid": round(schedule["interest_paid"].sum(), 2),
        "actual_term_months": len(schedule),
        "interest_to_principal_ratio": round(
            schedule["interest_paid"].sum() / inputs.effective_principal, 4
        ),
    }