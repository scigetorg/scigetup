from unittest.mock import patch, mock_open
from pathlib import Path
import pytest
import json

from scigetup.app import main, create_desktop_file

# Test for the main function
@patch('sys.argv', ['scigetup', 'fake/path/software.json'])
@patch('scigetup.app.Path.is_file', return_value=True) # Mock is_file to return True
@patch('scigetup.app.Path.home')
@patch('scigetup.app.Path.mkdir')
@patch('scigetup.app.create_desktop_file')
def test_main_success(mock_create_desktop, mock_mkdir, mock_home, mock_is_file):
    # Setup mocks
    mock_home.return_value = Path("/fake/home")
    
    # Mock file content
    mock_data = json.dumps({
        "Sample Category": {
            "software": [{"name": "TestApp", "executable": "testapp-cli"}]
        }
    })
    
    # Use mock_open to simulate opening the file
    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        # Run main
        main()

    # Assertions
    # Check that the file was "opened"
    mock_file.assert_called_once_with(Path('fake/path/software.json'), "r")
    
    # Check that the base directory is created
    mock_mkdir.assert_any_call(parents=True, exist_ok=True)
    
    # Check that create_desktop_file was called
    mock_create_desktop.assert_called_once()
    
    args, kwargs = mock_create_desktop.call_args
    assert args[1]['name'] == 'TestApp'
