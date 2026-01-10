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
4.  Compare the effectiveness of the Pairwise suite against a Random baseline.

### 2. Test Design Specification

#### Factors & Levels
We modeled the `tabulate` function with 7 factors:

1.  **Input Type**: `ListOfLists`, `ListOfDicts`, `DictOfColumns`
2.  **Headers Mode**: `Explicit`, `FirstRow`, `Keys`
3.  **Table Format**: `plain`, `github`, `grid`, `psql`
4.  **Row Indices**: `always`, `never`, `Custom`
5.  **Missing Values**: `Default`, `NA`
6.  **Data Mix**: `Strings`, `IntsFloats`, `MixedNone`
7.  **Size**: `Small2x2`, `Medium5x4`, `WideText`

#### Constraints
To ensure test validity, the following logical constraints are enforced (invalid combinations are rejected):
1.  **Dictionary Inputs**: If `InputType` is Dict-based, `HeadersMode` cannot be `FirstRow`.
2.  **Keys Headers**: If `HeadersMode` is `Keys`, `InputType` must be Dict-based.
3.  **NA Handling**: If `MissingValues` is `NA`, `DataMix` must include None (`MixedNone`).
4.  **List Inputs**: If `InputType` is `ListOfLists`, `HeadersMode` cannot be `Keys`.
5.  **Wide Text**: If `Size` is `WideText`, `TableFormat` must be a grid-like format (`grid`, `psql`, `github`) to properly test wrapping/layout.

### 3. Repository Structure

*   `tabulate_model.txt`: The PICT model file defining factors, levels, and constraints.
*   `pairwise_tests.csv`: The generated pairwise test cases (valid combinations).
*   `random_tests.csv`: A baseline set of randomly generated test cases.
*   `test_tabulate_pairwise.py`: Pytest runner for the pairwise suite.
*   `test_random.py`: Pytest runner for the random suite (includes constraint checks).
*   `generate_random_suite.py`: Script to generate the random test CSV.

### 4. Installation & Prerequisites

**1. Install Python Dependencies:**
```bash
pip install pytest tabulate pytest-cov
```

**2. (Optional) Install PICT:**
To regenerate the pairwise tests, you need the Microsoft PICT tool.
*   **Source:** [microsoft/pict](https://github.com/microsoft/pict)
*   **Installation:** Follow the build instructions in the PICT repository. Ensure the `pict` executable is in your PATH.

### 5. Usage Instructions

#### A. Generating Pairwise Tests
If you have PICT installed, you can regenerate the test suite:
```bash
pict tabulate_model.txt > pairwise_tests.csv
```
*Note: `pairwise_tests.csv` is already included in the repo, so this step is optional.*

#### B. Running the Pairwise Suite
Run the pairwise tests using pytest:
```bash
python3 -m pytest test_tabulate_pairwise.py
```
**Expected Result:** All tests should **PASS**. This confirms that the valid pairwise combinations function correctly in `tabulate`.

#### C. Running the Random Baseline
Run the random test suite:
```bash
python3 -m pytest test_random.py
```
**Expected Result:** Some tests will **FAIL**.
*   **Why?** The random generator (`generate_random_suite.py`) does not enforce constraints.
*   The test runner (`test_random.py`) acts as an oracle and raises `pytest.fail` when it encounters an invalid combination (e.g., trying to use "FirstRow" headers with a "ListOfDicts"). This demonstrates the value of the Pairwise model's constraints vs. pure random generation.

#### D. Measuring Coverage
To verify statement coverage of the test runner:
```bash
python3 -m pytest --cov=test_tabulate_pairwise test_tabulate_pairwise.py
```

### 6. Evaluation Report

*Use this section to record your findings after running the tests.*

| Metric | Pairwise Suite | Random Baseline |
| :--- | :--- | :--- |
| **Total Tests** | 18 | 18 |
| **Valid Tests** | 18| 7 |
| **Invalid Tests (Constraint Violations)** | 0 | 11 |
| **Bugs Found** | [Enter count] | [Enter count] |
| **Statement Coverage** | [Enter %] | [Enter %] |

**Key Findings:**
1.  [Observation about efficiency]
2.  [Observation about validity/constraints]
3.  [Observation about coverage]
