import pytest
from core.amortization import LoanInputs
from core.affordability import (
    BorrowerProfile, calculate_front_end_ratio, calculate_back_end_ratio,
    is_loan_affordable, maximum_loan_amount,
    FRONT_END_LIMIT, BACK_END_LIMIT
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def standard_loan():
    return LoanInputs(principal=400_000, annual_rate=0.065, term_years=30)

@pytest.fixture
def qualified_borrower():
    return BorrowerProfile(gross_monthly_income=10_000, monthly_debts=500)

@pytest.fixture
def stretched_borrower():
    return BorrowerProfile(gross_monthly_income=6_000, monthly_debts=1_500)


# ── Front-end ratio tests ─────────────────────────────────────────────────────

def test_front_end_ratio_is_between_0_and_1(standard_loan, qualified_borrower):
    ratio = calculate_front_end_ratio(qualified_borrower, standard_loan)
    assert 0 < ratio < 1

def test_higher_income_lowers_front_end_ratio(standard_loan):
    low  = BorrowerProfile(gross_monthly_income=6_000,  monthly_debts=0)
    high = BorrowerProfile(gross_monthly_income=12_000, monthly_debts=0)
    assert calculate_front_end_ratio(high, standard_loan) < \
           calculate_front_end_ratio(low,  standard_loan)


# ── Back-end ratio tests ──────────────────────────────────────────────────────

def test_back_end_ratio_exceeds_front_end_ratio(standard_loan, qualified_borrower):
    front = calculate_front_end_ratio(qualified_borrower, standard_loan)
    back  = calculate_back_end_ratio(qualified_borrower, standard_loan)
    assert back > front

def test_no_debts_makes_ratios_equal(standard_loan):
    borrower = BorrowerProfile(gross_monthly_income=10_000, monthly_debts=0)
    front = calculate_front_end_ratio(borrower, standard_loan)
    back  = calculate_back_end_ratio(borrower, standard_loan)
    assert abs(front - back) < 0.0001


# ── Affordability verdict tests ───────────────────────────────────────────────

def test_qualified_borrower_passes(standard_loan, qualified_borrower):
    result = is_loan_affordable(qualified_borrower, standard_loan)
    assert result["affordable"] is True

def test_stretched_borrower_fails(standard_loan, stretched_borrower):
    result = is_loan_affordable(stretched_borrower, standard_loan)
    assert result["affordable"] is False

def test_affordability_result_has_required_keys(standard_loan, qualified_borrower):
    result = is_loan_affordable(qualified_borrower, standard_loan)
    for key in ["front_end_ratio", "back_end_ratio", "front_end_pass",
                "back_end_pass", "affordable"]:
        assert key in result


# ── Maximum loan tests ────────────────────────────────────────────────────────

def test_max_loan_is_positive(qualified_borrower):
    result = maximum_loan_amount(qualified_borrower, 0.065, 30)
    assert result > 0

def test_higher_income_yields_higher_max_loan():
    low  = BorrowerProfile(gross_monthly_income=6_000,  monthly_debts=0)
    high = BorrowerProfile(gross_monthly_income=12_000, monthly_debts=0)
    assert maximum_loan_amount(high, 0.065, 30) > \
           maximum_loan_amount(low,  0.065, 30)

def test_more_debt_reduces_max_loan():
    low_debt  = BorrowerProfile(gross_monthly_income=10_000, monthly_debts=200)
    high_debt = BorrowerProfile(gross_monthly_income=10_000, monthly_debts=1_500)
    assert maximum_loan_amount(high_debt, 0.065, 30) < \
           maximum_loan_amount(low_debt,  0.065, 30)