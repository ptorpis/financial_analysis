import pandas as pd
import json
import analyzer
import getstatements
import matplotlib.pyplot as plt
import logging
import yfinance as yf

logging.basicConfig(
    filename='../.logs/main.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


ERROR: int = -1


"""
What the report will look like:
    A pdf document for ease of use and portability
    

    Introduction
    Company name, ticker, founded, industry, current share price
    
    Financial Statements
    Ratios, Growth rates, differences visualized

    Strong point analysis
    list all of the strong points of the company's financial position

    Risk analysis
    risk rating
"""
df_datapoints = pd.read_csv('../data/datapoints.csv')

with open('../data/ratios.json') as file:
    formulas = json.load(file)


def generate_data(ticker='MSFT'):

    """
    Generates the necessary files for the report, using the modules that I have build
    """
    statements = getstatements
    statements.retrieve_and_export_statements(ticker, export=False, report=True)


    analysis = analyzer.FinancialAnalyzer(ticker)
    analysis.load_data(df_datapoints['balance_sheet'].tolist(), df_datapoints['income_statement'].dropna().tolist(), df_datapoints['cash_flow'].dropna().tolist())
    analysis.analyze()
    analysis.difference()
    analysis.growth_rates()
    analysis.export_csv()

def generate_plots(ticker='MSFT'):
    """
    Create the necessary figures inside this function
    - print the financial statements in png or similar format
    - growth rate visualization
    - Difference table, highlight the major deviations with a different font color or something
    """

    # Generate a plot for all the growth rates
    df_growth = pd.read_csv(f'../data_output/report/analysis/{ticker}_growth.csv', header=0)
    df_growth.set_index('ratio', inplace=True)

    ax = df_growth.iloc[:, 1:].T.plot(kind='bar', figsize=(12, 6), width=0.8)

    # Add title and labels
    plt.title('Growth Rates Across Years', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Values', fontsize=12)

    # Add legend
    plt.legend(title='Ratio', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save plot
    plt.tight_layout()  # Adjust layout to fit everything
    plt.savefig(f'../data_output/report/{ticker}_growth_rates_plot.png', format='png')


def strong_points(ticker='MSFT'):
    """
    Create triggers for the positive aspects of the company's financial posititon

    - Good profitability metrics: high or increasing net profit margin, operating margin, gross profit margin
    - Consistent revenue growth
    - High ROE, ROA
    - Low debt to equity ratio
    - healthy liquidity position: current and quick ratio above industry thresholds
    - strong Free Cash Flow: positive and/or growing
    - EPS growth
    - Strong dividend performance: increasing dividend payout without making it unsustainable
    - Asset efficiency: high/improving asset turnover ratio
    - Low CapEx compared to Revenue
    - Consistent, growing operating cash flow
    
    Evaluate strong points and highlight them in the report

    Additional strong points that I am not going to be evaluating, but will promt the user to look into
    - Strong market share or competitive position
    - Good credit rating
    - Strong brand and intellectual property
    - Positive market sentiment

    I am not going to score this part, only the risks, but I will mention how a high number of strong points will lead to a higher probability of a good investment

    Note: if a strong point does not get triggered, it does not mean that the company is struggling on that front, you should still do your own research    
    """


class RiskAnalysis():
    """
    Create warnings for potential issues in the data
    - Declining profitability
    - High Debt levels
    - Negative or decreasing Free Cash Flow
    - Low or Negative ROE
    - Rising Operational expenses: operating expenses are rising disproportionally to revenue
    - Liquidity Problems: current ratio falls below 1 or the quick ratio is significantly below 0.5
    - Earnings volatility: standard deviation of earnings over a period is high
    - Negative Growth in key metrics: revenue, gross profit, operating profit growth has been negative over the last couple of periods
    - Excessive Dividend Payout Ratio
    - High CapEx with low Returns: CapEx is high, while ROA is low
    - Industry risks
    
    Evaluate risks and create a point scoring system where the company starts out with 100 points and each risk factor will decrease this score by some amount
    different risk factors have different weights (can also do a multiplier if there is a lot at once in a certain area)
    A - F

    Additional risks that I am not going to be evaluating, but will promt the user to look further into this
    - Deteriorating credit rating
    - Stock price decline or high volatility
    - Loss of major clients or revenue concentration
    - Legal, regulatory risks
    - High employee turnover
    - Excessive exposure to cyclical or volatile industries
    - Impairment of assets, or major write offs
    - Management and ownership changes

    For these, I will provide a guide for the user as to what to look out for and will be included in the report
    Note: same as with the strong points, just because a point was triggered or not, there is no guaratee that it is actually the case
    This report is only meant to guide the usr into the right direction.
    """
    def __init__(self, ticker='MSFT'):
        self.df_growth = pd.read_csv(f'../data_output/report/analysis/{ticker}_growth.csv', header=0)
        self.df_growth.set_index('ratio', inplace=True)

        self.df_data = pd.read_csv(f'../data_output/report/analysis/{ticker}_data.csv', header=0)

        self.df_averages = pd.read_csv('../data/averages.csv')
        self.sector = yf.Ticker(ticker).info.get('sector', 'n/a').lower()

    def profitability_warning(self):
        """
        Looks at revenue and profit margins over time and if it has been declining over a certain threshold, returns a score and a rating. The score is of type float and the rating is of type int 
    
        """
        score: float = 0
        severity: int = 0




        try:
            cumulative_margin_growth: float = self.df_growth.loc['net_profit'].iloc[1:].sum()
            cumulative_revenue_growth: float = (self.df_data['Total Revenue'].iloc[0] - self.df_data['Total Revenue'].iloc[-1]) / self.df_data['Total Revenue'].iloc[-1]
        except ZeroDivisionError:
            logging.error("Missing data, zero-division error.")
            return ERROR

if __name__ == "__main__":
    generate_data()
    #generate_plots()
    #risk = RiskAnalysis()
    #risk.profitability_warning()
    



    