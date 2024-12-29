import yfinance as yf
import pandas as pd
import getstatements
import analyzer

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


datapoints = pd.read_csv('../data/datapoints.csv')

def generate_data(ticker='MSFT'):
    statements = getstatements # Statements are exported into "/report" and the analysis tables are put into "/data_output"
    statements.retrieve_and_export_statements(ticker, export=False, report=True)

    analysis = analyzer.FinancialAnalyzer(ticker)
    company_data = analysis.load_data(
        datapoints['balance_sheet'].tolist(),
        datapoints['income_statement'].dropna().tolist(),
        datapoints['cash_flow'].dropna().tolist()
        )
    company_data = company_data.T

    company_ratios = analysis.analyze()
    company_ratios = company_ratios.T

    difference = analysis.difference()
    growth_rates = analysis.growth_rates()

    return {
        'company_data': company_data,
        'company_ratios': company_ratios,
        'difference': difference,
        'growth_rates': growth_rates
    }


    


def plots(ticker='MSFT'):
    pass


def generate_report(ticker_symbol, output_file):
        # Fetch company data using yfinance
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
    
    # Get today's date
    today = datetime.now().strftime("%B %d, %Y")
    
    # Generate the PDF cover page
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "Financial Report")
    
    # Company Name
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 150, f"{company_name} ({ticker_symbol.upper()})")
    
    # Company Info
    c.setFont("Helvetica", 12)
    text_lines = [
        f"Sector: {sector}",
        f"Industry: {industry}",
        f"Website: {website}",
        f"Date: {today}",
    ]
    y = height - 200
    for line in text_lines:
        c.drawCentredString(width / 2, y, line)
        y -= 20
    
    # Disclaimer
    c.setFont("Helvetica-Oblique", 10)
    disclaimer = "This report is for educational purposes only and is not intended as financial advice."
    c.drawString(50, 60, disclaimer)
    c.drawString(50, 50, 'For more information, see documentation.')
    
    c.showPage()
    
    # Fetch data
    analysis = analyzer.FinancialAnalyzer(ticker_symbol)
    company_data = analysis.load_data(
        datapoints['balance_sheet'].tolist(),
        datapoints['income_statement'].dropna().tolist(),
        datapoints['cash_flow'].dropna().tolist()
        )
    company_data = company_data.T

    company_ratios = analysis.analyze()
    company_ratios = company_ratios.T

    difference = analysis.difference()
    growth_rates = analysis.growth_rates()

    # Second Page: Data and Ratios Tables
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 50, "Data and Ratios")

    # Add Data Table
    y = height - 100
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Data:")
    y -= 20


    company_data_list = company_data.values.tolist()
    data_table = Table(company_data_list, colWidths=[160, 160])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    data_table.wrapOn(c, width, y)
    data_table.drawOn(c, 50, y - 100)

    # Add Ratios Table
    y -= 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Ratios:")
    y -= 20

    company_ratios_list = company_ratios.values.tolist()

    ratios_table = Table(company_ratios_list, colWidths=[160, 160])
    ratios_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    ratios_table.wrapOn(c, width, y)
    ratios_table.drawOn(c, 50, y - 100)

    # Save the PDF
    c.save()
    print(f"Cover page generated: {output_file}")



if __name__ == "__main__":
    request = input("Ticker Request: ").upper().strip()
    generate_report(request, '../report/financial_report.pdf')