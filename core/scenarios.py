from dataclasses import dataclass
from core.amortization import LoanInputs, build_amortization_schedule, \
    calculate_monthly_payment, summarize_loan

def compare_loan_terms(principal: float,
                        annual_rate: float,
                        term_a_years: int = 30,
                        term_b_years: int = 15) -> dict:
    """
    Compares two loan terms side by side.
    Default: 30yr vs 15yr on the same principal and rate.
    """
    loan_a = LoanInputs(principal=principal, annual_rate=annual_rate,
                        term_years=term_a_years)
    loan_b = LoanInputs(principal=principal, annual_rate=annual_rate,
                        term_years=term_b_years)

    summary_a = summarize_loan(loan_a)
    summary_b = summarize_loan(loan_b)

    return {
        f"term_{term_a_years}yr": summary_a,
        f"term_{term_b_years}yr": summary_b,
        "monthly_payment_difference": round(
            summary_a["monthly_payment"] - summary_b["monthly_payment"], 2
        ),
        "interest_saved":  round(
            summary_a["total_interest_paid"] - summary_b["total_interest_paid"], 2
        ),
    }

def extra_payment_impact(inputs: LoanInputs,
                          extra_payment: float) -> dict:
    """
    Compares base loan vs same loan with extra monthly payment.
    Shows months saved and total interest saved.
    """
    base_inputs  = LoanInputs(
        principal=inputs.principal,
        annual_rate=inputs.annual_rate,
        term_years=inputs.term_years
    )
    extra_inputs = LoanInputs(
        principal=inputs.principal,
        annual_rate=inputs.annual_rate,
        term_years=inputs.term_years,
        extra_monthly_payment=extra_payment
    )

    base_summary  = summarize_loan(base_inputs)
    extra_summary = summarize_loan(extra_inputs)

    months_saved = (base_summary["actual_term_months"]
                    - extra_summary["actual_term_months"])

    return {
        "base":             base_summary,
        "with_extra":       extra_summary,
        "extra_payment":    extra_payment,
        "months_saved":     months_saved,
        "years_saved":      round(months_saved / 12, 1),
        "interest_saved":   round(
            base_summary["total_interest_paid"]
            - extra_summary["total_interest_paid"], 2
        ),
    }


def refinance_analysis(current_balance: float,
                        current_rate: float,
                        current_remaining_months: int,
                        new_rate: float,
                        new_term_years: int,
                        closing_costs: float) -> dict:
    """
    Calculates whether refinancing makes financial sense.
    Break-even = months until monthly savings cover closing costs.
    """
    current_loan = LoanInputs(
        principal=current_balance,
        annual_rate=current_rate,
        term_years=current_remaining_months // 12
    )
    new_loan = LoanInputs(
        principal=current_balance,
        annual_rate=new_rate,
        term_years=new_term_years
    )

    current_payment = calculate_monthly_payment(current_loan)
    new_payment     = calculate_monthly_payment(new_loan)
    monthly_savings = current_payment - new_payment

    # Avoid division by zero if new rate is higher
    if monthly_savings <= 0:
        break_even_months = None
    else:
        break_even_months = round(closing_costs / monthly_savings)

    return {
        "current_payment":   round(current_payment, 2),
        "new_payment":       round(new_payment, 2),
        "monthly_savings":   round(monthly_savings, 2),
        "closing_costs":     closing_costs,
        "break_even_months": break_even_months,
        "break_even_years":  round(break_even_months / 12, 1)
                             if break_even_months else None,
        "worth_refinancing": break_even_months is not None
                             and break_even_months < (new_term_years * 12),
    }