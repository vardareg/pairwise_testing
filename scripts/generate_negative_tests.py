
import csv
import os

def generate_negative_tests():
    # Define the failing test cases based on constraint violations
    cases = [
        {
            "InputType": "ListOfDicts",
            "HeadersMode": "FirstRow",
            "TableFormat": "plain",
            "RowIndices": "never",
            "MissingValues": "Default",
            "DataMix": "Strings",
            "Size": "Small2x2",
            "ExpectedException": "ValueError"
        },
        {
            "InputType": "DictOfColumns",
            "HeadersMode": "FirstRow",
            "TableFormat": "plain",
            "RowIndices": "never",
            "MissingValues": "Default",
            "DataMix": "Strings",
            "Size": "Small2x2",
            "ExpectedException": "ValueError"
        },
        {
            "InputType": "ListOfLists",
            "HeadersMode": "Keys",
            "TableFormat": "plain",
            "RowIndices": "never",
            "MissingValues": "Default",
            "DataMix": "Strings",
            "Size": "Small2x2",
            "ExpectedException": "ValueError"
        }
    ]

    fieldnames = [
        "InputType", "HeadersMode", "TableFormat", "RowIndices",
        "MissingValues", "DataMix", "Size", "ExpectedException"
    ]

    output_path = os.path.join("data", "negative_tests.csv")

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',') # Using comma for standard CSV
        writer.writeheader()
        for case in cases:
            writer.writerow(case)

    print(f"Generated {len(cases)} negative test cases in {output_path}")

if __name__ == "__main__":
    generate_negative_tests()
