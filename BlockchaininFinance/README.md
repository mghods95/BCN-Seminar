# Consensus Examples (PoW, PoA, PBFT, PoS)

Short, educational Python examples to use in a presentation.

Files:
- consensus_examples.py — contains all four tiny demos and a runnable __main__.

How to run
- Requires Python 3.6+
- Run: `python3 consensus_examples.py`
- Each section prints a minimal demonstration:

  - PoW: mines a nonce meeting a small difficulty (adjust difficulty for demo speed)
  - PoA: shows round-robin proposers from an authority validator list
  - PBFT: simulates a tiny pre-prepare / prepare / commit flow and prints quorum checks
  - PoS: picks proposers proportional to stake; runs 1000 picks to show distribution

Presentation notes / talking points
- PoW: energy-intensive, security via computational cost, used by Bitcoin
- PoA: low-latency, permissioned, relies on identity/trust of validators
- PBFT: classical BFT algorithm for small permissioned networks (fast finality)
- PoS: security via economic stake, energy-efficient, various selection schemes

License: Feel free to fork, adapt, and include these snippets in your slides.

---

# Blockchain Financial Examples for Presentation

![Blockchain in Finance](./blockchain_in_finance.png)

This folder contains three short, self-contained Python demos you can use in slides or run live:

- payment_example.py — illustrates a simple account-based payment flow with a mempool, nonce checks, and signature verification (mock).
- smart_contract_example.py — shows a deployable token contract and an escrow contract to demonstrate how contracts hold state and enforce rules.
- bonds_example.py — models tokenized bonds with issuance, coupon payments, transfers, and redemption at maturity.

How to use
- Requires Python 3.7+.
- Run each demo: `python3 payment_example.py` (or `smart_contract_example.py` / `bonds_example.py`).

Presentation talking points
- Payment example: discuss atomic transfer, nonce for replay protection, mempool ordering, and why signatures matter.
- Smart contracts: highlight deterministic execution, state persistence, and trust minimization (escrow example shows on-chain enforcement vs. off-chain contracts).
- Tokenized bonds: talk about programmability (coupon schedules, automatic payouts), fractional ownership, settlement speed, and regulatory considerations.

Next steps / suggestions
- Convert to Jupyter notebook cells for slide demos (I can prepare a notebook).
- Add real cryptographic signatures with ecdsa/cryptography for a more realistic demo.
- Wire these examples to a tiny simulated P2P network or consensus demo so you can show transactions being broadcast and included in blocks.
- Split into modules and add unit tests for each behavior to show testable financial logic.

License: Use freely in your presentation.
