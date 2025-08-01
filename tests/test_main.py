from unittest.mock import patch, mock_open
from pathlib import Path
import pytest
import json

from scigetup.app import main, create_desktop_file

# Test for create_desktop_file function
def test_create_desktop_file_gui():
    # Mocks
    mock_path = Path("/fake/dir")
    app_info = {"name": "TestApp", "executable": "testapp-gui", "gui": True}
    
    # Use mock_open to simulate file operations
    m = mock_open()
    with patch("builtins.open", m), patch("pathlib.Path.chmod") as mock_chmod:
        create_desktop_file(mock_path, app_info)

    # Assertions
    m.assert_called_once_with(mock_path / "TestApp.desktop", "w")
    handle = m()
    
    # Check that the content written to the file is correct
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    assert "[Desktop Entry]" in written_content
    assert "Name=TestApp" in written_content
    # Corrected assertion for the Exec command
    assert 'Exec=x-terminal-emulator -- bash -c "module load TestApp; testapp-gui"' in written_content
    assert "Terminal=false" in written_content
    
    # Check that chmod was called
    mock_chmod.assert_called_once()

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
