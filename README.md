# Project Setup Guide

Follow the steps below to set up and run the project in a clean, isolated Python environment.

## 1. Install Python

Ensure Python is installed on your machine, with a version **3.9 or higher**. You can verify the installation by running:

```bash
python --version
```

If Python is not installed, download and install it from the [official Python website](https://www.python.org/downloads/). Make sure to check the option to **Add Python to PATH** during installation.

## 2. Create a Virtual Environment

Navigate to your project directory and create a virtual environment to isolate dependencies:

```bash
python -m venv venv
```

This will create a folder named `venv` containing the virtual environment.

## 3. Activate the Virtual Environment

Activate the virtual environment using the appropriate command for your operating system:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

After activation, you should see the environment name `(venv)` in your terminal prompt, indicating the virtual environment is active.

## 4. Install Required Packages

With the virtual environment activated, install the required Python packages specified in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This ensures that all the necessary dependencies are available for the project.

## 5. Set Up the Local Database

To set up the local database, follow these steps:

1. **Create the Database**: 
   - Name the database `solution_app`.
   
2. **Import the Data**: 
   - Use the provided `business_data.sql` file to populate the database with initial data.

## 6. Run the Scraper

Once the environment is set up and the database is configured, you can run the scraper script:

```bash
python script.py
```

This will execute the main scraper functionality of the project.

---

### Additional Commands

- **Deactivate Virtual Environment**:
  When you're done working, deactivate the virtual environment by running:
  ```bash
  deactivate
  ```

- **Reactivate Virtual Environment**:
  When returning to the project, reactivate the virtual environment:
  ```bash
  venv\Scripts\activate  # Windows
  source venv/bin/activate  # macOS/Linux
  ```

---

This guide should help you get up and running quickly.