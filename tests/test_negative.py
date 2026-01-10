import pytest
import csv
from pathlib import Path
from tabulate import tabulate

# ---------------------------------------------------------
# HELPER: DATA GENERATION FACTORY (Copied to ensure self-containment)
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
def load_negative_cases():
    cases = []
    try:
        data_path = Path(__file__).parent.parent / "data" / "negative_tests.csv"
        with open(data_path, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                cases.append(row)
    except FileNotFoundError:
        pytest.fail("negative_tests.csv not found")
    return cases

test_cases = load_negative_cases()

# ---------------------------------------------------------
# PYTEST EXECUTION
# ---------------------------------------------------------
@pytest.mark.parametrize("case", test_cases)
def test_negative_constraints(case):
    """
    Executes negative test cases. Expects strict ValueError.
    """
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

    kwargs = {'tablefmt': case['TableFormat']}
    if headers_arg:
        kwargs['headers'] = headers_arg

    if showindex_arg != "default":
        # Safe handling if slicing fails (though it shouldn't for negative tests)
        if headers_arg == "firstrow" and isinstance(showindex_arg, list):
             kwargs['showindex'] = showindex_arg[1:]
        else:
             kwargs['showindex'] = showindex_arg

    if missingval_arg:
        kwargs['missingval'] = missingval_arg

    # 2. Execution & Assertion
    # We expect a ValueError because these are invalid combinations per the model
    with pytest.raises(ValueError, match="not supported"):
        tabulate(raw_data, **kwargs)
