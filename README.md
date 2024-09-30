# My Codebase

Welcome to **My Codebase**, a comprehensive repository containing Jupyter Notebooks, Python scripts, and Bash scripts for data analysis, simulation, and various computational tasks. This repository is organized to facilitate easy navigation, modularity, and reusability of code across different projects.

## Table of Contents

- [Features](#features)
- [Directory Structure](#directory-structure)

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up a Virtual Environment](#set-up-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
  - [Install `muonpipe` Module in Editable Mode](#install-muonpipe-module-in-editable-mode)
- [Usage](#usage)
  - [Running Jupyter Notebooks](#running-jupyter-notebooks)
  - [Executing Python Scripts](#executing-python-scripts)
  - [Running Bash Scripts](#running-bash-scripts)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Jupyter Notebooks**: Interactive notebooks for data analysis, visualization, and exploration.
- **Python Scripts**: Modular Python scripts for various computational tasks.
- **Bash Scripts**: Automation scripts for setup, data processing, and deployment.
- **Custom Modules**: Reusable Python modules (`muonpipe`) to streamline code across notebooks and scripts.

## Directory Structure

- **python/jupyter_notebooks/**: Contains all Jupyter Notebook files for data analysis and visualization.
- **python/python_scripts/**: Holds standalone Python scripts for various tasks.
- **python/python_modules/**: Custom Python modules, including `muonpipe`, essential for other code in the repository.
- **bash_scripts/**: Bash scripts for automating setup and deployment processes.
- **data/**: Directory for storing raw and processed data.
- **C++/**: Directory for C++ code
- **requirements.txt**: Lists all Python dependencies required for the project.
- **README.md**: This documentation file.

## Installation

### Prerequisites

- **Python 3.10 or higher**
- **Git**
- **pip** (Python package installer)
- **Virtual Environment Tool** (`venv` or `conda`)

### Clone the Repository

```bash
git clone https://github.com/jstvdk/my_codebase.git
cd my_codebase
```

### Set Up a Virtual Environment and installing the dependencies

From the project root directory:

```bash
conda create -n my_codebase_env python=3.10
conda activate my_codebase_env
pip install --upgrade pip
pip install -r requirements.txt
```
### Install `muonpipe` Module in Editable Mode

The `muonpipe` module is essential for the functionality of almost all python related code in this repository. Installing it in editable mode ensures that any changes made to the module are immediately available without needing to reinstall.

**To install it, navigate to the `python_modules` Directory:**

   ```bash
   cd python/python_modules/muonpipe
   pip install -e .
   ```

   **Note:** Ensure that you’re using the same Python environment (e.g., virtual environment) for both installing the package and running Jupyter Notebooks