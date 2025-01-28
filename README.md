# Financial Analysis

## Overview

This program is meant to help the financial analysis of a company's stock, mainly by allowing the user to export financial statements going back to the last 4 periods (4 years and/or 4 quarters).
Main feature is the statement export, treat the report generation as an experimental feature.

## Features

 - Export financial statements (balance sheet, income statement, and cash flow statements). The program is written in python and is utilizing the yFinance library to access data.
 - Generate a PDF rerport containing some general numbers in a table, key financial ratios, growth rates and the company's performance compared to sector averages, some visualization of the data. 
 
 The sector averages were collected by me, but I cannot guarantee the accuracy of the data.

## Prerequisites

To use this tool, you need to have Python installed on you computer, for this I recommend the latest verion, but 3.11+ will work for sure.

If you don't already have python installed, follow this link:

https://www.python.org/downloads/

## Usage

1. Clone the repository to your machine (in some terminal):

    git clone https://github.com/ptorpis/financial_analysis

2. Navigate to the program's directory.

    cd path/to/download

cd (change directory) to wherever you have saved this project.

3. Required libraries: Install the dependencies listed in 'requirements.txt' by running the following command.

    pip install -r requirements.txt

4. Run the main script.

### Running the main script (example, Windows based):

    python main.py msft -r -s excel csv

Whichever company you want to run the program with, pass its ticker as the first argument. Upper and lower case works the same.

There are 2 modes - statements and report mode. These can be passed as arguments when running the program in the terminal.
To generate a report, use the -r and if you want to export financial statements, use -s. After the flag -s, you need to specify which format you want the statements to be exported in. You can choose from 'excel' and 'csv' (both can be passed at the same time).

    python main.py -h

or

    python main.py --help

If you want to see the arguments and the usage.

## Errors

It is possible that the yFinance API is not responding, or the program cannot retireve the data for some other reason, empty tables will be returned.

If any other issues arise, please contact me.

## Output

Files are created in the data_output/ folder, in this folder there are 2 subfolders: data_output/csv/ and ../excel/ (they might not be there before the first usage of the program, but they will be automatically created).
The statements for a company will be placed in their individual folders (these will be automatically created also).

data_{COMPANY_TICKER}.xlsx contains the yearly statements and quarterly_data_{COMPANY_TICKER}.xlsx contains the last 4 quarterly statements.

.csv files are similar, but the individiual statements will be placed in different files. Example: balance_sheet_{COMPANY_TICKER}.csv

Reports are exported into report/. The files will be named based on the company's ticker and today's date.
financial_report_{COMPANY_TICKER}_{DD-MM_YY}.pdf.

## Disclaimer

This tool is for informational and educational purposes only. It is not intended to replace professional financial advice. The accuracy of these results cannot be guaranteed. The creator(s) are not liable for any decisions made based on the reports or exported data.

## Contribution

1. Fork the repository.
2. Create a new branch for your feature or bug-fix:

    git checkout -b feature-name

3. Commit your changes:

    git commit -m 'Added feature-name'

4. Push to your fork:

    git push origin feature-name

5. Open a pull request.


## Contact

For questions or support, please contact ptorpis@gmail.com
