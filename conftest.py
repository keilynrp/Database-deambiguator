"""
Root conftest — ensures the repo root is on sys.path so that
`import backend` works when pytest is invoked from any working directory.
"""
import sys
import os

# Insert repo root at the front of sys.path
sys.path.insert(0, os.path.dirname(__file__))
