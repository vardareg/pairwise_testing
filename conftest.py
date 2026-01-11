import csv
import os
import pytest

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
# CSV LOADING & PARAMETRIZATION
# ---------------------------------------------------------
def load_cases(filename):
    cases = []
    if not os.path.exists(filename):
        return []

    with open(filename, 'r') as f:
        # Read first line to detect delimiter
        line = f.readline()
        f.seek(0)

        # Simple heuristic: count tabs vs commas
        delimiter = '\t' if line.count('\t') > line.count(',') else ','

        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            cases.append(row)
    return cases

# Expose load_cases to pytest namespace for DRY usage in test files
pytest.load_cases = load_cases

@pytest.fixture(scope="session")
def data_factory():
    """Fixture that returns the TestDataFactory class."""
    return TestDataFactory
