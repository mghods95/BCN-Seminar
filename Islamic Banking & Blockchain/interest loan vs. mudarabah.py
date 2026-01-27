import numpy as np
import pandas as pd

np.random.seed(42)

# Capital invested by the bank
capital = 100_000

# Conventional loan parameters
interest_rate = 0.08  # 8% fixed interest

# Mudarabah parameters
bank_profit_share = 0.60   # bank gets 60% of profits
entrepreneur_share = 0.40

# Monte Carlo settings
n_simulations = 100_000

# Business profit distribution (real economy uncertainty)
# Mean profit = 20k, standard deviation = 50k
business_outcomes = np.random.normal(
    loc=20_000,
    scale=50_000,
    size=n_simulations
)

# --- Interest-based loan payoff ---
# Fixed payoff (ignoring default mechanics for clarity)
loan_payoff = np.full(n_simulations, capital * (1 + interest_rate))

# --- Mudarabah payoff ---
mudarabah_payoff = np.where(
    business_outcomes >= 0,
    capital + bank_profit_share * business_outcomes,  # profit sharing
    capital + business_outcomes                        # losses borne by bank
)

def risk_metrics(payoffs, capital):
    return {
        "Expected Payoff": np.mean(payoffs),
        "Std Deviation": np.std(payoffs),
        "Probability of Loss": np.mean(payoffs < capital),
        "5% VaR": np.percentile(payoffs, 5)
    }

loan_metrics = risk_metrics(loan_payoff, capital)
mudarabah_metrics = risk_metrics(mudarabah_payoff, capital)

summary = pd.DataFrame([loan_metrics, mudarabah_metrics],
                       index=["Interest Loan", "Mudarabah"])
summary

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

# Mudarabah payoff distribution
plt.hist(
    mudarabah_payoff,
    bins=100,
    density=True,
    alpha=0.7,
    label="Mudarabah (PLS)"
)

# Interest loan payoff as a vertical line
plt.axvline(
    capital * (1 + interest_rate),
    linewidth=3,
    linestyle="--",
    color="red",
    label="Interest Loan (Fixed Payoff)"
)

# Initial capital reference
plt.axvline(
    capital,
    linewidth=2,
    linestyle=":",
    label="Initial Capital"
)

plt.title("Bank Payoff Distribution: Interest Loan vs Mudarabah")
plt.xlabel("Bank Payoff")
plt.ylabel("Density")
plt.legend()
plt.show()
