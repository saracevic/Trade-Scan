"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_dir)
