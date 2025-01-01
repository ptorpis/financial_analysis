from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageBreak
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import yfinance as yf
import analyzer
import matplotlib.pyplot as plt
import numpy as np
import argparse
import getstatements
from datetime import datetime
import os

# Function to create a table from a dataframe
def create_table_from_dataframe(df):
    """Converts a pandas dataframe into a table for ReportLab with headers and index included."""
    # Combine the index as the first column
    df_with_index = df.copy()
    df_with_index.insert(0, 'Index', df_with_index.index)

    # Convert DataFrame to list of lists
    data = [df_with_index.columns.tolist()] + df_with_index.values.tolist()

    # Create the table
    table = Table(data)

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
        ('ALIGN', (0, 1), (0, -1), 'LEFT'), # Index Column alligned to the left
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Body background
        ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid lines
    ]))

    return table


def get_info(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        company_name = ticker.info.get("longName", "Unknown Company Name")
        sector = ticker.info.get("sector", "Unknown Sector")
        industry = ticker.info.get("industry", "Unknown Industry")
        website = ticker.info.get("website", "N/A")

        return {
            "company_name": company_name,
            "sector": sector,
            "industry": industry,
            "website": website
        }
        
    except:
        print("Unable to fetch company data.")
        return {
            "company_name": "Unknown Company Name",
            "sector": "Unknown Sector",
            "industry": "Unknown Industry",
            "website": "N/A"
            }
    
def plots(ticker, sector):
    averages = pd.read_csv('../data/averages.csv', header=0)
    sector_avg = averages[sector]


# Function to generate the PDF
def generate_pdf_report(file_name, symbol_request='MSFT'):
    
    info = get_info(symbol_request)
    
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title Page
    elements.append(Paragraph("Financial Performance Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("This report is meant to be used for educational purposes only and is not meant as financial advice. For more information, see documentation.", styles['Normal']))
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(info.get("company_name"), styles['Heading2']))
    elements.append(Paragraph(info.get("sector"), styles['Normal']))
    elements.append(Paragraph(info.get("industry"), styles['Normal']))
    elements.append(Paragraph(info.get("website"), styles['Normal']))
    elements.append(Spacer(1, 48))

    elements.append(Paragraph("Prepared using data from the last four years, using the 'yFinance' python library.", styles['Italic']))
    elements.append(Spacer(1, 48))
    
    elements.append(PageBreak())
    
    # Notable Datapoints Page
    
    elements.append(Paragraph("Notable Datapoints over the Last 4 Years", styles['Heading1']))
    elements.append(Spacer(1, 24))
    # Placeholder for Table

    datapoints = pd.read_csv('../data/datapoints.csv')
    analysis = analyzer.FinancialAnalyzer(symbol_request)
    company_data = pd.DataFrame()
    company_data = analysis.load_data(
        datapoints['balance_sheet'].tolist(),
        datapoints['income_statement'].dropna().tolist(),
        datapoints['cash_flow'].dropna().tolist()
    )

    company_data['Year'] = company_data['Year'].astype(int)
    transposed_data = company_data.set_index('Year').T
    eps = transposed_data.loc['Basic EPS']
    transposed_data = transposed_data / 1_000_000
    transposed_data.loc['Basic EPS'] = eps
    # Replace this with actual DataFrame content
    elements.append(create_table_from_dataframe(transposed_data))
    elements.append(Paragraph("Numbers are displayed in millions (USD), where applicable, except for EPS."))
    elements.append(Spacer(1, 24))
    
    elements.append(PageBreak())
    
    # Ratios Page
    elements.append(Paragraph(f"Ratios for {symbol_request}", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Here are the calculated ratios for {symbol_request} over the last 4 years.", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Placeholder for Ratios Table
    company_ratios = analysis.analyze()
    company_ratios['year'] = company_ratios['year'].astype(int)
    transposed_ratios = company_ratios.set_index('year').T
    transposed_ratios = transposed_ratios.round(3)

    index_name_mapping = {
        'current_ratio': 'Current Ratio',
        'quick_ratio': 'Quick Ratio',
        'gross_profit': 'Gross Profit',
        'net_profit': 'Net Profit',
        'roa': 'Return on Assets',
        'roe': 'Return on Equity',
        'asset_turnover': 'Asset Turnover',
        'debt_to_equity': 'Debt to Equity',
        'interest_cover': 'Interest Cover',
    }
    transposed_ratios.rename(index=index_name_mapping, inplace=True)


    elements.append(create_table_from_dataframe(transposed_ratios))
    elements.append(Spacer(1, 24))
    
    # Comparison to Sector Averages Page
    elements.append(Paragraph(f"{symbol_request} Compared to Sector Averages", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Microsoft's financial ratios compared to its sector averages are presented below. Positive value means that the given datapoint was above the sector average.", styles['Normal']))
    elements.append(Paragraph("Sector averages are gathered by averaging out around 50 companies in the given sector, may not be accurate.", styles['Italic']))
    elements.append(Spacer(1, 24))
    # Placeholder for Sector Comparison Table

    difference = analysis.difference()
    difference = difference.set_index('ratio')
    difference = difference.round(3)
    difference.rename(index=index_name_mapping, inplace=True)

    elements.append(create_table_from_dataframe(difference))
    elements.append(Spacer(1, 24))
    
    elements.append(PageBreak())

    # Growth Rates Page
    elements.append(Paragraph(f"Growth Rates for {symbol_request}", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("The growth rates for key financial metrics are summarized below. Number are displayed in percentages.", styles['Normal']))
    elements.append(Spacer(1, 24))
    # Placeholder for Growth Rates Table

    growth_rates = analysis.growth_rates()
    growth_rates = growth_rates.set_index('ratio')
    growth_rates = growth_rates.round(2)
    growth_rates.rename(index=index_name_mapping, inplace=True)
    elements.append(create_table_from_dataframe(growth_rates))
    elements.append(Spacer(1, 24))

    elements.append(PageBreak())

    # Plots Page
    elements.append(Paragraph("Visual Analysis of Key Metrics", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("The following graphs represent the trends and patterns of important financial metrics.", styles['Normal']))
    # Placeholder for Plot Images
    # images = ['path_to_plot1.png', 'path_to_plot2.png']  # Replace with actual paths
    # for img_path in images:
    #     elements.append(Image(img_path, width=400, height=300))
    #     elements.append(Spacer(1, 24))

    sector = info['sector'].lower()
    averages = pd.read_csv('../data/averages.csv')

    ratio_index_map = {
        'current_ratio': 0,
        'quick_ratio': 1,
        'gross_profit': 2,
        'net_profit': 3,
        'roa': 4,
        'roe': 5,
        'asset_turnover': 6,
        'debt_to_equity': 7,
        'interest_cover': 8
    }
    
    columns_to_plot = ['year', 'current_ratio', 'quick_ratio', 'debt_to_equity']
    plot_df = company_ratios[columns_to_plot]

    # Step 3: Create subplots

    # Subplot configuration
    ratios_to_plot = [
        ('current_ratio', 'Current Ratio', 'skyblue', 'Sector Avg - Current Ratio', 'blue'),
        ('quick_ratio', 'Quick Ratio', 'lightgreen', 'Sector Avg - Quick Ratio', 'green'),
        ('debt_to_equity', 'Debt to Equity', 'salmon', 'Sector Avg - Debt to Equity', 'red')
    ]

    x = np.arange(len(plot_df.index))  # Positions for bars
    width = 0.25  # Narrower bars to look more compact

    # Step 3: Create the subplots with a vertical orientation
    fig, axs = plt.subplots(3, 1, figsize=(6, 12))  # More vertical layout with increased height and reduced width

    for i, (column, title, color, avg_label, avg_color) in enumerate(ratios_to_plot):
        ax = axs[i]  # Select subplot
        
        # Plot bars for each ratio
        ax.bar(x, plot_df[column], width, label=f'{title} {symbol_request}', color=color)
        
        # Add horizontal line for the sector average
        avg_value = averages[sector].iloc[ratio_index_map[column]]
        for xpos in x:
            ax.hlines(
                y=avg_value,
                xmin=xpos - width / 2,  # Align horizontal line with narrower bars
                xmax=xpos + width / 2,
                color=avg_color,
                linestyle='--',
                label=avg_label if xpos == 0 else None
            )
        
        # Set labels and titles for each subplot
        ax.set_xlabel('Year')
        ax.set_ylabel('Value')
        ax.set_title(f'{title} vs {sector} Sector Average')
        
        # Set the x-axis tick labels as integers (removing the decimal point)
        ax.set_xticks(x)
        ax.set_xticklabels(plot_df['year'].map(int))  # Use map(int) to remove the .0
        
        ax.legend(loc='upper right')

    # Fine-tune the layout for a more compact, vertical appearance
    plt.tight_layout()  # Automatically adjusts spacing between plots
    plt.subplots_adjust(hspace=0.5)  # Optional: fine-tune the vertical space between subplots

    # Save or show the plot
    plt.savefig(f'../data_output/{symbol_request}_ratios.png', dpi=300)

    elements.append(Image(f'../data_output/{symbol_request}_ratios.png', width=3*72, height=6*72))

    growth_rates = analysis.growth_rates()
    years = ['2022', '2023', '2024']
    ratios_to_plot = growth_rates['ratio'].values  # Ratio names
    ratios_growth = growth_rates.drop('ratio', axis=1).values  # Growth rate values for each ratio

    # Plot all the growth rates on the same chart
    plt.figure(figsize=(10, 6))

    # Use matplotlib.colormaps to get a distinct colormap
    colormap = plt.colormaps['tab10']  # Access the 'tab10' colormap
    colors = [colormap(i / len(ratios_to_plot)) for i in range(len(ratios_to_plot))]  # Generate distinct colors

    # Plot each ratio with a unique color
    for i, (ratio, growth) in enumerate(zip(ratios_to_plot, ratios_growth)):
        plt.plot(years, growth, label=ratio, marker='o', color=colors[i])

    # Set labels and title
    plt.xlabel('Year')
    plt.ylabel('Growth Rate (%)')
    plt.title('Growth Rates of Financial Ratios Over Time')

    # Add a legend to identify each ratio
    plt.legend(loc='best')

    # Add grid for better readability
    plt.grid(True)

    # Save the plot as a PNG (optional)
    plt.savefig(f'../data_output/{symbol_request}_rate_all.png', dpi=300)
    elements.append(Image(f'../data_output/{symbol_request}_rate_all.png', width=8*72, height=4*72))
    
    elements.append(PageBreak())

    # Appendix Page
    elements.append(Paragraph("Appendix", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Additional Disclaimers and Notes:", styles['Heading2']))
    elements.append(Paragraph("This report is based on data obtained from reliable sources but is for educational purposes only.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("For full financial statements and further analysis, please refer to the official filings of the company. Full financial statements can be exported into .xlsx. See Documentation.", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Data Source: https://finance.yahoo.com/", styles['Normal']))
    
    # Build the document with all the elements
    doc.build(elements)
    os.remove(f'../data_output/{symbol_request}_ratios.png')
    os.remove(f'../data_output/{symbol_request}_rate_all.png')



# Call the function to generate the PDF
def main():
    today_date = datetime.today().strftime('%y-%m-%d')
    parser = argparse.ArgumentParser(
        description='Python based program that can calculate financial ratios, growth rates, export financial statements and a report.',
        usage='%(prog)s <ticker_request> [-r] [-s {excel,csv} [{excel,csv} ...]]\n Libraries Required (run this command): pip install -r requirements.txt\n Make sure pip is installed by running: pip --version'
        )
    
    parser.add_argument(
        'ticker_request',  # Name of the argument
        type=str,
        help='The ticker symbol of the company (e.g., MSFT, AAPL, etc.). Accepts all combinations of upper and lower case letters.'
    )

    parser.add_argument(
        '-r', '--report',
        action='store_true',
        help='Generate a financial performance report.'
        )
    
    parser.add_argument(
        '-s', '--statements',
        nargs='+',  # Accept one or more formats
        choices=['excel', 'csv'],  # Limit options to 'excel' and 'csv'
        help='Export financial statements in specified formats (choose: excel, csv, or both).'   
    )

    args = parser.parse_args()
    args.ticker_request = args.ticker_request.upper()


    if args.report:
        generate_pdf_report(f"../report/financial_report_{args.ticker_request}_{today_date}.pdf", args.ticker_request)
    
    if args.statements:

        export_excel = 'excel' in args.statements
        export_csv = 'csv' in args.statements

        getstatements.retrieve_and_export_statements(
            ticker_request = args.ticker_request,
            excel=export_excel,
            csv=export_csv

        )



    if not args.report and not args.statements:
        parser.print_help()

if __name__ == "__main__":
    main()