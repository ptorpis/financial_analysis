# Financial Analysis

## Overview

This program is meant to help the financial analysis of a company's stock, mainly by allowing the user to export financial statements going back to the last 4 periods (4 years and/or 4 quarters).
Main feature is the statement export, treat the report generation as an experimental feature.
This tool is not meant to replace in depth analysis of financial statements.

## Features

 - Export financial statements (balance sheet, income statement, and cash flow statements). The program is written in python and is utilizing the yFinance library to access data.
 - Generate a PDF rerport containing some general numbers in a table, key financial ratios, growth rates and the company's performance compared to sector averages, some visualization of the data. 
 
 The sector averages were collected by me, but I cannot guarantee the accuracy of the data.

## Prerequisites

To use this tool, you need to have Python installed on you computer, for this I recommend the latest verion, but 3.11+ will work for sure.

Required libraries: Install the dependencies listed in 'requirements.txt' by running the following command.
    pip install -r requirements.txt

## Usage

1. Clone the repository to your machine:
    git clone *placeholder*
2. Navigate to the program's directory.
3. Run the main script.

### Running the main script (example, Windows based):

    python main.py msft -s -r excel csv

There are 2 modes - statements and report mode. These can be passed as arguments when running the program in the terminal.
To generate a report, use the 
    -r 
and if you want to export financial statements, use
    -s
after the flag -s, you need to specify which format you want the statements to be exported in. You can choose from 'excel' and 'csv' (both can be passed at the same time).

