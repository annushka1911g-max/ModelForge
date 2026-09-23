"""
Unit tests for framework adapters skeleton.
"""
import pytest
from inference.adapters.base import BaseModelAdapter


def test_base_adapter_abstract():
    """
    Ensure BaseModelAdapter cannot be instantiated directly without implementations.
    """
    with pytest.raises(TypeError):
        BaseModelAdapter("dummy/path")
