# fd-cex-checker

A program to automatically verify the counterexamples in the paper
[Exploring Relations among Fairness Notions in Discrete Fair Division](https://arxiv.org/abs/2502.02815).

Each counterexample proves a non-implication of the form "F1 does not imply F2":
it is a fair division instance and an allocation that satisfies F1 for every agent,
together with a witness agent who does not satisfy F2.

## File overview

| File | Purpose |
|---|---|
| `valuation.py` | Abstract `Valuation` base class and `AdditiveValuation` |
| `instance.py` | `Instance`: a list of valuations and agent weights |
| `allocation.py` | `Allocation`: maps items to agents (owner and bundle views) |
| `conditions.py` | `verify_conditions`: checks valuation/marginal type constraints from the JSON spec |
| `notions.py` | Per-agent fairness checks; `is_fair` / `is_fair_to` dispatchers |
| `counterexample.py` | `Counterexample` dataclass and its `verify` method |
| `check.py` | Command-line entry point |
| `simple_cexs.py` | Small worked examples for understanding the code |
| `simple_cexs.json` | JSON spec for the simple examples ([`cpigjs`](https://github.com/sharmaeklavya2/cpigjs/) format) |

## Usage

Verify a collection of counterexamples:

    python check.py <counterexamples.py>

Also cross-check against a cpigjs-format JSON spec:

    python check.py <counterexamples.py> --cpigjs-json <spec.json>

Skip the mathematical verification (JSON cross-check only):

    python check.py <counterexamples.py> --cpigjs-json <spec.json> --no-verify

Exits with code 0 if everything passes, 1 otherwise. All output goes to stderr.

## Adding counterexamples

Create or extend a Python file that exposes a module-level list:

```python
COUNTEREXAMPLES: list[Counterexample] = [...]
```

Each entry is a `Counterexample` with the following fields:

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier matching the JSON spec |
| `instance` | `Instance` | Valuations and weights |
| `allocation` | `Allocation` | The allocation (bundles or owner vector) |
| `witness` | `int` | Agent index who violates `violates` |
| `satisfies` | `str` | Fairness notion satisfied by all agents |
| `violates` | `str` | Fairness notion violated by `witness` |

Notion names match the cpigjs JSON spec (`'EF'`, `'PROP'`, `'MMS'`, …).
Composite notions are supported: `'EF1+PROP'` (conjunction), `'EF1|MMS'`
(disjunction).

See `simple_cexs.py` for worked examples.

## Requirements

Python 3.10 or later (uses `match` statements).
No third-party dependencies.
