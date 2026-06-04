# 🏠 AI Mortgage Decision Assistant

An AI-powered mortgage decision tool built with Python, Streamlit, and the Claude API. This project converts a professional Excel-based mortgage amortization model into a fully interactive, intelligent financial assistant — designed for portfolio demonstration and practical real-world use.

---

## 🎯 What It Does

Most mortgage calculators tell you your payment. This tool tells you whether you can afford it, how different decisions affect your long-term costs, and — in upcoming releases — explains everything in plain English through an AI advisor powered by Claude.

**Core capabilities:**

- **Loan Summary** — monthly payment, total cost, total interest, and actual payoff term including the impact of prepayments and extra monthly payments
- **Amortization Schedule** — full month-by-month breakdown of principal, interest, and remaining balance
- **Affordability Analysis** — front-end and back-end DTI ratio checks against industry lending standards, with maximum qualifying loan calculation
- **Scenario Comparisons** — 15yr vs 30yr analysis, extra payment impact modeling, and refinance break-even analysis

---

## 🏗️ Architecture

The project is organized around a strict separation of concerns — business logic, UI, and AI are completely independent layers.

```
ai-mortgage-assistant/
│
├── app/                        # Streamlit UI layer
│   └── main.py                 # Application entry point
│
├── core/                       # Pure Python business logic (no UI dependencies)
│   ├── amortization.py         # Payment engine, amortization schedule, loan summary
│   ├── affordability.py        # DTI ratios, affordability verdict, max loan amount
│   └── scenarios.py            # Term comparison, extra payment impact, refinance analysis
│
├── ai/                         # Claude API integration (Phase 3)
│   ├── advisor.py              # AI advisor logic
│   └── prompts.py              # Prompt templates
│
├── data/                       # Static data and RAG knowledge base (Phase 4)
│   └── knowledge/              # Mortgage documents for RAG
│
├── tests/                      # Unit tests — 31 passing
│   ├── test_amortization.py
│   ├── test_affordability.py
│   └── test_scenarios.py
│
├── conftest.py
├── requirements.txt
└── README.md
```

**Why this structure?** The `core/` layer has zero knowledge of Streamlit or Claude. It is pure Python math. This means it can be tested independently, reused in other applications, and swapped to a different UI without touching any business logic.

---

## 🧮 Core Modules

### `core/amortization.py`
The mortgage calculation engine. Translates Excel's `PMT()`, `IPMT()`, and `PPMT()` functions into testable Python using `numpy_financial`.

Key components:
- `LoanInputs` dataclass — typed container for all loan parameters including upfront prepayment and extra monthly payments
- `calculate_monthly_payment()` — fixed monthly P&I payment
- `build_amortization_schedule()` — full amortization table as a pandas DataFrame with early payoff logic
- `summarize_loan()` — high-level metrics composed from the functions above

### `core/affordability.py`
Lender qualification logic based on industry-standard DTI thresholds.

Key components:
- `BorrowerProfile` dataclass — borrower income and existing debt
- `calculate_front_end_ratio()` — housing cost as % of gross income (28% limit)
- `calculate_back_end_ratio()` — total debt as % of gross income (43% limit)
- `is_loan_affordable()` — combined affordability verdict with pass/fail on each ratio
- `maximum_loan_amount()` — largest principal a borrower qualifies for given income and debts

### `core/scenarios.py`
What-if analysis engine for financial decision support.

Key components:
- `compare_loan_terms()` — side-by-side 15yr vs 30yr comparison
- `extra_payment_impact()` — months and interest saved by additional monthly payments
- `refinance_analysis()` — break-even calculation for refinancing at a new rate

---

## 🖥️ UI — Streamlit

The Streamlit interface provides a real-time interactive dashboard with four tabs:

| Tab | What It Shows |
|-----|--------------|
| 📊 Loan Summary | Key metrics + interest vs principal area chart |
| 📅 Amortization Schedule | Full scrollable payment table |
| ✅ Affordability | DTI ratios, pass/fail indicators, max loan amount |
| 🔄 Scenarios | Term comparison, extra payment simulator, refinance analyzer |

All inputs are controlled from the sidebar — changing any value updates all four tabs instantly.

---

## 🧪 Testing

31 unit tests across all three core modules, organized by function:

```bash
pytest tests/ -v
```

```
tests/test_amortization.py    11 tests
tests/test_affordability.py   10 tests
tests/test_scenarios.py       10 tests
─────────────────────────────────────
Total: 31 passed
```

Tests cover known calculation values (verified against Excel), edge cases (early payoff, final payment rounding, zero savings on refinance), and behavioral assertions (higher income → lower DTI, larger prepayment → lower total interest).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/itsmohans/ai-mortgage-assistant.git
cd ai-mortgage-assistant

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app/main.py
```

Open your browser at `http://localhost:8501`

### Run Tests

```bash
pytest tests/ -v
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| UI | Streamlit 1.58 |
| Financial Math | numpy-financial |
| Data Manipulation | pandas |
| AI Advisor | Anthropic Claude API (Phase 3) |
| Vector Search | ChromaDB + LangChain (Phase 4) |
| Testing | pytest |
| Version Control | Git / GitHub |

---

## 🗺️ Roadmap

This project is being built incrementally across four phases:

- [x] **Phase 1 — Python Core** · Amortization engine, affordability analysis, scenario modeling, 31 unit tests
- [x] **Phase 2 — Streamlit UI** · Interactive dashboard with real-time inputs and charts
- [ ] **Phase 3 — Claude AI Advisor** · Natural language explanations of loan analysis using the Anthropic Claude API
- [ ] **Phase 4 — RAG Architecture** · Ground AI responses in real mortgage documents (CFPB guides, lending standards) using vector embeddings and retrieval-augmented generation

---

## 💡 Design Decisions

**Why separate `core/` from `app/`?**
Business logic that lives inside UI components cannot be unit tested, reused, or maintained cleanly. Keeping `core/` dependency-free means every function can be tested in isolation and the entire calculation layer can be reused in a different UI or API without modification.

**Why `@dataclass` for inputs?**
Passing structured typed objects (`LoanInputs`, `BorrowerProfile`) instead of raw arguments makes function signatures readable, prevents positional argument errors, and provides a single place to add validation later.

**Why `numpy_financial` instead of manual formulas?**
`numpy_financial.pmt()` is the exact equivalent of Excel's `PMT()` — same formula, same edge case handling. This makes the Excel-to-Python migration verifiable and keeps the math auditable.

---

## 👤 Author

**Mapla** · Senior Business Systems Analyst transitioning to AI/Product/Data roles.

This project is part of a portfolio demonstrating practical AI engineering skills including Python architecture, financial domain modeling, test-driven development, and LLM integration.

[GitHub](https://github.com/itsmohans) · [LinkedIn](#)

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.
