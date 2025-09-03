"""
Shared pytest fixtures for the Apfell testing suite.

This file contains common fixtures and test utilities that can be used
across all test modules in the project.
"""
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test files.
    
    Returns:
        Path: Temporary directory path that is automatically cleaned up.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """
    Provide a sample configuration dictionary for testing.
    
    Returns:
        Dict[str, Any]: Sample configuration with common settings.
    """
    return {
        "debug": False,
        "timeout": 30,
        "max_retries": 3,
        "default_sleep": 1,
        "user_agent": "Mozilla/5.0 (compatible; Test)",
        "server_host": "localhost",
        "server_port": 8080,
    }


@pytest.fixture
def mock_config_file(temp_dir: Path, sample_config: Dict[str, Any]) -> Path:
    """
    Create a mock configuration file in the temp directory.
    
    Args:
        temp_dir: Temporary directory fixture
        sample_config: Sample configuration fixture
        
    Returns:
        Path: Path to the created config file.
    """
    config_file = temp_dir / "config.json"
    config_file.write_text(json.dumps(sample_config, indent=2))
    return config_file


@pytest.fixture
def mock_agent():
    """
    Create a mock agent object for testing.
    
    Returns:
        Mock: Mock agent with common methods and properties.
    """
    agent = Mock()
    agent.uuid = "test-agent-uuid-12345"
    agent.name = "test_agent"
    agent.sleep_time = 5
    agent.jitter = 0.1
    agent.kill_date = None
    agent.working_hours = None
    agent.user_agent = "Mozilla/5.0 (compatible; Test)"
    agent.host = "test-host"
    agent.user = "test-user"
    agent.domain = "test-domain"
    agent.architecture = "x64"
    agent.process_name = "test_process"
    agent.pid = 1234
    agent.ip = "192.168.1.100"
    
    # Mock methods
    agent.execute_command = Mock(return_value={"status": "success", "output": ""})
    agent.send_response = Mock(return_value=True)
    agent.get_config = Mock(return_value={})
    
    return agent


@pytest.fixture
def mock_task():
    """
    Create a mock task object for testing.
    
    Returns:
        Mock: Mock task with common properties and methods.
    """
    task = Mock()
    task.id = "test-task-id-12345"
    task.command_name = "test_command"
    task.parameters = {}
    task.timestamp = "2023-01-01T00:00:00Z"
    task.operator = "test_operator"
    task.callback = "test-callback-id"
    task.status = "submitted"
    task.completed = False
    
    # Mock methods
    task.update_status = Mock()
    task.add_response = Mock()
    task.mark_complete = Mock()
    task.mark_error = Mock()
    
    return task


@pytest.fixture
def mock_callback():
    """
    Create a mock callback object for testing.
    
    Returns:
        Mock: Mock callback with common properties and methods.
    """
    callback = Mock()
    callback.id = "test-callback-id-12345"
    callback.agent_callback_id = "test-agent-callback-id"
    callback.user = "test_user"
    callback.host = "test-host"
    callback.pid = 1234
    callback.ip = "192.168.1.100"
    callback.external_ip = "203.0.113.1"
    callback.process_name = "test_process"
    callback.integrity_level = 2
    callback.locked = False
    callback.active = True
    
    # Mock methods  
    callback.update_info = Mock()
    callback.send_heartbeat = Mock()
    callback.get_tasks = Mock(return_value=[])
    
    return callback


@pytest.fixture
def mock_mythic_response():
    """
    Create a mock Mythic server response for testing.
    
    Returns:
        Mock: Mock response object with common structure.
    """
    response = Mock()
    response.status_code = 200
    response.ok = True
    response.json = Mock(return_value={
        "status": "success",
        "output": "",
        "tasks": [],
        "responses": []
    })
    response.text = '{"status": "success"}'
    response.headers = {"Content-Type": "application/json"}
    
    return response


@pytest.fixture
def mock_file_system(temp_dir: Path):
    """
    Create a mock file system structure for testing file operations.
    
    Args:
        temp_dir: Temporary directory fixture
        
    Returns:
        Dict[str, Path]: Dictionary mapping file names to their paths.
    """
    files = {}
    
    # Create some test files
    test_file = temp_dir / "test_file.txt"
    test_file.write_text("This is a test file content")
    files["test_file"] = test_file
    
    # Create a test directory with files
    test_dir = temp_dir / "test_directory"
    test_dir.mkdir()
    
    nested_file = test_dir / "nested_file.txt"
    nested_file.write_text("Nested file content")
    files["nested_file"] = nested_file
    
    # Create a binary test file
    binary_file = temp_dir / "test_binary.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")
    files["binary_file"] = binary_file
    
    files["base_dir"] = temp_dir
    files["test_dir"] = test_dir
    
    return files


@pytest.fixture
def mock_environment_vars(monkeypatch):
    """
    Set up mock environment variables for testing.
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    test_env = {
        "MYTHIC_SERVER": "https://test-mythic-server.com",
        "MYTHIC_TOKEN": "test-token-12345",
        "MYTHIC_CALLBACK_ID": "test-callback-id",
        "DEBUG": "false",
        "TEST_MODE": "true"
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env


@pytest.fixture(autouse=True)
def reset_mocks():
    """
    Automatically reset all mocks after each test.
    This fixture runs automatically for every test.
    """
    yield
    # Any cleanup code can go here if needed


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test") 
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test location.
    
    Automatically adds 'unit' marker to tests in tests/unit/
    and 'integration' marker to tests in tests/integration/
    """
    for item in items:
        # Add unit marker to tests in unit directory
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration directory  
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)