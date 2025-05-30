# Debt Simplification Algorithm

This project implements a debt simplification algorithm, which minimizes the number of transactions needed to settle debts in a group.

## Table of Contents

- [Algorithm Explanation](#algorithm-explanation)
- [Project Structure](#project-structure)
- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Example Data](#example-data)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Requirements](#requirements)
- [License](#license)

## Algorithm Explanation

The debt simplification algorithm follows these rules:

1. Everyone owes the same net amount at the end.
2. No one owes a person that they didn't owe before.
3. No one owes more money in total than they did before the simplification.

The algorithm works by calculating the net balance for each person and then creating a minimal set of transactions to settle all debts.

### Step-by-Step Algorithm

1. **Calculate Net Balances**

   - For each transaction where person A owes person B amount X:
     - Decrease A's balance by X
     - Increase B's balance by X
   - After processing all transactions, each person's net balance represents how much they owe (if negative) or are owed (if positive)

2. **Separate Into Givers and Receivers**

   - Givers (Debtors): People with negative balances who need to pay money
   - Receivers (Creditors): People with positive balances who need to receive money

3. **Sort Both Lists**

   - Sort givers by the amount they owe (largest first)
   - Sort receivers by the amount they are owed (largest first)

4. **Create Simplified Transactions**
   - Starting with the largest giver and receiver:
     1. Find the minimum of what the giver owes and what the receiver is owed
     2. Create a transaction of this amount from the giver to the receiver
     3. Decrease the giver's debt and the receiver's credit by this amount
     4. If a giver's debt becomes zero, move to the next giver
     5. If a receiver's credit becomes zero, move to the next receiver
     6. Repeat until all debts are settled

### Algorithm Complexity

- Time Complexity: O(n log n), where n is the number of people (due to sorting)
- Space Complexity: O(n), to store the balances and the simplified transactions

## Project Structure

The project is organized as follows:

```
DSA-2024.2/
├── .git/                  # Git version control files
├── main.py                # Main application entry point
├── idea.md                # Document for brainstorming and ideas (Vietnamese - detailed project requirements/aspirations)
├── README.md              # This README file
├── src/                   # Source code
│   ├── __init__.py        # Package initialization
│   ├── algorithms/        # Algorithm implementations
│   │   ├── __init__.py    # Exposes available simplifier classes
│   │   ├── minimize_transactions/  # Algorithms focused on minimizing transaction count
│   │   │   ├── __init__.py
│   │   │   ├── base_simplifier.py
│   │   │   ├── cycle_detector_minimize_tx.py # Implements DebtCycleSimplifierMinimizeTx
│   │   │   ├── min_cost_max_flow_minimize_tx.py # Implements MinCostMaxFlowSimplifierMinimizeTx
│   │   │   ├── time_aware_greedy_minimize_tx.py # Implements TimeAwareGreedySimplifierMinimizeTx
│   │   │   └── timeline_dp.py # Implements TimelineDPSimplifier
│   │   └── prioritize_urgency_and_cost/ # Algorithms focused on time and cost factors
│   │       ├── __init__.py
│   │       └── time_aware_greedy.py # Implements TimeAwareGreedySimplifier
│   ├── core_types/        # Core type definitions (Person, Date, Transaction)
│   │   ├── __init__.py
│   │   ├── date.py
│   │   ├── person.py
│   │   └── transaction.py
│   ├── data_structures/   # Custom data structures
│   │   ├── __init__.py
│   │   ├── array.py
│   │   ├── binary_search_tree.py
│   │   ├── graph.py
│   │   ├── hash_table.py
│   │   ├── linked_list.py
│   │   ├── priority_queue.py # Includes Heap functionality
│   │   └── tuple.py          # Custom Tuple implementation
│   ├── database/          # Database related modules
│   │   ├── check_db.py
│   │   └── debt_simplifier.db # SQLite database
│   ├── samples/           # Sample data for testing and demonstration
│   │   ├── __init__.py
│   │   ├── sample_transactions.csv
│   │   ├── sample_transactions_1.py
│   │   ├── sample_transactions_2.py
│   │   ├── sample_transactions_edge_cases.py
│   │   └── sample_transactions_minimize_test.py
│   ├── ui/                # User interface components
│   │   ├── __init__.py
│   │   └── gui.py         # GUI implementation
│   └── utils/             # Utility functions and classes
│       ├── __init__.py
│       ├── math_helpers.py
│       └── sorting.py     # Sorting algorithms (MergeSort, QuickSort, HeapSort)
└── tests/                 # Test files
    ├── __init__.py        # Package initialization
    ├── data_structures/   # Tests for data_structures
    │   ├── test_array.py
    │   ├── test_hash_table.py
    │   └── test_priority_queue.py
    ├── minimize_transactions/ # Tests for transaction minimization algorithms
    │   ├── __init__.py
    │   ├── test_debt_cycle_minimize_tx_count.py
    │   ├── test_mcmf_minimize_count.py
    │   ├── test_time_aware_greedy_minimize_tx_count.py
    │   ├── test_timeline_dp.py
    │   └── test_utils.py
    └── prioritize_urgency_and_cost/ # Tests for urgency and cost prioritization
        └── test_time_aware_greedy.py
```

## Features

### Debt Simplification Algorithms

The project implements several advanced algorithms for debt simplification, available via `src/algorithms/__init__.py`. These are broadly categorized into:

1.  **Transaction Count Minimization** (primarily from `src/algorithms/minimize_transactions/`):

    - **`DebtCycleSimplifierMinimizeTx`** (from `cycle_detector_minimize_tx.py`):
      - Focus: Detects and resolves debt cycles (e.g., A owes B, B owes C, C owes A) to reduce transaction counts.
      - Underlying Method: Likely uses graph traversal algorithms to find and simplify cycles.
    - **`MinCostMaxFlowSimplifierMinimizeTx`** (from `min_cost_max_flow_minimize_tx.py`):
      - Focus: Models the debt network as a flow problem to find the minimum cost way to settle debts, which often minimizes transactions.
      - Underlying Method: Implements min-cost max-flow algorithms.
    - **`TimeAwareGreedySimplifierMinimizeTx`** (from `time_aware_greedy_minimize_tx.py`):
      - Focus: A greedy approach that aims to minimize transactions while potentially considering time-based factors like due dates.
    - **`TimelineDPSimplifier`** (from `timeline_dp.py`):
      - Focus: Uses dynamic programming across a timeline to make settlement decisions, potentially handling complex time-dependent constraints. (Note: May be experimental as it was commented out in `src/algorithms/__init__.py`'s `__all__` list).

2.  **Urgency and Cost Prioritization** (from `src/algorithms/prioritize_urgency_and_cost/`):
    - **`TimeAwareGreedySimplifier`** (from `time_aware_greedy.py`):
      - Focus: A greedy algorithm that prioritizes settling debts based on urgency (e.g., upcoming due dates) and cost (e.g., interest rates, penalty fees).

_(Note: For detailed time/space complexities of each algorithm, refer to the source code documentation within each file, as these can be intricate.)_

### Custom Data Structures

(Located in `src/data_structures/`)

Implements core data structures from scratch:

- **Array** (`array.py`): Dynamic array.
- **LinkedList** (`linked_list.py`): Basic linked list.
- **HashTable** (`hash_table.py`): Hash table with chaining.
- **PriorityQueue** (`priority_queue.py`): Implemented using a heap, suitable for MinHeap/MaxHeap behavior based on comparator.
- **Graph** (`graph.py`): Generic graph structure (likely used for transaction representation).
- **BinarySearchTree** (`binary_search_tree.py`): For ordered data storage/retrieval if needed.
- **Tuple** (`tuple.py`): Custom tuple implementation.

### Sorting Algorithms

(Located in `src/utils/sorting.py`)

- MergeSort
- QuickSort
- HeapSort

### Core Types

(Located in `src/core_types/`)

- **Person** (`person.py`): Represents individuals in transactions.
- **Date** (`date.py`): Custom date implementation for handling borrow/due dates.
- **Transaction** (`transaction.py`): Represents a debt with attributes like amount, dates, potentially interest/penalties (as per `idea.md`).

### GUI Interface

Provides a user-friendly interface for:

- Adding and removing transactions
- Viewing net balances
- Simplifying debts using different approaches
- Visualizing the debt graph before and after simplification
- Loading example data for demonstration

## Installation

### Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.6 or higher
- Tkinter (for GUI)
- Matplotlib (for visualization)
- NetworkX (for graph visualization)

### Installing Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/dsa-final-project.git
cd dsa-final-project

# Install Python dependencies
pip install matplotlib networkx
```

Note: The GUI implementation uses Tkinter, which is included in the Python standard library, but on some Linux distributions it needs to be installed separately:

```bash
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On Fedora/RHEL:
sudo dnf install python3-tkinter

# On macOS with Homebrew:
brew install python-tk
```

## Running the Application

### Option 1: Using the main.py script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x main.py

# Run the application
./main.py
```

Or:

```bash
python main.py
```

## Usage Guide

### Using the Application

Once the application starts, you can:

1. **Add Transactions Tab**

   - Enter debtor, creditor, and amount information
   - Click "Add Transaction" to add a new transaction
   - Use "Delete Selected" to remove transactions
   - Click "Load Example Data" to load a demonstration dataset
   - Use "Import Sample Transactions" to load from sample files

2. **View Transactions Tab**

   - See the net balances for each person
   - View who owes money and who is owed
   - Click "Refresh Balances" to update the view

3. **Simplified Debts Tab**

   - Select an algorithm approach from the dropdown
   - Click "Simplify Debts" to run the selected algorithm
   - View the resulting simplified transactions
   - Click "Visualize" to see a graphical representation

4. **Visualization Tab**
   - Click "Visualize Debts" to generate a graph visualization
   - Compare original transactions with simplified transactions
   - Use the toolbar to zoom, pan, and save the visualization

## Example Data

The application includes a sample dataset that demonstrates debt simplification. You can load this example data by clicking the "Load Example Data" button in the Add Transactions tab.

Example transactions (9 total):

- Gabe owes $30 to Bob
- Gabe owes $10 to David
- Fred owes $10 to Bob
- Fred owes $30 to Charlie
- Fred owes $10 to David
- Fred owes $10 to Ema
- Bob owes $40 to Charlie
- Charlie owes $20 to David
- David owes $50 to Ema

Simplified transactions (reduced to 3 total):

- Fred owes $60 to Ema
- Gabe owes $40 to Charlie
- David owes $10 to Charlie

## Running Tests

The project contains a suite of tests organized by module. To run tests, you would typically use a test runner like `pytest` or Python's `unittest` module from the command line, targeting specific test files or directories.

Example (if using `pytest`, which is a common choice but not explicitly stated as a dependency):

```bash
# To run all tests in the tests/ directory
pytest tests/

# To run tests for a specific module, e.g., data_structures
pytest tests/data_structures/

# To run a specific test file
pytest tests/data_structures/test_array.py
```

Example (if using Python's `unittest`):

```bash
# To run tests in a specific file
python -m unittest tests/data_structures/test_array.py

# To discover and run tests in a directory (less straightforward without a helper script)
# python -m unittest discover -s tests/
```

_(Note: The exact commands for running tests depend on the project's testing setup and conventions. The original README mentioned specific scripts `test_algorithm.py` and `verify_balances.py` which were not found. The structure suggests module-wise testing as shown above.)_

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed correctly
2. Check the console output for error messages
3. Verify that you're running Python 3.6 or higher
4. Make sure the application files are in their original structure
5. If visualizations don't appear, check that matplotlib and networkx are installed

## Requirements

- Python 3.6+
- Tkinter (for GUI)
- Matplotlib (for visualization)
- NetworkX (for graph visualization)

## License

This project is licensed under the MIT License.
