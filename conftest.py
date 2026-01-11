import pytest
from utils import TestDataFactory, load_cases

@pytest.fixture(scope="session")
def data_factory():
    """Fixture that returns the TestDataFactory class."""
    return TestDataFactory

def pytest_generate_tests(metafunc):
    """
    Automated parametrization based on fixture names.
    - 'pairwise_case': loads pairwise_tests.csv
    - 'random_case': loads random_tests.csv
    """
    if "pairwise_case" in metafunc.fixturenames:
        cases = load_cases("pairwise_tests.csv")
        metafunc.parametrize("pairwise_case", cases)

    if "random_case" in metafunc.fixturenames:
        cases = load_cases("random_tests.csv")
        metafunc.parametrize("random_case", cases)
