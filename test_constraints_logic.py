import pytest
from tabulate import tabulate

def is_valid_case(case_dict):
    """
    Validates the 5 constraints from the design spec.
    Returns True if valid, False otherwise.
    """
    input_type = case_dict.get('InputType', '')
    headers_mode = case_dict.get('HeadersMode', '')
    missing_values = case_dict.get('MissingValues', '')
    data_mix = case_dict.get('DataMix', '')
    size = case_dict.get('Size', '')
    table_fmt = case_dict.get('TableFormat', '')

    # 1. InputType in ["ListOfDicts", "DictOfColumns"] -> HeadersMode != "FirstRow"
    if input_type in ["ListOfDicts", "DictOfColumns"] and headers_mode == "FirstRow":
        return False

    # 2. HeadersMode == "Keys" -> InputType in ["ListOfDicts", "DictOfColumns"]
    if headers_mode == "Keys" and input_type not in ["ListOfDicts", "DictOfColumns"]:
        return False

    # 3. MissingValues == "NA" -> DataMix == "MixedNone"
    if missing_values == "NA" and data_mix != "MixedNone":
        return False

    # 4. InputType == "ListOfLists" -> HeadersMode != "Keys"
    if input_type == "ListOfLists" and headers_mode == "Keys":
        return False

    # 5. Size == "WideText" -> TableFormat in ["grid", "psql", "github"]
    if size == "WideText" and table_fmt not in ["grid", "psql", "github"]:
        return False

    return True

def run_tabulate_check(case, data_factory):
    """
    Helper to generate data and run tabulate.
    Returns True if successful (output length > 0), raises Assertion/Exception otherwise.
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
            kwargs['showindex'] = showindex_arg[1:]
        else:
            kwargs['showindex'] = showindex_arg

    if missingval_arg:
        kwargs['missingval'] = missingval_arg

    try:
        result = tabulate(raw_data, **kwargs)
    except Exception as e:
        pytest.fail(f"Tabulate crashed: {e}")

    return len(result) > 0


def test_pairwise_constraints(pairwise_case, data_factory):
    """
    Validates & Executes Pairwise Suite.
    - Assert ALL rows return True for is_valid_case.
    - Run the SUT.
    """
    # 1. Validate Constraint
    valid = is_valid_case(pairwise_case)
    assert valid, f"Pairwise case generated invalid combination: {pairwise_case}"

    # 2. Run SUT
    # Note: This might fail if the known bug exists in tabulate.
    # The requirement is "Run the SUT for these to ensure they pass".
    # If there is a known bug, this test will fail, which is expected behavior for a QA test suite detecting bugs.
    output_ok = run_tabulate_check(pairwise_case, data_factory)
    assert output_ok, "Tabulate returned empty output for valid pairwise case"

def test_random_constraints(random_case, data_factory):
    """
    Validates & Executes Random Suite.
    - Determine validity.
    - IF Valid: Run SUT, Expect Success.
    - IF Invalid: Run SUT, Expect Success (Robustness/Graceful Exit).
    """
    # 1. Determine Validity
    valid = is_valid_case(random_case)

    # 2. Log Status
    # Using print to stdout, accessible with -s
    print(f"Validating row: {'Valid' if valid else 'Invalid'} - {random_case}")

    # 3. Run SUT (Robustness Check)
    # Even invalid cases should not crash the system.
    output_ok = run_tabulate_check(random_case, data_factory)
    assert output_ok, "Tabulate returned empty output (or crashed) for random case"
