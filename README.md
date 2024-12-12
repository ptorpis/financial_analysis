# financial_analysis

### Output Files
The `/data_output` directory is used to store generated output files. This folder is not tracked in the repository except for a placeholder file `.gitkeep`.

## Modules
### analyzer.py


### getstatements.py

Overview

The getstatements.py module is designed to retrieve financial statements for a specified company from Yahoo Finance using the yfinance library. It provides functionality to extract annual and quarterly financial statements, including the balance sheet, income statement, and cash flow statement. Users can choose to export the retrieved data into Excel or CSV formats for further analysis.

Features
    Fetch Financial Data:
        Retrieves annual and quarterly financial statements from Yahoo Finance.
    
    Includes:
        Balance Sheets
        Income Statements
        Cash Flow Statements
    
    Customizable Data Export:
        Save statements in Excel (.xlsx) or CSV (.csv) formats.
        Separate files for annual and quarterly data.

    Error Logging:
        Logs issues encountered during data retrieval to ../.logs/main.log.
    
    Requirements
        Python 3.7+
        Libraries:
            yfinance
            pandas
            logging

    Install the required libraries using:
        pip install yfinance pandas

Usage:
    To use the script, run it directly from the terminal (make sure your current directory is "/modules").
        python getstatements.py

Input: 
    Ticker Request: Enter the stock ticker of the company (e.g., AAPL for Apple Inc.).
    This input is not case sensitive (it will accept aapl for Apple Inc., or any combination of lower and uppercase letters, as long as they spell the company's ticker)
    
    Export Files: Choose whether to export data to Excel files (y/n).

Outputs:
    The script retrieves financial data and displays the following statements in the terminal:

    Annual:
        Balance Sheet
        Income Statement
        Cash Flow Statement
    
    Quarterly:
        Balance Sheet
        Income Statement
        Cash Flow Statement
    
    If export options are selected, the data is saved in the following directories:
    
    Excel Output:
        Annual data: ../data_output/{TICKER}_data.xlsx
        Quarterly data: ../data_output/{TICKER}_quarterly_data.xlsx
    
    CSV Reports:
        Annual data: ../report/ (e.g., balance_sheetAAPL.csv, income_statementAAPL.csv)
        Quarterly data: ../report/ (e.g., qbalance_sheetAAPL.csv, qincome_statementAAPL.csv)
    
    Exported Files
        AAPL_data.xlsx (Excel file containing annual data)
        AAPL_quarterly_data.xlsx (Excel file containing quarterly data)

Functions:
    GetStatements
        A class to retrieve and store financial statements for a given ticker.

    Attributes:

        ticker: The Yahoo Finance ticker object for the company.
        balance_sheet, income_statement, cash_flow: Pandas DataFrames for the respective statements.
    
    Methods:

        get_statements: Retrieves annual statements.
        get_quarterly_statements: Retrieves quarterly statements.
        retrieve_and_export_statements(ticker_request: str, export: bool, report: bool)
        
        Fetches financial data for the specified ticker, displays it in the terminal, and optionally exports it.

    Parameters:
        ticker_request: The stock ticker to fetch data for (e.g., AAPL).
        export: If True, saves data to Excel files.
        report: If True, saves data to CSV files.
        get_yn(prompt: str) -> bool
        Prompts the user for a yes or no input.

    main()
        The entry point for the script. Handles user input and calls retrieve_and_export_statements.

Logging
    Logs errors (e.g., failed data retrieval) to ../.logs/main.log.
    
    Most of it can be ignored.

    Example log message:
        2024-12-12 10:45:23 - ERROR - Failed to load Balance Sheet.

Limitations
    Data Periods: Only retrieves up to 4 periods of data due to potential issues with larger datasets.
    
    Dependencies: Relies on the accuracy and availability of data from Yahoo Finance.
    
    Error Handling: Logs failures but does not terminate execution on errors.

