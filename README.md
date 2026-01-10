# SEDS 514 Software Testing - Project 3
## Pairwise Test Design on a Real OSS Project

**Project Status:** Completed
**System Under Test:** [python-tabulate](https://github.com/astanin/python-tabulate)

---

### 1. Context & Goal
This project applies **Pairwise Testing (2-way combinatorial interaction testing)** to the `tabulate` library, a popular Python tool for pretty-printing tables. The goal is to:
1.  Model the input space of the `tabulate()` function using Factors and Levels.
2. Inject bug to the `tabulate` library.
3.  Generate a pairwise covering array using **Microsoft PICT**.
4.  Implement the tests using `pytest`.
5.  Evaluate the effectiveness of the Pairwise suite by comparing it against a Random testing baseline with an equivalent budget.

### 2. Test Design Specification

#### Factors & Levels
We modeled the input space of the `tabulate` function using 7 factors, representing key configuration options:

1.  **Input Type**
    *   `ListOfLists`: Standard 2D list.
    *   `ListOfDicts`: List of dictionaries (keys as headers).
    *   `DictOfColumns`: Dictionary where keys are headers and values are column lists.
2.  **Headers Mode**
    *   `Explicit`: A list of strings provided via the `headers` argument.
    *   `FirstRow`: The first row of data is treated as headers.
    *   `Keys`: Keys of dictionary inputs are used as headers.
3.  **Table Format** (tablefmt)
    *   `plain`: No borders.
    *   `github`: Markdown-compatible.
    *   `grid`: Full grid borders.
    *   `psql`: PostgreSQL style.
4.  **Row Indices** (showindex)
    *   `always`: Boolean `True`.
    *   `never`: Boolean `False`.
    *   `Custom`: An explicit list of index labels.
5.  **Missing Values** (missingval)
    *   `Default`: Default library behavior (usually empty string).
    *   `NA`: Explicit replacement string "NA".
6.  **Data Mix**
    *   `Strings`: All text data.
    *   `IntsFloats`: Numeric data.
    *   `MixedNone`: Mix of types including `None` values (to test missing value handling).
7.  **Size**
    *   `Small2x2`: Minimal case.
    *   `Medium5x4`: Standard case.
    *   `WideText`: Includes long strings to test wrapping/layout logic.

#### Exhaustive Calculation: 
Based on these domains ($3 \times 3 \times 4 \times 3 \times 2 \times 3 \times 3$), the total number of combinatorial possibilities is 1,944.

#### Constraints
To ensure all generated tests are logically valid and runnable, we defined 5 constraints. Any combination violating these is rejected by the pairwise generator:

1.  **Dictionary Inputs**: If `InputType` is Dict-based (`ListOfDicts`, `DictOfColumns`), `HeadersMode` cannot be `FirstRow`.
2.  **Keys Headers**: If `HeadersMode` is `Keys`, `InputType` must be Dict-based (`ListOfDicts`, `DictOfColumns`).
3.  **NA Handling**: If `MissingValues` is `NA`, `DataMix` must include None (`MixedNone`) to allow verification of replacement.
4.  **List Inputs**: If `InputType` is `ListOfLists`, `HeadersMode` cannot be `Keys`.
5.  **Wide Text**: If `Size` is `WideText`, `TableFormat` must be a grid-like format (`grid`, `psql`, `github`) that supports wrapping or distinct layout.
#### Injected Bugs
A logic error was introduced in `src/tabulate/__init__.py` to cause failure under specific conditions involving `ListOfDicts` and `psql` format.

```python
# Bug injected for Pairwise Testing Project
# Triggers only when InputType=ListOfDicts AND TableFormat=psql
if tablefmt == "psql" and isinstance(tabular_data, list) and len(tabular_data) > 0 and isinstance(tabular_data[0], dict):
    return ""
```

This will cause the function to return an empty string instead of the formatted table, which should be caught by the test suite assertions.

### 3. Pairwise Test Generation

*   **Tool Used:** Microsoft PICT (Pairwise Independent Combinatorial Testing)
*   **Model File:** `data/tabulate_model.txt`
*   **Generated Suite:** `data/pairwise_tests.csv`
*   **Total Tests Generated:** 18
*   **Constraint Handling:** PICT natively supports constraints, ensuring all 18 tests are valid combinations.

### 4. Test Implementation

The tests are implemented using `pytest` in `tests/test_tabulate_pairwise.py`.



*   **Data Driven:** The test runner reads `data/pairwise_tests.csv` and dynamically generates test cases.
*   **Fixtures:** A `TestDataFactory` class converts abstract PICT parameters (e.g., "ListOfLists", "Custom") into actual Python objects (data structures, argument lists) required by `tabulate`.
*   **Oracles (Assertions):**
    1.  **Non-Empty Output:** Asserts that `tabulate()` returns a non-empty string.
    2.  **Missing Value Replacement:** If `MissingValues="NA"`, asserts that "NA" appears in the output.
    3.  **Explicit Headers:** If headers are provided explicitly, asserts they appear in the output.
    4.  **Negative Tests:** We integrated a negative test suite (sourced from `data/negative_tests.csv`) into the pairwise runner. These tests intentionally violate system constraints (e.g., `ListOfDicts` + `FirstRow`) to verify that the system handles them gracefully by raising `ValueError` instead of behaving unpredictably.

### 5. Evaluation Report

To evaluate the effectiveness of the Pairwise approach, we compared it against a Random Baseline suite (`tests/test_random.py`) generated with the same test budget (18 tests).

#### Metrics Comparison

| Metric | Pairwise Suite | Random Baseline |
| :--- | :--- | :--- |
| **Total Tests (Budget)** | 18 | 18 |
| **Valid Tests** | 18 | 7 |
| **Invalid Tests (Constraint Violations)** | 0 | 11 |
| **Bugs Found** | 2 | 0 |
| **Statement Coverage** | 90% | N/A |

#### Analysis

1.  **Pairwise Effectiveness:**
    *   The Pairwise suite successfully identified a **bug** in the system.
    *   **Bug Details:** The combination of `InputType=ListOfDicts` and `TableFormat=psql` causes `tabulate` to return an empty string (failure).
    *   **Tests Catching Bug:** Case 7 (`InputType=ListOfDicts`, `TableFormat=psql`, `Size=WideText`) and Case 12 (`InputType=ListOfDicts`, `TableFormat=psql`, `Size=Medium5x4`) in the generated CSV (mapped to pytest indices `case6` and `case10` due to 0-based indexing/header offset). *Note: The specific indices depend on the exact generated CSV order.*

2.  **Random Baseline Analysis:**
    *   **Graceful Rejection:** Previously, the random suite failed (crashed) on invalid tests. With the new constraint enforcement code, the 11 invalid test cases now trigger a `ValueError` which the test runner catches and treats as a **PASS** (Correct Rejection).
    *   **Bug Missed:** Despite passing the invalid cases gracefully, the random suite still **completely missed the bug**. This is because it failed to generate the specific failure-inducing combination (`ListOfDicts` + `psql`) within the limited budget.

### 6. Installation & Usage

**1. Install Dependencies:**
```bash
pip install pytest tabulate pytest-cov
```

**2. (Optional) Install PICT:**
To regenerate the pairwise tests, you need the Microsoft PICT tool.
*   **Source:** [microsoft/pict](https://github.com/microsoft/pict)
*   **Installation:** Follow the build instructions in the PICT repository. Ensure the `pict` executable is in your PATH.

### 7. Usage Instructions

#### A. Generating Pairwise Tests
If you have PICT installed, you can regenerate the test suite:
```bash
pict data/tabulate_model.txt > data/pairwise_tests.csv
```
*Note: `data/pairwise_tests.csv` is already included in the repo, so this step is optional.*

#### B. Running Pairwise Tests (Integrated Negative Tests)
```bash
python3 -m pytest tests/test_tabulate_pairwise.py
```
*Expect failures due to the identified bug, but negative tests should pass.*

#### C. Running Random Baseline
```bash
python3 -m pytest tests/test_random.py
```
*Expect all pass. Invalid cases are now correctly rejected with ValueError.*

#### D. Check Coverage
```bash
python3 -m pytest --cov=src/tabulate tests/test_tabulate_pairwise.py
```
---
**Authors:**  
Egehan Vardar (323011010)  
M. Fatih Gülmez (323011006)
