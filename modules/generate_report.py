from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageBreak
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import yfinance as yf
import analyzer


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
    elements.append(Spacer(1, 24))
    # Placeholder for Plot Images
    # images = ['path_to_plot1.png', 'path_to_plot2.png']  # Replace with actual paths
    # for img_path in images:
    #     elements.append(Image(img_path, width=400, height=300))
    #     elements.append(Spacer(1, 24))
    
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



# Call the function to generate the PDF
if __name__ == "__main__":
    generate_pdf_report("../report/Financial_Performance_Report.pdf")
