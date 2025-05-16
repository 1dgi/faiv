import os
import sys

# Get the root of your project (adjust if necessary)
project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, project_path)

from faiv_app.core import application
