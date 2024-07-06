import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

def fetch_report_details(ingredient_url, pbar):
    response = requests.get(ingredient_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'ContentContainer_ContentBottom_ingredientReferences'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Ignore header
            reports = []
            
            for row in rows:
                cells = row.find_all('td')
                status_cell = cells[1]
                link_tag = status_cell.find('a')
                date_reference = cells[2].text.strip()
                
                if link_tag and 'report' in link_tag.text.lower():
                    report_link = link_tag['href']
                    # Check for javascript:alert link
                    if 'javascript:alert' in report_link:
                        return "null", "null", "null"
                    report_link = f"https://cir-reports.cir-safety.org/{report_link}"
                    status = link_tag.text.strip()
                    reports.append((date_reference, report_link, status))
            
            if reports:
                formatted_reports = []
                for report in reports:
                    try:
                        report_date = pd.to_datetime(report[0], format='%B %d, %Y')
                    except ValueError:
                        try:
                            report_date = pd.to_datetime(report[0], format='%Y')
                        except ValueError:
                            try:
                                report_date = pd.to_datetime(report[0])
                            except ValueError:
                                report_date = pd.NaT  # Set as NaT if date not recognized

                    formatted_reports.append((report_date, report[1], report[2]))
                
                # Sort reports by date, treating NaT as older dates
                formatted_reports.sort(key=lambda x: (pd.Timestamp.min if pd.isna(x[0]) else x[0]), reverse=True)
                pbar.update(1)
                most_recent_report = formatted_reports[0]
                return most_recent_report[1], most_recent_report[2], most_recent_report[0] if pd.notna(most_recent_report[0]) else "Unknown Date"
    
    pbar.update(1)
    return "null", "null", "null"

def main():
    # Load the existing Excel file
    filename = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report.xlsx"
    df = pd.read_excel(filename)

    # Ensure there's a 'link' column in the DataFrame
    if 'link' not in df.columns:
        print("The 'link' column does not exist in the Excel file.")
        return

    # Create a tqdm progress bar
    with tqdm(total=min(70, len(df) - 30)) as pbar:  # Limit progress bar to 70 items or less
        report_links = []
        statuses = []
        date_references = []
        
        # Iterate from the 30th to the 100th link
        for link in df['link'][30:100]:
            report_link, status, date_reference = fetch_report_details(link, pbar)
            report_links.append(report_link)
            statuses.append(status)
            date_references.append(date_reference)

    # Add new columns to the DataFrame
    df.loc[30:99, 'Link del report'] = report_links  # For rows 30 to 99
    df.loc[30:99, 'Stato'] = statuses
    df.loc[30:99, 'Data/Referenza'] = date_references

    # Write the updated data back to the Excel file
    df.to_excel(filename, index=False, sheet_name='CIR Ingredients Report')
    
    print("Excel file successfully updated!")

# Run the main function
if __name__ == "__main__":
    main()
