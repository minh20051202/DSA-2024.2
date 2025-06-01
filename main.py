#!/usr/bin/env python3

"""
Main entry point for the Debt Simplification Algorithm application

This script launches the GUI implementation for managing and simplifying debts.
"""

import sys
import os
import traceback
import importlib.util
import tkinter as tk
from src.ui.gui import DebtSimplifierGUI
# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Main function to run the Debt Simplification GUI application"""
    # Create the root window
    root = tk.Tk()
    # Initialize the application
    app = DebtSimplifierGUI(root)
    # Start the main event loop
    root.mainloop()
    sys.exit(1)

if __name__ == "__main__":
    main() 