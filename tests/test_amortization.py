import pytest
from core.amortization import LoanInputs, calculate_monthly_payment, \
    build_amortization_schedule, summarize_loan


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def standard_loan():
    return LoanInputs(principal=400_000, annual_rate=0.065, term_years=30)

@pytest.fixture
def loan_with_extra():
    return LoanInputs(principal=400_000, annual_rate=0.065, term_years=30,
                      extra_monthly_payment=500)

@pytest.fixture
def loan_with_prepayment():
    return LoanInputs(principal=400_000, annual_rate=0.065, term_years=30,
                      prepayment=20_000)


# ── Monthly Payment Tests ─────────────────────────────────────────────────────

def test_monthly_payment_is_positive(standard_loan):
    assert calculate_monthly_payment(standard_loan) > 0

def test_monthly_payment_known_value(standard_loan):
    assert abs(calculate_monthly_payment(standard_loan) - 2528.27) < 0.01

def test_higher_rate_means_higher_payment():
    low_rate = LoanInputs(400_000, 0.05, 30)
    high_rate = LoanInputs(400_000, 0.07, 30)
    assert calculate_monthly_payment(high_rate) > calculate_monthly_payment(low_rate)

def test_prepayment_reduces_monthly_payment(standard_loan, loan_with_prepayment):
    assert calculate_monthly_payment(loan_with_prepayment) < calculate_monthly_payment(standard_loan)


# ── Amortization Schedule Tests ───────────────────────────────────────────────

def test_schedule_has_360_rows_for_30yr(standard_loan):
    schedule = build_amortization_schedule(standard_loan)
    assert len(schedule) == 360

def test_schedule_balance_reaches_zero(standard_loan):
    schedule = build_amortization_schedule(standard_loan)
    assert schedule["ending_balance"].iloc[-1] < 0.01

def test_period_1_interest_is_correct(standard_loan):
    schedule = build_amortization_schedule(standard_loan)
    expected = 400_000 * (0.065 / 12)
    assert abs(schedule.iloc[0]["interest_paid"] - expected) < 0.01

def test_extra_payment_shortens_term(standard_loan, loan_with_extra):
    s1 = build_amortization_schedule(standard_loan)
    s2 = build_amortization_schedule(loan_with_extra)
    assert len(s2) < len(s1)

def test_prepayment_reduces_total_interest(standard_loan, loan_with_prepayment):
    s1 = build_amortization_schedule(standard_loan)
    s2 = build_amortization_schedule(loan_with_prepayment)
    assert s2["interest_paid"].sum() < s1["interest_paid"].sum()


# ── Summary Tests ─────────────────────────────────────────────────────────────

def test_summary_keys_present(standard_loan):
    summary = summarize_loan(standard_loan)
    for key in ["monthly_payment", "total_paid", "total_interest_paid",
                "actual_term_months", "interest_to_principal_ratio"]:
        assert key in summary

def test_total_paid_exceeds_principal(standard_loan):
    summary = summarize_loan(standard_loan)
    assert summary["total_paid"] > standard_loan.principal