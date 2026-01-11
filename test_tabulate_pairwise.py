import pytest
from tabulate import tabulate

# ---------------------------------------------------------
# PYTEST EXECUTION
# ---------------------------------------------------------
def test_tabulate_pairwise(pairwise_case, data_factory):
    """
    Executes one row from the PICT output.
    Uses `pairwise_case` fixture from conftest.py for data.
    Uses `data_factory` fixture from conftest.py for helper methods.
    """
    case = pairwise_case

    # 1. Prepare Inputs
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
