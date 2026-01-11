import pytest
from tabulate import tabulate

# ---------------------------------------------------------
# HELPER: DATA GENERATION FACTORY (Copied from test_tabulate_pairwise.py)
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

# ---------------------------------------------------------
# NEGATIVE TEST CASES
# ---------------------------------------------------------

def test_dict_with_firstrow_headers():
    """
    Constraint Violation: InputType is Dict-based AND HeadersMode is "FirstRow".
    Expected Behavior: Should run gracefully (no crash) and return a string.
    """
    # 1. Setup invalid combination
    input_type = "ListOfDicts"
    headers = "firstrow"

    # Generate standard data
    raw_data = TestDataFactory.generate_data(input_type, "Strings", "Small2x2")

    # 2. Execute
    try:
        result = tabulate(raw_data, headers=headers)
    except Exception as e:
        pytest.fail(f"Tabulate crashed on Dict + FirstRow: {e}")

    # 3. Assert
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be empty"


def test_list_with_keys_headers():
    """
    Constraint Violation: HeadersMode is "Keys" AND InputType is NOT Dict-based.
    Expected Behavior: Should run gracefully (no crash) and return a string.
    """
    # 1. Setup invalid combination
    input_type = "ListOfLists"
    headers = "keys"

    # Generate standard data
    raw_data = TestDataFactory.generate_data(input_type, "Strings", "Small2x2")

    # 2. Execute
    try:
        result = tabulate(raw_data, headers=headers)
    except Exception as e:
        pytest.fail(f"Tabulate crashed on List + Keys: {e}")

    # 3. Assert
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be empty"


def test_widetext_plain_format():
    """
    Constraint Violation: Size is "WideText" AND TableFormat is NOT grid-like (e.g., "plain").
    Expected Behavior: Should run gracefully (no crash) and return a string.
    """
    # 1. Setup invalid combination
    size = "WideText"
    tablefmt = "plain"

    # Generate wide data
    raw_data = TestDataFactory.generate_data("ListOfLists", "Strings", size)

    # 2. Execute
    try:
        result = tabulate(raw_data, tablefmt=tablefmt)
    except Exception as e:
        pytest.fail(f"Tabulate crashed on WideText + Plain: {e}")

    # 3. Assert
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be empty"
