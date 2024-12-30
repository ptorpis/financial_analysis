import yfinance as yf
import pandas as pd
import json

datapoints = pd.read_csv('../data/all_datapoints.csv', header=0)
RATIOS = datapoints['ratios'].dropna().tolist()
balance_sheet_datapoints = datapoints['balance_sheet'].tolist()
income_statement_datapoints = datapoints['income_statement'].dropna().tolist()
cash_flow_datapoints = datapoints['cash_flow'].dropna().tolist()

list_of_datapoints = balance_sheet_datapoints + income_statement_datapoints + cash_flow_datapoints

CURRENT_YEAR = 2024

class FinancialAnalyzer():
    def __init__(self, ticker_symbol, years=4):
        self.ticker = yf.Ticker(ticker_symbol)
        self.ticker_symbol = ticker_symbol
        self.years = list(range(years))
        self.sector = self.ticker.info.get('sector', 'n/a').lower()

    def get_data(self):
        self.data = pd.DataFrame()
        self.data['Year'] = list_of_datapoints
        for year in range(4):
            company_data = []
            for i in range(len(balance_sheet_datapoints)):
                try:
                    company_data.append(self.ticker.balance_sheet.loc[balance_sheet_datapoints[i]].iloc[year])
                except:
                    company_data.append('NaN')
            for i in range(len(income_statement_datapoints)):
                try:
                    company_data.append(self.ticker.income_stmt.loc[income_statement_datapoints[i]].iloc[year])
                except:
                    company_data.append('NaN')
            for i in range(len(cash_flow_datapoints)):
                try:
                    company_data.append(self.ticker.cash_flow.loc[cash_flow_datapoints[i]].iloc[year])
                except:
                    company_data.append('NaN')
            self.data[CURRENT_YEAR - year] = company_data
        print(self.data)
    
    def get_ratios(self):
        try:
            with open("../data/_ratios.json", 'r') as file:
                formulas = json.load(file)
        except FileNotFoundError:
            print("File Not Found.")
            return
        except json.JSONDecodeError:
            print("JSON Decode Error.")
            return
        
        
        for column in self.data.columns:
            self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
        
        transposed = self.data.T
        
        df_ratios = pd.DataFrame() # store the ratios in a DataFrame

        for i, row in transposed.iterrows():
            print(row)
            current_ratios = {'Year': CURRENT_YEAR - int(i)}
            print(f'Ratios for {CURRENT_YEAR - int(i)}, for {self.ticker}')
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
                    print("Missing Data.")
                except ZeroDivisionError:
                    print("Division By 0 Error.")
                except Exception as e:
                    print("Calculation Error.")

            df_ratios = df_ratios._append(current_ratios, ignore_index=True)
            
        # Declaring and returning the ratios table
        self.df_ratios = df_ratios
        print(self.df_ratios)
            

analyzer = FinancialAnalyzer('MSFT')
analyzer.get_data()
analyzer.get_ratios()