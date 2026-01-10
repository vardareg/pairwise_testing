import csv
import random
from pathlib import Path

# 1. Define Domains (The Input Factors)
domains = {
    "InputType":      ["ListOfLists", "ListOfDicts", "DictOfColumns"],
    "HeadersMode":    ["Explicit", "FirstRow", "Keys"],
    "TableFormat":    ["plain", "github", "grid", "psql"],
    "RowIndices":     ["always", "never", "Custom"],
    "MissingValues":  ["Default", "NA"],
    "DataMix":        ["Strings", "IntsFloats", "MixedNone"],
    "Size":           ["Small2x2", "Medium5x4", "WideText"]
}

# 2. Define Constraints Logic (Python version of PICT logic)
def is_valid_combination(case):
    return True

# 3. Generator
def generate_random_tests(num_tests=20):
    fieldnames = list(domains.keys())
    tests = []
    
    attempts = 0
    while len(tests) < num_tests and attempts < 1000:
        attempts += 1
        
        # Pick one random value for each parameter
        candidate = {k: random.choice(v) for k, v in domains.items()}
        
        # Check if it's a valid test case
        if is_valid_combination(candidate):
            # Check for duplicates (optional, but good for small sets)
            if candidate not in tests:
                tests.append(candidate)
    
    return tests, fieldnames

# 4. Write to CSV
if __name__ == "__main__":
    # We aim for 20 tests (approximate number a PICT 2-wise model would generate for this complexity)
    generated_tests, headers = generate_random_tests(18)
    
    data_dir = Path(__file__).parent.parent / "data"
    filename = data_dir / "random_tests.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(generated_tests)
        
    print(f"Generated {len(generated_tests)} random test cases in '{filename}'.")
    print("You can run these using the same Pytest script by changing the CSV filename.")