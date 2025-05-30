#!/usr/bin/env python3

"""
Main entry point for the Debt Simplification Algorithm application

This script launches the GUI implementation for managing and simplifying debts.
"""

import sys
import os
import traceback
import importlib.util

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = {
        "tkinter": "Please install Tkinter (sudo apt-get install python3-tk on Ubuntu/Debian)",
        "matplotlib": "Please install matplotlib (pip install matplotlib)",
        "networkx": "Please install networkx (pip install networkx)"
    }
    
    missing_modules = []
    
    for module_name, install_message in required_modules.items():
        if module_name == "tkinter":
            try:
                import tkinter
            except ImportError:
                missing_modules.append(f"- {module_name}: {install_message}")
        else:
            if importlib.util.find_spec(module_name) is None:
                missing_modules.append(f"- {module_name}: {install_message}")
    
    return missing_modules

def main():
    """Main function to run the Debt Simplification GUI application"""
    # Check dependencies first
    missing_modules = check_dependencies()
    if missing_modules:
        print("Error: Missing required dependencies:")
        for message in missing_modules:
            print(message)
        print("\nPlease install the missing dependencies and try again.")
        sys.exit(1)
    
    try:
        import tkinter as tk
        from src.ui.gui import DebtSimplifierApp
        
        # Create the root window
        root = tk.Tk()
        
        # Set window title and icon
        root.title("Debt Simplification Algorithm")
        
        # Try to set an icon if available
        try:
            if os.path.exists("icon.ico"):
                root.iconbitmap("icon.ico")
        except Exception:
            pass  # Ignore icon errors
        
        # Initialize the application
        app = DebtSimplifierApp(root)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("- Make sure you have all dependencies installed:")
        print("  pip install matplotlib networkx")
        print("- On Linux, ensure Tkinter is installed: sudo apt-get install python3-tk")
        print("- Check if the src/ui/gui.py file exists and contains the DebtSimplifierApp class")
        print("- For more information, check the error message above")
        sys.exit(1)

if __name__ == "__main__":
    main() 