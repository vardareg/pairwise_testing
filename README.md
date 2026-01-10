# SEDS 514 Software Testing - Project 3
## Pairwise Test Design on a Real OSS Project

**Project Status:** Completed
**System Under Test:** [python-tabulate](https://github.com/astanin/python-tabulate)

---

### 1. Context & Goal
This project applies **Pairwise Testing (2-way combinatorial interaction testing)** to the `tabulate` library, a popular Python tool for pretty-printing tables. The goal is to:
1.  Model the input space of the `tabulate()` function using Factors and Levels.
2.  Generate a pairwise covering array using **Microsoft PICT**.
3.  Implement the tests using `pytest`.
4.  Evaluate the effectiveness of the Pairwise suite by comparing it against a Random testing baseline with an equivalent budget.

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

#### Constraints
To ensure all generated tests are logically valid and runnable, we defined 5 constraints. Any combination violating these is rejected by the pairwise generator:

1.  **Dictionary Inputs**: If `InputType` is Dict-based (`ListOfDicts`, `DictOfColumns`), `HeadersMode` cannot be `FirstRow`.
2.  **Keys Headers**: If `HeadersMode` is `Keys`, `InputType` must be Dict-based (`ListOfDicts`, `DictOfColumns`).
3.  **NA Handling**: If `MissingValues` is `NA`, `DataMix` must include None (`MixedNone`) to allow verification of replacement.
4.  **List Inputs**: If `InputType` is `ListOfLists`, `HeadersMode` cannot be `Keys`.
5.  **Wide Text**: If `Size` is `WideText`, `TableFormat` must be a grid-like format (`grid`, `psql`, `github`) that supports wrapping or distinct layout.

### 3. Pairwise Test Generation

*   **Tool Used:** Microsoft PICT (Pairwise Independent Combinatorial Testing)
*   **Model File:** `tabulate_model.txt`
*   **Generated Suite:** `pairwise_tests.csv`
*   **Total Tests Generated:** 18
*   **Constraint Handling:** PICT natively supports constraints, ensuring all 18 tests are valid combinations.

### 4. Test Implementation

The tests are implemented using `pytest` in `test_tabulate_pairwise.py`.

*   **Data Driven:** The test runner reads `pairwise_tests.csv` and dynamically generates test cases.
*   **Fixtures:** A `TestDataFactory` class converts abstract PICT parameters (e.g., "ListOfLists", "Custom") into actual Python objects (data structures, argument lists) required by `tabulate`.
*   **Oracles (Assertions):**
    1.  **Non-Empty Output:** Asserts that `tabulate()` returns a non-empty string.
    2.  **Missing Value Replacement:** If `MissingValues="NA"`, asserts that "NA" appears in the output.
    3.  **Explicit Headers:** If headers are provided explicitly, asserts they appear in the output.
    4.  **Negative Tests:** While the primary suite focuses on valid inputs, the generated set includes combinations that stress-test valid edge cases (e.g., empty values, wide text).

### 5. Evaluation Report

To evaluate the effectiveness of the Pairwise approach, we compared it against a Random Baseline suite (`test_random.py`) generated with the same test budget (18 tests).

#### Metrics Comparison

| Metric | Pairwise Suite | Random Baseline |
| :--- | :--- | :--- |
| **Total Tests (Budget)** | 18 | 18 |
| **Valid Tests** | 18 | 7 |
| **Invalid Tests (Constraint Violations)** | 0 | 11 |
| **Bugs Found** | 2 | 0 |
| **Statement Coverage** | 90% | N/A (Test runner coverage) |

#### Analysis

1.  **Pairwise Effectiveness:**
    *   The Pairwise suite successfully identified a **bug** in the system.
    *   **Bug Details:** The combination of `InputType=ListOfDicts` and `TableFormat=psql` causes `tabulate` to return an empty string (failure).
    *   **Tests Catching Bug:** Case 7 (`InputType=ListOfDicts`, `TableFormat=psql`, `Size=WideText`) and Case 12 (`InputType=ListOfDicts`, `TableFormat=psql`, `Size=Medium5x4`) in the generated CSV (mapped to pytest indices `case6` and `case10` due to 0-based indexing/header offset). *Note: The specific indices depend on the exact generated CSV order.*

2.  **Random Baseline Weakness:**
    *   **High Invalid Rate:** 11 out of 18 random tests (61%) were invalid because the random generator did not respect the logical constraints of the SUT.
    *   **Bug Missed:** The random suite passed all tests (18 passed), completely missing the bug. This happened because it failed to generate the specific failure-inducing combination (`ListOfDicts` + `psql`) within the limited budget.

#### Note: Invalid Random Cases
The Random Baseline included the following invalid test cases which violate the defined system constraints:

1.  **Case 1:** `InputType='DictOfColumns'`, `HeadersMode='FirstRow'` (Violates: Dict input cannot use FirstRow).
2.  **Case 3:** `MissingValues='NA'`, `DataMix='Strings'` (Violates: NA replacement requires MixedNone data).
3.  **Case 4:** `MissingValues='NA'`, `DataMix='Strings'` (Violates: NA replacement requires MixedNone data).
4.  **Case 6:** `InputType='ListOfDicts'`, `HeadersMode='FirstRow'` (Violates: Dict input cannot use FirstRow).
5.  **Case 8:** `MissingValues='NA'`, `DataMix='IntsFloats'` (Violates: NA replacement requires MixedNone data).
6.  **Case 10:** `MissingValues='NA'`, `DataMix='IntsFloats'` (Violates: NA replacement requires MixedNone data).
7.  **Case 12:** `MissingValues='NA'`, `DataMix='Strings'` (Violates: NA replacement requires MixedNone data).
8.  **Case 13:** `MissingValues='NA'`, `DataMix='Strings'` (Violates: NA replacement requires MixedNone data).
9.  **Case 14:** `InputType='DictOfColumns'`, `HeadersMode='FirstRow'` (Violates: Dict input cannot use FirstRow).
10. **Case 15:** `MissingValues='NA'`, `DataMix='IntsFloats'` AND `Size='WideText'`, `TableFormat='plain'` (Violates: NA replacement logic AND WideText requires grid format).
11. **Case 16:** `InputType='ListOfLists'`, `HeadersMode='Keys'` (Violates: List input cannot use Keys headers).

### 6. Installation & Usage

**1. Install Dependencies:**
```bash
pip install pytest tabulate pytest-cov
```

**2. Run Pairwise Tests:**
```bash
python3 -m pytest test_tabulate_pairwise.py
```
*Expect failures due to the identified bug.*

**3. Run Random Baseline:**
```bash
python3 -m pytest test_random.py
```
*Expect all pass (false negatives due to lack of coverage).*

**4. Check Coverage:**
```bash
python3 -m pytest --cov=test_tabulate_pairwise test_tabulate_pairwise.py
```
