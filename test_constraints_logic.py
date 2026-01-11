import pytest
import os
from tabulate import tabulate

# ---------------------------------------------------------
# HELPER: CONSTRAINT VALIDATION
# ---------------------------------------------------------
def get_validity(case):
    """
    Validates the 5 constraints from the design spec.
    Returns (True, "Valid") if valid.
    Returns (False, "Constraint Violation: [Reason]") if invalid.
    """
    input_type = case.get('InputType', '')
    headers_mode = case.get('HeadersMode', '')
    missing_values = case.get('MissingValues', '')
    data_mix = case.get('DataMix', '')
    size = case.get('Size', '')
    table_fmt = case.get('TableFormat', '')

    # 1. InputType in ["ListOfDicts", "DictOfColumns"] -> HeadersMode != "FirstRow"
    if input_type in ["ListOfDicts", "DictOfColumns"] and headers_mode == "FirstRow":
        return False, f"Constraint Violation: InputType '{input_type}' incompatible with HeadersMode 'FirstRow'"

    # 2. HeadersMode == "Keys" -> InputType in ["ListOfDicts", "DictOfColumns"]
    if headers_mode == "Keys" and input_type not in ["ListOfDicts", "DictOfColumns"]:
        return False, f"Constraint Violation: HeadersMode 'Keys' requires InputType 'ListOfDicts' or 'DictOfColumns' (got '{input_type}')"

    # 3. MissingValues == "NA" -> DataMix == "MixedNone"
    if missing_values == "NA" and data_mix != "MixedNone":
        return False, f"Constraint Violation: MissingValues 'NA' requires DataMix 'MixedNone' (got '{data_mix}')"

    # 4. InputType == "ListOfLists" -> HeadersMode != "Keys"
    if input_type == "ListOfLists" and headers_mode == "Keys":
        return False, "Constraint Violation: InputType 'ListOfLists' incompatible with HeadersMode 'Keys'"

    # 5. Size == "WideText" -> TableFormat in ["grid", "psql", "github"]
    if size == "WideText" and table_fmt not in ["grid", "psql", "github"]:
        return False, f"Constraint Violation: Size 'WideText' requires TableFormat 'grid', 'psql', or 'github' (got '{table_fmt}')"

    return True, "Valid"

# ---------------------------------------------------------
# HELPER: PARAMETRIZATION GENERATOR
# ---------------------------------------------------------
def get_test_params(filename):
    """
    Reads CSV and generates pytest parameters with dynamic IDs.
    ID format: [VALID-RowN] or [INVALID-RowN]
    """
    # Use the shared loader from conftest (attached to pytest namespace)
    # This avoids DRY violation and duplicating CSV logic
    if not hasattr(pytest, 'load_cases'):
        # Fallback if conftest hasn't loaded (shouldn't happen in pytest execution)
        return []

    cases_data = pytest.load_cases(filename)
    params = []

    for i, row in enumerate(cases_data):
        valid, _ = get_validity(row)
        status_tag = "VALID" if valid else "INVALID"
        # User requested Row Index for brevity: [VALID-RowN]
        test_id = f"[{status_tag}-Row{i}]"
        params.append(pytest.param(row, id=test_id))

    return params

# ---------------------------------------------------------
# HELPER: SUT EXECUTION
# ---------------------------------------------------------
def run_tabulate_check(case, data_factory):
    """
    Helper to generate data and run tabulate.
    Returns True if successful (output length > 0).
    Raises Exception if tabulate crashes.
    """
    raw_data = data_factory.generate_data(
        case['InputType'],
        case['DataMix'],
        case['Size']
    )

    headers_arg = data_factory.get_headers(
        case['HeadersMode'],
        case['InputType'],
        case['Size']
    )

    showindex_arg = data_factory.get_showindex(
        case['RowIndices'],
        case['Size']
    )

    missingval_arg = "NA" if case['MissingValues'] == "NA" else ""

    kwargs = {'tablefmt': case['TableFormat']}

    if headers_arg:
        kwargs['headers'] = headers_arg

    if showindex_arg != "default":
        if headers_arg == "firstrow" and isinstance(showindex_arg, list):
            # Slice showindex if FirstRow consumes the first data row
            kwargs['showindex'] = showindex_arg[1:]
        else:
            kwargs['showindex'] = showindex_arg

    if missingval_arg:
        kwargs['missingval'] = missingval_arg

    result = tabulate(raw_data, **kwargs)
    return len(result) > 0

# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------

@pytest.mark.parametrize("case", get_test_params("pairwise_tests.csv"))
def test_pairwise_robustness(case, data_factory):
    """
    Validates & Executes Pairwise Suite (Expected 100% Valid).
    """
    # 1. Validate Constraint
    valid, reason = get_validity(case)
    assert valid, f"Pairwise case generated invalid combination: {reason}"

    # 2. Run SUT (Expected Green Path)
    try:
        output_ok = run_tabulate_check(case, data_factory)
        # Valid cases MUST produce output
        assert output_ok, "Tabulate returned empty output for valid pairwise case"
    except Exception as e:
        pytest.fail(f"Tabulate crashed on valid input: {e}")


@pytest.mark.parametrize("case", get_test_params("random_tests.csv"))
def test_random_robustness(case, data_factory):
    """
    Validates & Executes Random Suite (Mixed Valid/Invalid).
    Handles 'Green Path' (Valid) vs 'Robustness Path' (Invalid).
    """
    # 1. Determine Validity
    valid, reason = get_validity(case)

    if valid:
        # --- GREEN PATH ---
        # Assert SUT returns valid output.
        try:
            output_ok = run_tabulate_check(case, data_factory)
            assert output_ok, "Tabulate returned empty output for valid random case"
        except Exception as e:
            pytest.fail(f"Tabulate crashed on valid input: {e}")

    else:
        # --- ROBUSTNESS PATH ---
        # Assert the SUT does not crash.
        print(f"Skipping strict assertions for INVALID case: {reason}")
        try:
            # We don't assert output_ok here because invalid inputs might return empty strings.
            # We only care that it doesn't raise an exception.
            _ = run_tabulate_check(case, data_factory)
        except Exception as e:
            pytest.fail(f"Tabulate crashed on invalid input: {e}")
