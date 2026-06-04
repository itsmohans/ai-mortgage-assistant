import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from core.amortization import LoanInputs, build_amortization_schedule, summarize_loan
from core.affordability import BorrowerProfile, is_loan_affordable, maximum_loan_amount
from core.scenarios import compare_loan_terms, extra_payment_impact, refinance_analysis

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Mortgage Assistant",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 AI Mortgage Decision Assistant")
st.caption("Built with Python · Streamlit · Claude API (coming soon)")

# ── Sidebar — Loan Inputs ─────────────────────────────────────────────────────

st.sidebar.header("Loan Parameters")

principal = st.sidebar.number_input(
    "Loan Amount ($)", min_value=50_000, max_value=2_000_000,
    value=400_000, step=5_000
)
annual_rate = st.sidebar.slider(
    "Annual Interest Rate (%)", min_value=2.0, max_value=12.0,
    value=6.5, step=0.05
) / 100
term_years = st.sidebar.selectbox(
    "Loan Term", options=[10, 15, 20, 25, 30], index=4
)
prepayment = st.sidebar.number_input(
    "Upfront Prepayment ($)", min_value=0, max_value=500_000,
    value=0, step=1_000
)
extra_monthly = st.sidebar.number_input(
    "Extra Monthly Payment ($)", min_value=0, max_value=10_000,
    value=0, step=100
)

st.sidebar.header("Borrower Profile")
gross_income = st.sidebar.number_input(
    "Gross Monthly Income ($)", min_value=1_000, max_value=100_000,
    value=10_000, step=500
)
monthly_debts = st.sidebar.number_input(
    "Existing Monthly Debts ($)", min_value=0, max_value=20_000,
    value=500, step=100
)

# ── Build Core Objects ────────────────────────────────────────────────────────

inputs = LoanInputs(
    principal=principal,
    annual_rate=annual_rate,
    term_years=term_years,
    extra_monthly_payment=extra_monthly,
    prepayment=prepayment
)

borrower = BorrowerProfile(
    gross_monthly_income=gross_income,
    monthly_debts=monthly_debts
)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Loan Summary",
    "📅 Amortization Schedule",
    "✅ Affordability",
    "🔄 Scenarios"
])

# ── Tab 1: Loan Summary ───────────────────────────────────────────────────────

with tab1:
    st.subheader("Loan Summary")
    summary = summarize_loan(inputs)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Payment",   f"${summary['monthly_payment']:,.2f}")
    col2.metric("Total Paid",        f"${summary['total_paid']:,.2f}")
    col3.metric("Total Interest",    f"${summary['total_interest_paid']:,.2f}")
    col4.metric("Actual Term",       f"{summary['actual_term_months']} months")

    st.divider()

    # Interest vs Principal breakdown chart
    schedule = build_amortization_schedule(inputs)

    st.subheader("Interest vs Principal Over Time")
    chart_data = schedule[["period", "principal_paid", "interest_paid"]].set_index("period")
    st.area_chart(chart_data)

# ── Tab 2: Amortization Schedule ──────────────────────────────────────────────

with tab2:
    st.subheader("Full Amortization Schedule")

    display = schedule.copy()
    display.columns = ["Period", "Payment", "Principal", "Interest", "Balance"]
    for col in ["Payment", "Principal", "Interest", "Balance"]:
        display[col] = display[col].apply(lambda x: f"${x:,.2f}")

    st.dataframe(display, use_container_width=True, hide_index=True)

# ── Tab 3: Affordability ──────────────────────────────────────────────────────

with tab3:
    st.subheader("Affordability Analysis")
    result = is_loan_affordable(borrower, inputs)

    verdict_color = "green" if result["affordable"] else "red"
    verdict_text  = "✅ This loan appears affordable" \
                    if result["affordable"] else \
                    "❌ This loan may be a stretch"
    st.markdown(f"### :{verdict_color}[{verdict_text}]")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Front-End Ratio",
            f"{result['front_end_ratio']:.1%}",
            delta=f"Limit: {result['front_end_limit']:.0%}",
            delta_color="off"
        )
        if result["front_end_pass"]:
            st.success("Within front-end limit (28%)")
        else:
            st.error("Exceeds front-end limit (28%)")

    with col2:
        st.metric(
            "Back-End Ratio (DTI)",
            f"{result['back_end_ratio']:.1%}",
            delta=f"Limit: {result['back_end_limit']:.0%}",
            delta_color="off"
        )
        if result["back_end_pass"]:
            st.success("Within back-end limit (43%)")
        else:
            st.error("Exceeds back-end limit (43%)")

    st.divider()
    max_loan = maximum_loan_amount(borrower, annual_rate, term_years)
    st.metric("Maximum Loan You Qualify For", f"${max_loan:,.0f}")

# ── Tab 4: Scenarios ──────────────────────────────────────────────────────────

with tab4:
    st.subheader("Scenario Comparisons")

    # 15yr vs 30yr comparison
    st.markdown("#### 📌 15-Year vs 30-Year")
    comparison = compare_loan_terms(inputs.effective_principal, annual_rate)

    col1, col2, col3 = st.columns(3)
    col1.metric("30yr Monthly Payment",
                f"${comparison['term_30yr']['monthly_payment']:,.2f}")
    col2.metric("15yr Monthly Payment",
                f"${comparison['term_15yr']['monthly_payment']:,.2f}")
    col3.metric("Interest Saved with 15yr",
                f"${comparison['interest_saved']:,.2f}")

    st.divider()

    # Extra payment impact
    st.markdown("#### 💰 Extra Monthly Payment Impact")
    extra_amount = st.number_input(
        "Simulate extra monthly payment ($)",
        min_value=0, max_value=5000, value=500, step=100
    )
    impact = extra_payment_impact(inputs, extra_amount)

    col1, col2, col3 = st.columns(3)
    col1.metric("Months Saved",    f"{impact['months_saved']}")
    col2.metric("Years Saved",     f"{impact['years_saved']}")
    col3.metric("Interest Saved",  f"${impact['interest_saved']:,.2f}")

    st.divider()

    # Refinance analysis
    st.markdown("#### 🔁 Refinance Analysis")
    col1, col2 = st.columns(2)
    with col1:
        new_rate = st.slider(
            "New Interest Rate (%)",
            min_value=2.0, max_value=12.0, value=6.0, step=0.05
        ) / 100
        closing_costs = st.number_input(
            "Closing Costs ($)", min_value=0, max_value=20_000,
            value=5_000, step=500
        )

    refi = refinance_analysis(
        current_balance=inputs.effective_principal,
        current_rate=annual_rate,
        current_remaining_months=term_years * 12,
        new_rate=new_rate,
        new_term_years=term_years,
        closing_costs=closing_costs
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Payment", f"${refi['current_payment']:,.2f}")
    col2.metric("New Payment",     f"${refi['new_payment']:,.2f}")
    col3.metric("Monthly Savings", f"${refi['monthly_savings']:,.2f}")

    if refi["break_even_months"]:
        st.info(f"⏱ Break-even in **{refi['break_even_months']} months** "
                f"({refi['break_even_years']} years)")
        if refi["worth_refinancing"]:
            st.success("✅ Refinancing appears worthwhile")
        else:
            st.warning("⚠️ Break-even exceeds loan term — may not be worth it")
    else:
        st.error("❌ New rate is higher — refinancing not recommended")