import yfinance as yf
import pandas as pd
import logging
import os

logging.basicConfig(
    filename='../.logs/main.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def ensure_directories_exist():
    # Define the directories that need to exist
    directories = [
        '../data_output/excel',
        '../data_output/csv'
    ]

    # Check and create each directory
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except FileExistsError:
            pass


PERIODS = 4 # The max number of periods we are accessing through yFinance (anything more will give dubious data or missing altogether)

class GetStatements:
    def __init__(self, ticker):
        self.ticker = yf.Ticker(ticker)
        self.balance_sheet = pd.DataFrame()
        self.income_statement = pd.DataFrame()
        self.cash_flow = pd.DataFrame()

    def get_statements(self):
        try:
            self.balance_sheet = self.ticker.balance_sheet
        except Exception:
            logging.error("Failed to load Balance Sheet.")
        
        try:    
            self.income_statement = self.ticker.income_stmt
        except Exception:
            logging.error("Failed to load Income Statement.")
        
        try:    
            self.cash_flow = self.ticker.cash_flow
        except Exception:
            logging.error("Failed to load Cash Flow Statement.")

        return {
            "balance_sheet": self.balance_sheet.iloc[:, :PERIODS],
            "income_statement": self.income_statement.iloc[:, :PERIODS],
            "cash_flow": self.cash_flow.iloc[:, :PERIODS],
        }


    def get_quarterly_statements(self):
        try:
            self.balance_sheet = self.ticker.quarterly_balance_sheet
        except Exception:
            logging.error("Failed to load Balance Sheet.")
        
        try:
            self.income_statement = self.ticker.quarterly_income_stmt
        except Exception:
            logging.error("Failed to load Income Statement.")
        
        try:    
            self.cash_flow = self.ticker.quarterly_cash_flow
        except Exception:
            logging.error("Failed to load Cash Flow Statement.")

        return {
            "qbalance_sheet": self.balance_sheet.iloc[:, :PERIODS],
            "qicome_statement": self.income_statement.iloc[:, :PERIODS],
            "qcash_flow": self.cash_flow.iloc[:, :PERIODS]
        }

def retrieve_and_export_statements(ticker_request: str, excel, csv):
    retriever = GetStatements(ticker_request)
    pd.set_option("display.max_rows", None)


    # Retrieve yearly statements
    yearlyStatements = retriever.get_statements()
    BalanceSheet = yearlyStatements["balance_sheet"]
    IncomeStatement = yearlyStatements["income_statement"]
    CashFlow = yearlyStatements["cash_flow"]

    # Retrieve quarterly statements
    quarterlyStatements = retriever.get_quarterly_statements()
    qBalanceSheet = quarterlyStatements["qbalance_sheet"]
    qIncomeStatement = quarterlyStatements["qicome_statement"]
    qCashFlow = quarterlyStatements["qcash_flow"]

    #print(f"{BalanceSheet}\n\n{IncomeStatement}\n\n{CashFlow}")
    
    ensure_directories_exist()
    # Export to Excel if requested
    
    if excel:
        try:
            os.makedirs(f'data_output/excel/{ticker_request.upper()}')
        except FileExistsError:
            pass

        with pd.ExcelWriter(f"data_output/excel/{ticker_request.upper()}/data_{ticker_request.upper()}.xlsx") as writer:
            BalanceSheet.to_excel(writer, sheet_name="Balance Sheet")
            IncomeStatement.to_excel(writer, sheet_name="Income Statement")
            CashFlow.to_excel(writer, sheet_name="Cash Flow")
                         
        with pd.ExcelWriter(f"data_output/excel/{ticker_request.upper()}/quarterly_data_{ticker_request.upper()}.xlsx") as writer:
            qBalanceSheet.to_excel(writer, sheet_name="Balance Sheet")
            qIncomeStatement.to_excel(writer, sheet_name="Income Statement")
            qCashFlow.to_excel(writer, sheet_name="Cash Flow")

    if csv:
        try:
            os.makedirs(f'data_output/csv/{ticker_request.upper()}')
        except FileExistsError:
            pass

        BalanceSheet.to_csv(f'data_output/csv/{ticker_request.upper()}/balance_sheet_{ticker_request.upper()}.csv')
        IncomeStatement.to_csv(f'data_output/csv/{ticker_request.upper()}/income_statement_{ticker_request.upper()}.csv')
        CashFlow.to_csv(f'data_output/csv/{ticker_request.upper()}/cash_flow_{ticker_request.upper()}.csv')

        qBalanceSheet.to_csv(f'data_output/csv/{ticker_request.upper()}/qbalance_sheet_{ticker_request.upper()}.csv')
        qIncomeStatement.to_csv(f'data_output/csv/{ticker_request.upper()}/qincome_statement_{ticker_request.upper()}.csv')
        qCashFlow.to_csv(f'data_output/csv/{ticker_request.upper()}/qcash_flow_{ticker_request.upper()}.csv')

def get_yn(prompt: str) -> bool:
    while True:
        response = input(f"{prompt} (y/n): ").strip()
        if response in ['y', 'Y']:
            return True
        elif response in ['n', 'N']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# Run this only if the script is executed directly
def main():
    ticker_request = input("Ticker Request: ").upper().strip()
    excel = get_yn("Export files? (xls)")
    csv = get_yn("Export files? (csv)")

    retrieve_and_export_statements(ticker_request, excel, csv)

if __name__ == "__main__":
    main()
