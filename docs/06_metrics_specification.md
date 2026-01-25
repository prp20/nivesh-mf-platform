# Metrics Specification Document

## Purpose
Defines all financial metrics used in the system, including formulas, applicability,
lookback periods, and interpretation rules.

---

## Equity Fund Metrics

### Alpha
- Excess return over benchmark adjusted for beta
- Lookback: 3Y rolling
- Higher is better

### Beta
- Volatility relative to benchmark
- Lookback: 3Y rolling
- Lower than 1 preferred

### Sharpe Ratio
- (Return − Risk-free rate) / Std Deviation
- Equity only
- Higher is better

### Sortino Ratio
- (Return − Risk-free rate) / Downside Deviation
- Higher is better

### R-Squared
- Benchmark correlation
- Higher implies style purity

---

## Market Cycle Metrics

### Upside Capture Ratio
- Preferred > 1

### Downside Capture Ratio
- Preferred < 1