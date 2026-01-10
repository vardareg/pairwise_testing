import pytest
import csv
import sys
from tabulate import tabulate

# ---------------------------------------------------------
# HELPER: DATA GENERATION FACTORY
# ---------------------------------------------------------
class TestDataFactory:
    """
    Translates abstract PICT parameters into concrete Python objects
    for the tabulate library.
    """
    @staticmethod
    def generate_data(input_type, data_mix, size):
        rows = 2 if "Small" in size else 5
        cols = 2 if "Small" in size else 4

        # Base data generation
        data = []
        for r in range(rows):
            row_data = []
            for c in range(cols):
                val = f"r{r}c{c}" # Default string

                if data_mix == "IntsFloats":
                    val = r * 10 + c + 0.5
                elif data_mix == "MixedNone":
                    # Inject None in the middle of the dataset
                    if r == 1 and c == 1:
                        val = None
                    else:
                        val = f"val_{r}_{c}"

                if size == "WideText" and c == 0:
                    val = "This is a very long text string intended to test layout."

                row_data.append(val)
            data.append(row_data)

        # Structure formatting
        if input_type == "ListOfLists":
            return data

        elif input_type == "ListOfDicts":
            headers = [f"Head{i}" for i in range(cols)]
            return [dict(zip(headers, row)) for row in data]

        elif input_type == "DictOfColumns":
            headers = [f"Head{i}" for i in range(cols)]
            # Transpose
            col_dict = {}
            for i, h in enumerate(headers):
                col_dict[h] = [row[i] for row in data]
            return col_dict

        return data

    @staticmethod
    def get_headers(headers_mode, input_type, size):
        cols = 2 if "Small" in size else 4
        if headers_mode == "Explicit":
            if input_type == "ListOfDicts":
                return {f"Head{i}": f"Col_Hex_{i}" for i in range(cols)}
            return [f"Col_Hex_{i}" for i in range(cols)]
        elif headers_mode == "FirstRow":
            return "firstrow"
        elif headers_mode == "Keys":
            return "keys"
        return []

    @staticmethod
    def get_showindex(row_indices, size):
        rows = 2 if "Small" in size else 5
        if row_indices == "always":
            return "always"
        elif row_indices == "never":
            return "never"
        elif row_indices == "Custom":
            return [f"id_{i}" for i in range(rows)]
        return "default"

# ---------------------------------------------------------
# CSV LOADER
# ---------------------------------------------------------
def load_pict_cases():
    cases = []
    try:
        with open('random_tests.csv', 'r') as f:
            reader = csv.DictReader(f, delimiter='\t') # PICT usually outputs tab-separated
            # If PICT output comma, change delimiter to ','
            if reader.fieldnames and len(reader.fieldnames) == 1:
                 f.seek(0)
                 reader = csv.DictReader(f, delimiter=',')

            for row in reader:
                cases.append(row)
    except FileNotFoundError:
        print("WARNING: 'random_tests.csv' not found.")
        return []
    return cases

test_cases = load_pict_cases()

# ---------------------------------------------------------
# PYTEST EXECUTION
# ---------------------------------------------------------
@pytest.mark.parametrize("case", test_cases)
def test_tabulate_pairwise(case):
    """
    Executes one row from the PICT output.
    """
    # 0. Enforce Constraints
    # 1. IF [InputType] IN {"ListOfDicts", "DictOfColumns"} THEN [HeadersMode] <> "FirstRow";
    if case['InputType'] in ["ListOfDicts", "DictOfColumns"] and case['HeadersMode'] == "FirstRow":
        pytest.fail("Constraint Violation: FirstRow headers not supported for dict-based inputs")

    # 2 & 4. IF [HeadersMode] = "Keys" THEN [InputType] IN {"ListOfDicts", "DictOfColumns"};
    # (Equivalent to IF [InputType] = "ListOfLists" THEN [HeadersMode] <> "Keys")
    if case['InputType'] == "ListOfLists" and case['HeadersMode'] == "Keys":
        pytest.fail("Constraint Violation: Keys headers not supported for ListOfLists")

    # 3. IF [MissingValues] = "NA" THEN [DataMix] = "MixedNone";
    if case['MissingValues'] == "NA" and case['DataMix'] != "MixedNone":
        pytest.fail("Constraint Violation: MissingValues='NA' requires DataMix='MixedNone'")

    # 5. IF [Size] = "WideText" THEN [TableFormat] IN {"grid", "psql", "github"};
    if case['Size'] == "WideText" and case['TableFormat'] not in ["grid", "psql", "github"]:
        pytest.fail("Constraint Violation: WideText requires grid/psql/github format")

    # 1. Prepare Inputs
    raw_data = TestDataFactory.generate_data(
        case['InputType'],
        case['DataMix'],
        case['Size']
    )

    headers_arg = TestDataFactory.get_headers(
        case['HeadersMode'],
        case['InputType'],
        case['Size']
    )

    showindex_arg = TestDataFactory.get_showindex(
        case['RowIndices'],
        case['Size']
    )

    missingval_arg = "NA" if case['MissingValues'] == "NA" else ""

    # 2. Execution (The Action)
    try:
        # We construct the kwargs dynamically to handle default/empty cases
        kwargs = {'tablefmt': case['TableFormat']}

        if headers_arg:
            kwargs['headers'] = headers_arg

        if showindex_arg != "default":
            if headers_arg == "firstrow" and isinstance(showindex_arg, list):
                # When using firstrow, the first data row becomes the header
                # so the index list needs to be one shorter.
                kwargs['showindex'] = showindex_arg[1:]
            else:
                kwargs['showindex'] = showindex_arg

        if missingval_arg:
            kwargs['missingval'] = missingval_arg

        result = tabulate(raw_data, **kwargs)

    except Exception as e:
        pytest.fail(f"Tabulate crashed with params {case}: {str(e)}")

    # 3. Oracles (Assertions)

    # Oracle A: Result should not be empty
    assert len(result) > 0, "Output table was empty"

    # Oracle B: If we asked for 'NA' replacement and had None values, check for it
    if case['MissingValues'] == "NA" and case['DataMix'] == "MixedNone":
        assert "NA" in result, "Missing value was not replaced with 'NA'"

    # Oracle C: If headers are explicit, they should appear
    if case['HeadersMode'] == "Explicit":
        # Check first header specifically
        assert "Col_Hex_0" in result, "Explicit headers missing from output"