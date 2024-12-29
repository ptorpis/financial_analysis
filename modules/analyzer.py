import yfinance as yf
import pandas as pd
import json
from typing import Final
import logging


logging.basicConfig(
    filename='../.logs/main.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


MAX_YEARS_REQUEST: Final[int] = 4
CURRENT_YEAR: Final[int] = 2024
RATIOS = ['current_ratio', 'quick_ratio', 'gross_profit', 'net_profit', 'roa', 'roe', 'asset_turnover', 'debt_to_equity', 'interest_cover']
METHODS = {
    1: "csv",
    2: "xlsx"
}

# Loading necessary datapoints from external file
df = pd.read_csv('../data/datapoints.csv')
balance_sheet_datapoints = df['balance_sheet'].tolist()
income_statement_datapoints = df['income_statement'].dropna().tolist()
cash_flow_datapoints = df['cash_flow'].dropna().tolist()


class FinancialAnalyzer:
    def __init__(self, ticker, years=4):
        self.ticker = yf.Ticker(ticker)
        self.ticker_text = ticker
        self.years = list(range(years))
        self.data = pd.DataFrame()
        self.sector = self.ticker.info.get('sector', 'n/a').lower()

    def load_data(self, bs_datapoints, is_datapoints, cf_datapoints):
        # getting the financial data using yfinance
        for year in self.years:
            company_info = {'Year': CURRENT_YEAR - year,}

            for datapoint in bs_datapoints:
                try:
                    company_info[datapoint] = (
                        self.ticker.balance_sheet.loc[datapoint].iloc[year]
                        if datapoint in self.ticker.balance_sheet.index else "N/A"
                    )
                except IndexError:
                    company_info[datapoint] = "N/A"
                    logging.info(f'{company_info[datapoint]} Datapoint Missing')
            
            try:
                for datapoint in is_datapoints:
                    company_info[datapoint] = (
                        self.ticker.income_stmt.loc[datapoint].iloc[year]
                        if datapoint in self.ticker.income_stmt.index else "N/A"
                    )
            except IndexError:
                company_info[datapoint] = "N/A"
                logging.info(f'{company_info[datapoint]} Datapoint Missing')          

            try:
                for datapoint in cf_datapoints:
                    company_info[datapoint] = (
                        self.ticker.cash_flow.loc[datapoint].iloc[year]
                        if datapoint in self.ticker.cashflow.index else "N/A"
                    )
            except IndexError:
                company_info[datapoint] = "N/A"
                logging.info(f'{company_info[datapoint]} Datapoint Missing')
            
            self.data = self.data.dropna()._append(company_info, ignore_index=True)

        return self.data
  

    def analyze(self):
        try:
            with open("../data/ratios.json", 'r') as file:
                formulas = json.load(file)
        except FileNotFoundError:
            logging.error(f"{file} File Not Found.")
            return
        except json.JSONDecodeError:
            logging.error("error decoding JSON.")
            return
        

        for column in self.data.columns:
            self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
        
        
        df_ratios = pd.DataFrame() # store the ratios in a DataFrame

        for year, row in self.data.iterrows():
            current_ratios = {'year': CURRENT_YEAR - year}
            print(f'Ratios for {CURRENT_YEAR - year}, for {self.ticker}')
            for ratio_name, formula in formulas.items(): # unpack the formulas 1 by 1 and calculate the ratios
                try:
                    formatted_formula = formula
                    for column in row.index:
                        formatted_formula = formatted_formula.replace(column, f"row['{column}']")
                    result = eval(formatted_formula)


                    current_ratios[ratio_name] = result


                    print(f"  {ratio_name.replace('_', ' ')}: {result:.2f}")
                
                # error handling
                except KeyError:
                    logging.error(f"{ratio_name.replace('_', ' ')}: Data missing for calculation.")
                except ZeroDivisionError:
                    logging.error(f"{ratio_name.replace('_', ' ')}: Division by zero error.")
                except Exception as e:
                    logging.error(f"{ratio_name.replace('_', ' ')}: Calculation error - {e}")

            df_ratios = df_ratios._append(current_ratios, ignore_index=True)
            
        # Declaring and returning the ratios table
        self.df_ratios = df_ratios

        #print(f"\nRatios Table:\n{df_ratios}\n")
        return df_ratios

    
    # Calculating the difference between the industry average and the calculated values
    def difference(self):
        df_averages = pd.read_csv("../data/averages.csv", header=0, index_col='ratios')
        
        self.df_difference = pd.DataFrame()

        # Looping through the ratios in the outer and the years in the inner loop, this is to have every ratio in it's own line
        for r in range(len(RATIOS)):
            
            difference = {'ratio': RATIOS[r]}

            # Creating 2 variables for the current data to make indexing easier
            current_avg = df_averages[self.sector].iloc[r]
            current_r = self.df_ratios[RATIOS[r]] # Entire column of values with the name of the ratio being the header
            
            for year in range(len(self.years)):
                
                try:
                    current_diff = (current_r[year] - current_avg)

                    difference[CURRENT_YEAR - year] = current_diff
                except KeyError:
                    logging.error('KeyError in "difference"')
            
            self.df_difference = self.df_difference._append(difference, ignore_index=True)

        #print(f"Difference Table: \n{self.df_difference}")
        return self.df_difference


    def growth_rates(self):
        
        self.df_growth_rates = pd.DataFrame()

        for r in range(len(RATIOS)):
            
            growth_rates = {'ratio': RATIOS[r]}

            current_r = self.df_ratios[RATIOS[r]] # Declaring this for easier indexing, see also 'current_r' in 'difference'
            
            for year in range(len(self.years) - 1):
                
                try:
                    growth_rate = (current_r.iloc[year] - current_r.iloc[year + 1]) / current_r.iloc[year + 1]
                    growth_rate *= 100
                    growth_rates[CURRENT_YEAR - year] = growth_rate
                except IndexError as e:
                    logging.error(f'{e} in "growth_rates"')
            
            self.df_growth_rates = self.df_growth_rates._append(growth_rates, ignore_index=True)
        
        #print(f"\nGrowth Rate Table:\n{self.df_growth_rates}")
        return self.df_growth_rates
    
    def export_csv(self):
        self.data.to_csv(f"../data_output/{self.ticker_text}_data_analysis.csv", index=False)
        self.df_ratios.to_csv(f"../data_output/{self.ticker_text}_ratios_analysis.csv", index=False)
        self.df_difference.to_csv(f"../data_output/{self.ticker_text}_difference_analysis.csv", index=False)

        if len(self.years) >= 2:
            self.df_growth_rates.to_csv(f"../data_output/{self.ticker_text}_growth_analysis.csv")



def get_int(promt: str, case: int) -> int:
    match case:
        case 1:
            while True:  
                try:
                    number = int(input(promt))
                    if number >= 0 and number <= MAX_YEARS_REQUEST:
                        return number
                    else:
                        print(f"Enter a valid integer (0-{MAX_YEARS_REQUEST})")
                except ValueError:
                    pass
        case 2:
            while True:
                try:
                    number = int(input(promt))
                    if number in METHODS:
                        return number
                    else:
                        print(f"Enter a Valid Method")
                except ValueError:
                    pass
        case _:
            raise ValueError("Invalid Case")


def get_yn(prompt: str) -> bool:
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'Y', 'yes']:
            return True
        elif response in ['n', 'N', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def get_float(promt) -> float:
    while True:
        try:
            number = float(input(promt))
            return number
        except ValueError:
            pass


def main():

    ticker = input("Ticker Request: ").upper().strip()
    years_request = get_int("Number of years to analyze: ", case=1)

    analyzer = FinancialAnalyzer(ticker, years_request)
    CompanyData: pd.DataFrame = analyzer.load_data(balance_sheet_datapoints, income_statement_datapoints, cash_flow_datapoints)
    Ratios: pd.DataFrame = analyzer.analyze()
    Difference: pd.DataFrame = analyzer.difference()

    # Only calculate growth rates is there are more than 1 years to analyze.
    if years_request >= 2:
        GrowthRates: pd.DataFrame = analyzer.growth_rates()
        pass

    export: bool = get_yn("Export files? ")

    if export:
        export_method: int = get_int("Export Method (1: .csv, 2: .xlsx): ", case=2)

        match export_method:
            case 1: # Exporting to .csv
                
                CompanyData.to_csv(f"../data_output/{ticker.upper()}_data_analysis.csv", index=False)
                Ratios.to_csv(f"../data_output/{ticker.upper()}_ratios_analysis.csv", index=False)
                Difference.to_csv(f"../data_output/{ticker.upper()}_difference_analysis.csv", index=False)

                if years_request >= 2:
                    GrowthRates.to_csv(f"../data_output/{ticker.upper()}_growth_analysis.csv")

            case 2: # Exporting to Excel File (.xlsx)
                with pd.ExcelWriter(f"../data_output/{ticker.upper()}_data_analysis.xlsx") as writer:
                    
                    CompanyData.to_excel(writer, sheet_name="Data", index=False)
                    Ratios.to_excel(writer, sheet_name="Ratios", index=False)
                    Difference.to_excel(writer, sheet_name="Difference", index=False)
                    
                    if years_request >= 2:
                        GrowthRates.to_excel(writer, sheet_name="Growth Rates", index=False)
            case _:
                raise ValueError("Invalid Export Case")
    else:       
        return
 
if __name__ == "__main__":
    main()