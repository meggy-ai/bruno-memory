"""
Pytest configuration and fixtures for bruno-memory tests.

This module provides common fixtures and configuration for the test suite.
"""

import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock

from bruno_core.models import Message, MessageRole


@pytest.fixture
def sample_message() -> Message:
    """Create a sample message for testing."""
    return Message(
        role=MessageRole.USER,
        content="Hello, this is a test message"
    )


@pytest.fixture
def sample_messages() -> list[Message]:
    """Create multiple sample messages for testing."""
    return [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi! How can I help you?"),
        Message(role=MessageRole.USER, content="Tell me about the weather"),
    ]


@pytest.fixture
def conversation_id() -> str:
    """Provide a test conversation ID."""
    return "test_conv_123"


@pytest.fixture
def user_id() -> str:
    """Provide a test user ID."""
    return "test_user_456"


# Add more fixtures as backends are implemented
