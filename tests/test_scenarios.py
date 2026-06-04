import pytest
from core.amortization import LoanInputs
from core.scenarios import compare_loan_terms, extra_payment_impact, \
    refinance_analysis


# ── compare_loan_terms tests ──────────────────────────────────────────────────

def test_15yr_payment_higher_than_30yr():
    result = compare_loan_terms(400_000, 0.065)
    assert result["term_15yr"]["monthly_payment"] > \
           result["term_30yr"]["monthly_payment"]

def test_15yr_saves_interest_vs_30yr():
    result = compare_loan_terms(400_000, 0.065)
    assert result["interest_saved"] > 0

def test_comparison_has_payment_difference_key():
    result = compare_loan_terms(400_000, 0.065)
    assert "monthly_payment_difference" in result


# ── extra_payment_impact tests ────────────────────────────────────────────────

def test_extra_payment_saves_months():
    loan = LoanInputs(principal=400_000, annual_rate=0.065, term_years=30)
    result = extra_payment_impact(loan, extra_payment=500)
    assert result["months_saved"] > 0

def test_extra_payment_saves_interest():
    loan = LoanInputs(principal=400_000, annual_rate=0.065, term_years=30)
    result = extra_payment_impact(loan, extra_payment=500)
    assert result["interest_saved"] > 0

def test_larger_extra_payment_saves_more():
    loan = LoanInputs(principal=400_000, annual_rate=0.065, term_years=30)
    small = extra_payment_impact(loan, extra_payment=200)
    large = extra_payment_impact(loan, extra_payment=800)
    assert large["interest_saved"] > small["interest_saved"]


# ── refinance_analysis tests ──────────────────────────────────────────────────

def test_lower_rate_reduces_payment():
    result = refinance_analysis(350_000, 0.075, 300, 0.065, 30, 5000)
    assert result["new_payment"] < result["current_payment"]

def test_break_even_is_positive():
    result = refinance_analysis(350_000, 0.075, 300, 0.065, 30, 5000)
    assert result["break_even_months"] > 0

def test_higher_closing_costs_extends_break_even():
    low  = refinance_analysis(350_000, 0.075, 300, 0.065, 30, 3_000)
    high = refinance_analysis(350_000, 0.075, 300, 0.065, 30, 8_000)
    assert high["break_even_months"] > low["break_even_months"]

def test_no_savings_when_new_rate_is_higher():
    result = refinance_analysis(350_000, 0.065, 300, 0.075, 30, 5000)
    assert result["monthly_savings"] < 0
    assert result["worth_refinancing"] is False