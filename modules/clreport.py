import pandas as pd
import analyzer
import yfinance as yf
df = pd.read_csv('../data/datapoints.csv')
balance_sheet_datapoints = df['balance_sheet'].tolist()
income_statement_datapoints = df['income_statement'].dropna().tolist()
cash_flow_datapoints = df['cash_flow'].dropna().tolist()

ticker_symbol = 'MSFT'
ticker = yf.Ticker(ticker_symbol)
analysis = analyzer.FinancialAnalyzer("msft")

data = analysis.load_data(balance_sheet_datapoints, income_statement_datapoints, cash_flow_datapoints)


# Getting the DataFrame ready to display
data['Year'] = data['Year'].astype(int)

ratios = analysis.analyze()
transposed_data = data.set_index('Year').T
ratios['year'] = ratios['year'].astype(int)
transposed_ratios = ratios.set_index('year').T

# Dividing everything except for EPS
eps = transposed_data.loc['Basic EPS']
transposed_data = transposed_data / 1_000_000
transposed_data.loc['Basic EPS'] = eps


pd.options.display.float_format = "{:.3f}".format

print('Financial Performance Report\n')
print('This report is meant to be used for educational purposes only and is not meant as financial advice.')
print(ticker.info.get("longName", "Unknown Company"))
print(ticker.info.get('sector', 'Unknown Sector'))
print(ticker.info.get('industry', 'Unknown Industry'))
print(f'Website: {ticker.info.get('website', 'N/A')}\n')

print('Notable Datapoints over the last 4 years.')
print(transposed_data)
print('The numbers are displayed in millions of USD. (Except EPS)')
print(f'\nRatios for {ticker_symbol}')
print(transposed_ratios)

growth = analysis.growth_rates()
print(f'\nGrowth Rates for {ticker_symbol}')
growth_percentage = growth.map(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x) # Adds a percentage after each value and formats it so that it only displays 2 decimals
print(growth_percentage.to_string(index=False))

print('\n')
difference = analysis.difference()
print(f'{ticker_symbol} compared to sector averages.')
print(difference.to_string(index=False))
print('\n\n')
print('**This will be a page with the plots for the most important ratios and numbers. (They are to be created with matplotlib)**\n\n')

print('Appendix, more disclaimers, where the data is from and go see the full exported statements for further analysis.')