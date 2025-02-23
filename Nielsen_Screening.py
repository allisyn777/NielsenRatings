from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
import pandas as pd
import time

def scrape_nielsen_miami():
    """Navigates to Nielsen, selects Miami-Ft. Lauderdale, clicks Go, scrapes table data."""

    # 1. Set up the Chrome WebDriver (auto-install with webdriver_manager)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # 2. Go to Nielsen's market selection page
        url = "https://tlr.nielsen.com/tlr/public/market.do?method=loadAllMarket"
        driver.get(url)

        # 3. Wait for the dropdown to appear
        dropdown_locator = (By.ID, "marketSelect")  # <-- Adjust if the ID is different
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(dropdown_locator))

        market_dropdown = driver.find_element(*dropdown_locator)
        select = Select(market_dropdown)

        # (Optional) Print all dropdown options to find the exact text
        print("Available markets in dropdown:")
        for idx, option in enumerate(select.options):
            print(f"{idx}: '{option.text}'")

        # 4. Select the exact text that matches "MIAMI-FT. LAUDERDALE-HOLLYWOOD"
        #    Make sure to match the text you see printed above.
        select.select_by_visible_text("MIAMI-FT. LAUDERDALE-HOLLYWOOD")

        # 5. Click the "Go" button
        go_button = driver.find_element(By.ID, "goButton")  # <-- Adjust if the ID is different
        go_button.click()

        # 6. Wait for the ratings table to load on the new page
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # 7. Locate the table and extract data
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        # First row: headers
        headers = []
        th_cells = rows[0].find_elements(By.TAG_NAME, "th")
        for th in th_cells:
            headers.append(th.text.strip())

        # Remaining rows: data
        data = []
        for row in rows[1:]:
            td_cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [td.text.strip() for td in td_cells]
            if row_data:
                data.append(row_data)

        return headers, data

    except Exception as e:
        print(f"Error encountered: {e}")
        return None, None
    finally:
        # Always close the browser at the end
        driver.quit()

def save_to_pdf(headers, data, pdf_filename):
    """Save the table into a PDF file using FPDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Nielsen Ratings - Miami/Ft. Lauderdale", ln=True, align='C')
    pdf.ln(10)
    
    # Print headers
    pdf.set_font("Arial", 'B', 12)
    header_line = " | ".join(headers)
    pdf.cell(200, 10, txt=header_line, ln=True)
    pdf.ln(5)

    # Print rows
    pdf.set_font("Arial", '', 10)
    for row in data:
        row_line = " | ".join(row)
        pdf.cell(200, 8, txt=row_line, ln=True)
    
    pdf.output(pdf_filename)

def main():
    # Scrape the data
    headers, data = scrape_nielsen_miami()
    if not headers or not data:
        print("No data found or an error occurred.")
        return

    # Save to PDF
    pdf_file = "miami_fort_lauderdale_ratings.pdf"
    save_to_pdf(headers, data, pdf_file)
    print(f"Data saved to {pdf_file}")

    # (Optional) Save to Excel or JSON
    df = pd.DataFrame(data, columns=headers)
    df.to_excel("miami_fort_lauderdale_ratings.xlsx", index=False)
    df.to_json("miami_fort_lauderdale_ratings.json", orient="records", indent=4)
    print("Also saved Excel and JSON versions.")

if __name__ == "__main__":
    main()
# Jessie is pretty smart and the best