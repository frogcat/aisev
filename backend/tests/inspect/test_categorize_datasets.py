import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch, mock_open
from src.inspect.categorize_datasets import DataCategorizer
from pathlib import Path
from inspect_ai.model import get_model


@pytest.mark.asyncio
async def test_exec_categorize_data():
    """Test exec_categorize_data method with mocked dependencies"""
    # Create a mock model
    mock_model = Mock()
    categorizer = DataCategorizer(mock_model)

    # Create test DataFrame
    test_df = pd.DataFrame({
        'text': ['test input 1', 'test input 2'],
        'output': ['test output 1', 'test output 2']
    })

    # Mock YAML content
    mock_yaml_content = """
    goals:
      - id: G1
        statement: "Test goal"
    """

    # Mock GSNExplorer results
    mock_explorer_results = [
        {"ID": "G1", "leaf": "Test leaf 1"},
        {"ID": "G2", "leaf": "Test leaf 2"}
    ]

    # Mock the categorize_data_with_input_output_GSN method
    categorizer.categorize_data_with_input_output_GSN = AsyncMock(
        return_value="G1")

    with patch("builtins.open", mock_open(read_data=mock_yaml_content)), \
            patch("yaml.safe_load", return_value={"test": "data"}), \
            patch("src.gsn.gsn_explorer.GSNExplorer") as mock_gsn_explorer:

        # Setup mock GSNExplorer
        mock_explorer_instance = Mock()
        mock_explorer_instance.explore.return_value = mock_explorer_results
        mock_gsn_explorer.return_value = mock_explorer_instance

        # Execute the method
        result = await categorizer.exec_categorize_data(test_df)

        # Verify results
        assert len(result) == 40  # 2 leaves * 2 rows * 10 GSN files
        assert all(r == "G1" for r in result)  # All should return "G1"

        # Verify GSNExplorer was called for each GSN file
        assert mock_gsn_explorer.call_count == 10

        # Verify categorize_data_with_input_output_GSN was called correctly
        assert categorizer.categorize_data_with_input_output_GSN.call_count == 40


root = Path(__file__).parent.parent.parent
data_dir = root / "dataset"
data_output_dir = data_dir / "output"


@pytest.mark.asyncio
async def test_exec_categorize_data_with_real_data():
    """Test exec_categorize_data method with actual data structure from categorize_datasets.py"""
    # Test with actual data structure

    # Setup test data directory

    # Skip test if data file doesn't exist
    parquet_file = data_dir / "test-00000-of-00001.parquet"
    print(data_dir)
    if not parquet_file.exists():
        pytest.skip(f"Test data file {parquet_file} not found")

    df = pd.read_parquet(data_dir / "test-00000-of-00001.parquet")
    df = df.sample(10, random_state=42)
    model = get_model(
        "openai/gpt-4o-mini",
    )
    categorizer = DataCategorizer(model)

    # Execute categorization
    result = await categorizer.exec_categorize_data(df)

    # Basic assertions
    assert isinstance(result, list)
    assert len(result) > 0
    # Each result should be a string (category ID)
    assert all(isinstance(r, str) for r in result)
