import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from shared.logger import setup_logger


def test_setup_logger_basic():
    """Test basic logger setup"""
    logger = setup_logger("test_bot")
    assert logger.name == "test_bot"
    assert len(logger.handlers) == 2


def test_setup_logger_log_level():
    """Test logger respects LOG_LEVEL environment variable"""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        logger = setup_logger("debug_bot")
        assert logger.level == logging.DEBUG


def test_setup_logger_creates_log_directory():
    """Test that logger creates logs directory"""
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("shared.logger.Path") as mock_path,
    ):
        mock_log_dir = Path(temp_dir) / "logs"
        mock_path.return_value = mock_log_dir
        setup_logger("dir_test_bot")
        assert mock_log_dir.exists()


def test_setup_logger_default_log_level():
    """Test logger uses INFO as default log level"""
    with patch.dict(os.environ, {}, clear=True):
        logger = setup_logger("default_bot")
        assert logger.level == logging.INFO


def test_setup_logger_handlers_cleared():
    """Test that existing handlers are cleared"""
    logger = setup_logger("clear_test_bot")
    initial_handler_count = len(logger.handlers)

    logger = setup_logger("clear_test_bot")
    assert len(logger.handlers) == initial_handler_count
