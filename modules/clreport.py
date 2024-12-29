import pandas as pd
import yfinance as yf
import analyzer


datapoints = pd.read_csv('../data/datapoints.csv')

def generate_report(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        company_info = ticker.info
        company_name = company_info.get("longName", "Unknown Company")
        sector = company_info.get("sector", "Unknown Sector")
        industry = company_info.get("industry", "Unknown Industry")
        website = company_info.get("website", "N/A")
    except Exception as e:
        print("Error fetching company information:", e)
        return
    print("FINANCIAL REPORT")
    print(ticker)
    print(sector)
    print(industry)
    print(website)

    analysis = analyzer.FinancialAnalyzer(ticker_symbol)
    data = analysis.load_data(
        datapoints['balance_sheet'].tolist(),
        datapoints['income_statement'].dropna().tolist(),
        datapoints['cash_flow'].dropna().tolist()
    )

    data.set_index('Year', inplace=True)
    print(data.T)


    ratios = analysis.analyze()
    print(ratios)

generate_report("MSFT")