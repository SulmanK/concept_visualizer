"""
Tests for logging setup utilities.
"""

import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from app.utils.logging.setup import setup_logging, is_health_check


class TestSetupLogging:
    """Tests for the setup_logging function."""

    @patch("app.utils.logging.setup.logging.StreamHandler")
    @patch("app.utils.logging.setup.logging.handlers.RotatingFileHandler")
    @patch("app.utils.logging.setup.Path")
    def test_setup_logging_default_settings(
        self, mock_path, mock_rotating_handler, mock_stream_handler
    ):
        """Test setup_logging with default settings."""
        # Setup
        mock_formatter = MagicMock()
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True  # Log directory exists
        
        # Mock stream handler
        mock_stream_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_stream_handler_instance
        
        # Mock rotating handlers
        mock_app_handler = MagicMock()
        mock_error_handler = MagicMock()
        mock_rotating_handler.side_effect = [mock_app_handler, mock_error_handler]
        
        # Mock root logger
        mock_root_logger = MagicMock()
        
        with patch("app.utils.logging.setup.logging.getLogger", return_value=mock_root_logger), \
             patch("app.utils.logging.setup.logging.Formatter", return_value=mock_formatter):
            
            # Execute
            setup_logging()
            
            # Assert
            # Check log level was set correctly
            mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
            
            # Check console handler was added
            mock_stream_handler.assert_called_once()
            mock_stream_handler_instance.setFormatter.assert_called_once_with(mock_formatter)
            
            # Check file handlers were created with correct settings
            assert mock_rotating_handler.call_count == 2
            mock_app_handler.setFormatter.assert_called_once_with(mock_formatter)
            mock_error_handler.setFormatter.assert_called_once_with(mock_formatter)
            
            # Error handler should have ERROR level
            mock_error_handler.setLevel.assert_called_once_with(logging.ERROR)
            
            # Check all handlers were added to root logger
            assert mock_root_logger.addHandler.call_count == 3
            mock_root_logger.addHandler.assert_has_calls([
                call(mock_stream_handler_instance),
                call(mock_app_handler),
                call(mock_error_handler)
            ])

    @patch("app.utils.logging.setup.logging.StreamHandler")
    @patch("app.utils.logging.setup.Path")
    def test_setup_logging_create_log_dir(
        self, mock_path, mock_stream_handler
    ):
        """Test setup_logging creating a log directory if it doesn't exist."""
        # Setup
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False  # Log directory does not exist
        
        # Mock stream handler
        mock_stream_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_stream_handler_instance
        
        # Mock root logger
        mock_root_logger = MagicMock()
        
        with patch("app.utils.logging.setup.logging.getLogger", return_value=mock_root_logger), \
             patch("app.utils.logging.setup.logging.Formatter"):
            
            # Execute
            setup_logging()
            
            # Assert
            # Check log directory was created
            mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("app.utils.logging.setup.logging.StreamHandler")
    @patch("app.utils.logging.setup.logging.handlers.RotatingFileHandler")
    @patch("app.utils.logging.setup.Path")
    def test_setup_logging_custom_level(
        self, mock_path, mock_rotating_handler, mock_stream_handler
    ):
        """Test setup_logging with custom log level."""
        # Setup
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        
        # Mock handlers
        mock_stream_handler.return_value = MagicMock()
        mock_rotating_handler.side_effect = [MagicMock(), MagicMock()]
        
        # Mock root logger
        mock_root_logger = MagicMock()
        
        with patch("app.utils.logging.setup.logging.getLogger", return_value=mock_root_logger), \
             patch("app.utils.logging.setup.logging.Formatter"):
            
            # Execute
            setup_logging(log_level="DEBUG")
            
            # Assert
            # Check log level was set correctly
            mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)

    @patch("app.utils.logging.setup.logging.StreamHandler")
    @patch("app.utils.logging.setup.Path")
    def test_setup_logging_custom_format(
        self, mock_path, mock_stream_handler
    ):
        """Test setup_logging with custom log format."""
        # Setup
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        
        # Custom format
        custom_format = "%(levelname)s - %(name)s: %(message)s"
        
        # Mock formatter
        mock_formatter = MagicMock()
        
        with patch("app.utils.logging.setup.logging.getLogger"), \
             patch("app.utils.logging.setup.logging.Formatter", return_value=mock_formatter) as mock_formatter_class, \
             patch("app.utils.logging.setup.logging.handlers.RotatingFileHandler"):
            
            # Execute
            setup_logging(log_format=custom_format)
            
            # Assert
            # Check formatter was created with custom format
            mock_formatter_class.assert_called_once_with(custom_format)

    @patch("app.utils.logging.setup.logging.StreamHandler")
    @patch("app.utils.logging.setup.Path")
    def test_setup_logging_clear_existing_handlers(
        self, mock_path, mock_stream_handler
    ):
        """Test setup_logging clears existing handlers."""
        # Setup
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        
        # Create mock handlers
        mock_existing_handler1 = MagicMock()
        mock_existing_handler2 = MagicMock()
        
        # Mock root logger with existing handlers
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = [mock_existing_handler1, mock_existing_handler2]  # Existing handlers
        
        with patch("app.utils.logging.setup.logging.getLogger", return_value=mock_root_logger), \
             patch("app.utils.logging.setup.logging.Formatter"), \
             patch("app.utils.logging.setup.logging.handlers.RotatingFileHandler"):
            
            # Execute
            setup_logging()
            
            # Assert that clear was called (by checking that handlers.clear() was called)
            assert mock_root_logger.handlers != [mock_existing_handler1, mock_existing_handler2]
            # We can also verify that addHandler was called at least once
            assert mock_root_logger.addHandler.called


class TestIsHealthCheck:
    """Tests for the is_health_check function."""

    @pytest.mark.parametrize("path,expected", [
        ("/health", True),
        ("/api/health", True),
        ("/ping", True),
        ("/api/ping", True),
        ("/_health", True),
        ("/api/v1/health", True),
        ("/api/services/health", True),
        ("/api/services/ping", True),
        ("/api/concepts/generate", False),
        ("/api/storage/recent", False),
        ("/", False),
        ("/api", False),
        ("/healthcheck", False),  # Not an exact match
    ])
    def test_is_health_check(self, path, expected):
        """Test is_health_check with various paths."""
        assert is_health_check(path) == expected 