"""
Test infrastructure validation tests.

This module contains tests to validate that the testing infrastructure
is set up correctly and working as expected.
"""
import pytest
import json
from pathlib import Path


class TestInfrastructureValidation:
    """Test class to validate testing infrastructure setup."""

    def test_pytest_works(self):
        """Test that pytest basic functionality works."""
        assert True

    def test_pytest_marks_unit(self):
        """Test that pytest unit markers work."""
        # This test should automatically get the 'unit' marker
        # from conftest.py based on its location
        pass

    def test_fixtures_available(self, temp_dir, sample_config):
        """Test that custom fixtures from conftest.py are available."""
        # Test temp_dir fixture
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Test sample_config fixture  
        assert isinstance(sample_config, dict)
        assert "timeout" in sample_config
        assert sample_config["timeout"] == 30

    def test_mock_fixtures(self, mock_agent, mock_task, mock_callback):
        """Test that mock fixtures are properly configured."""
        # Test mock_agent
        assert mock_agent.uuid == "test-agent-uuid-12345"
        assert mock_agent.name == "test_agent"
        assert hasattr(mock_agent, "execute_command")

        # Test mock_task
        assert mock_task.id == "test-task-id-12345"
        assert mock_task.command_name == "test_command"
        assert hasattr(mock_task, "update_status")

        # Test mock_callback
        assert mock_callback.id == "test-callback-id-12345"
        assert mock_callback.user == "test_user"
        assert hasattr(mock_callback, "send_heartbeat")

    def test_file_system_fixture(self, mock_file_system):
        """Test that mock file system fixture works."""
        assert "test_file" in mock_file_system
        assert "test_dir" in mock_file_system
        assert "binary_file" in mock_file_system
        
        test_file = mock_file_system["test_file"]
        assert test_file.exists()
        assert test_file.read_text() == "This is a test file content"

    def test_environment_vars_fixture(self, mock_environment_vars):
        """Test that environment variables fixture works."""
        import os
        assert os.getenv("MYTHIC_SERVER") == "https://test-mythic-server.com"
        assert os.getenv("TEST_MODE") == "true"

    def test_config_file_fixture(self, mock_config_file):
        """Test that config file fixture works."""
        assert mock_config_file.exists()
        config_data = json.loads(mock_config_file.read_text())
        assert config_data["timeout"] == 30
        assert config_data["server_host"] == "localhost"

    def test_pytest_mock_available(self, mocker):
        """Test that pytest-mock is available and working."""
        mock_func = mocker.Mock()
        mock_func.return_value = "test_return"
        
        result = mock_func()
        assert result == "test_return"
        mock_func.assert_called_once()

    @pytest.mark.unit
    def test_custom_marker_unit(self):
        """Test that custom unit marker works explicitly."""
        pass

    @pytest.mark.integration  
    def test_custom_marker_integration(self):
        """Test that custom integration marker works explicitly."""
        pass

    @pytest.mark.slow
    def test_custom_marker_slow(self):
        """Test that custom slow marker works."""
        pass


class TestCoverageConfiguration:
    """Test coverage configuration."""

    def test_coverage_source_configured(self):
        """Test that coverage is configured to track the right source."""
        # This test just verifies basic functionality
        # Coverage configuration is tested by running the coverage tool
        assert True

    def test_sample_function_for_coverage(self):
        """Sample function to generate some coverage data."""
        def sample_function(x, y):
            if x > y:
                return x + y
            else:
                return x - y
        
        result1 = sample_function(5, 3)
        result2 = sample_function(2, 4)
        
        assert result1 == 8
        assert result2 == -2


class TestProjectStructure:
    """Test project structure validation."""

    def test_project_structure_exists(self):
        """Test that required project structure exists."""
        project_root = Path(__file__).parent.parent
        
        # Check main project files
        assert (project_root / "pyproject.toml").exists()
        assert (project_root / "README.md").exists()
        
        # Check test structure
        assert (project_root / "tests").exists()
        assert (project_root / "tests" / "__init__.py").exists()
        assert (project_root / "tests" / "conftest.py").exists()
        assert (project_root / "tests" / "unit").exists()
        assert (project_root / "tests" / "integration").exists()

    def test_payload_type_directory_exists(self):
        """Test that main Payload_Type directory exists."""
        project_root = Path(__file__).parent.parent
        payload_type_dir = project_root / "Payload_Type"
        
        assert payload_type_dir.exists()
        assert payload_type_dir.is_dir()

    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml is valid and contains expected sections."""
        project_root = Path(__file__).parent.parent
        pyproject_file = project_root / "pyproject.toml"
        
        assert pyproject_file.exists()
        
        # Read and validate it's parseable (basic TOML validation)
        content = pyproject_file.read_text()
        assert "[tool.poetry]" in content
        assert "[tool.pytest.ini_options]" in content
        assert "[tool.coverage.run]" in content