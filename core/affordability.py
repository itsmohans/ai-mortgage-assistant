from dataclasses import dataclass
from core.amortization import LoanInputs, calculate_monthly_payment


# Industry-standard lending thresholds
FRONT_END_LIMIT = 0.28   # Max housing cost as % of gross income
BACK_END_LIMIT  = 0.43   # Max total debt as % of gross income

@dataclass
class BorrowerProfile:
    """
    Contains borrower financial information needed for affordability analysis.
    Separate from LoanInputs intentionally — borrower profile is about the
    person, LoanInputs is about the loan.
    """
    gross_monthly_income: float    # Before-tax monthly income
    monthly_debts: float           # Existing debts: car, student loans, cards


def calculate_front_end_ratio(profile: BorrowerProfile,
                              inputs: LoanInputs) -> float:
    """
    Front-end ratio = monthly mortgage payment / gross monthly income.
    Lenders want this below 28% (FRONT_END_LIMIT).
    """
    monthly_payment = calculate_monthly_payment(inputs)
    return monthly_payment / profile.gross_monthly_income

def calculate_back_end_ratio(profile: BorrowerProfile,
                              inputs: LoanInputs) -> float:
    """
    Back-end ratio (DTI) = (mortgage + all debts) / gross monthly income.
    Lenders want this below 43% (BACK_END_LIMIT).
    """
    monthly_payment = calculate_monthly_payment(inputs)
    total_monthly_debt = monthly_payment + profile.monthly_debts
    return total_monthly_debt / profile.gross_monthly_income

def maximum_loan_amount(profile: BorrowerProfile,
                         annual_rate: float,
                         term_years: int) -> float:
    """
    Returns the maximum loan principal a borrower qualifies for,
    based on whichever ratio is the binding constraint.
    """
    # Max payment allowed under each ratio
    max_payment_front = profile.gross_monthly_income * FRONT_END_LIMIT
    max_payment_back  = (profile.gross_monthly_income * BACK_END_LIMIT) \
                        - profile.monthly_debts

    # The binding constraint is whichever allows the smaller payment
    max_payment = min(max_payment_front, max_payment_back)

    # Work backwards from max payment to max principal using npf.pv
    import numpy_financial as npf
    monthly_rate = annual_rate / 12
    n_payments   = term_years * 12

    # npf.pv returns negative (present value of outflows), so we negate
    return -npf.pv(monthly_rate, n_payments, max_payment)

def is_loan_affordable(profile: BorrowerProfile,
                        inputs: LoanInputs) -> dict:
    """
    Checks both lending ratios and returns a full affordability verdict.
    """
    front = calculate_front_end_ratio(profile, inputs)
    back  = calculate_back_end_ratio(profile, inputs)

    return {
        "front_end_ratio": round(front, 4),
        "back_end_ratio": round(back, 4),
        "front_end_pass": bool(front <= FRONT_END_LIMIT),
        "back_end_pass": bool(back <= BACK_END_LIMIT),
        "affordable": bool(front <= FRONT_END_LIMIT and back <= BACK_END_LIMIT),
        "front_end_limit": FRONT_END_LIMIT,
        "back_end_limit": BACK_END_LIMIT,
    }

def maximum_loan_amount(profile: BorrowerProfile,
                         annual_rate: float,
                         term_years: int) -> float:
    """
    Returns the maximum loan principal a borrower qualifies for,
    based on whichever ratio is the binding constraint.
    """
    # Max payment allowed under each ratio
    max_payment_front = profile.gross_monthly_income * FRONT_END_LIMIT
    max_payment_back  = (profile.gross_monthly_income * BACK_END_LIMIT) \
                        - profile.monthly_debts

    # The binding constraint is whichever allows the smaller payment
    max_payment = min(max_payment_front, max_payment_back)

    # Work backwards from max payment to max principal using npf.pv
    import numpy_financial as npf
    monthly_rate = annual_rate / 12
    n_payments   = term_years * 12

    # npf.pv returns negative (present value of outflows), so we negate
    return -npf.pv(monthly_rate, n_payments, max_payment)