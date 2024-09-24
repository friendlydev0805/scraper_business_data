from bs4 import BeautifulSoup 
from curl_cffi import requests as crequests
import csv
import mysql.connector

# Configuration
CONFIG_FILE = 'config.json'
DATABASE_FILE = 'database_config.json'
CSV_FILE = 'scraped_data.csv'
MAIN_URL = 'https://www.smergers.com'

def extract_info_site(url):
    try:
        detail_response = crequests.get(url, impersonate="chrome110")
        detail_response.raise_for_status()
        detail_soup = BeautifulSoup(detail_response.content, "lxml")
        return detail_soup
    except Exception as e:
        print(f"Error extracting info from {url}: {e}")
        return None

def extract_section_content(soup, section_title):
    # Find the heading first
    
    
    section_heading = soup.find('div', class_='description-heading', text=f'{section_title}')
    if section_heading:
        # Find the next sibling which contains the description
        section_content = section_heading.find_next_sibling()
        print("Section content: ", section_content.get_text(separator=" ", strip=True))
        return section_content.get_text(separator=" ", strip=True) if section_content else None
    return None

def parse_detail_data(soup, page_url):
    if soup is None:
        return None

    data = {}
    
    # Extract the itemprop="name" content
    title_div = soup.find('h1', class_='fw-semibold fs-3 text-link sme-v3-extra-lineheight')
    if title_div:
        data['Title'] = title_div.get_text(strip=True)
    else:
        data['Title'] = None
        return data
    
    data['Page url'] = page_url
    
    print("Page url: ", page_url)
    
    name_div = soup.find('div', itemprop='name')
    data['Subtitle'] = name_div.get_text(strip=True) if name_div else None
    
    description_div = soup.find('div', itemprop='description')
    data['Subtitle Summary Details'] = description_div.get_text(strip=True) if description_div else None
    
    reason_div = soup.find('span', class_='reason')
    data['Reason'] = reason_div.get_text(strip=True) if reason_div else None
    
    try:
        transaction_reason_list_div = soup.find_all('div', class_='transaction-reason')
        data['Includes'] = transaction_reason_list_div[1].get_text(strip=True) if transaction_reason_list_div[1] else None
    except Exception as e:
        print(f"Includes data: {e}")
    
    try:
        contact_list_div = soup.find_all('div', class_='field-value')
        data['Name Phone, Email'] = contact_list_div[0].get_text(strip=True) if contact_list_div[0] else None
        data['Business name'] = contact_list_div[1].get_text(strip=True) if contact_list_div[1] else None
    except Exception as e:
        print(f"Name Phone, Email data and Business name: {e}")
    
    table_row_list_div = soup.find_all('span', class_='key-fact-tooltip')
    span_row_list_div = soup.find_all('span', class_='generic-tooltip')
    
    # Extract all field-label and field-value pairs

    for row in soup.find_all('tr', class_='field'):
        label = row.find('td', class_='field-label').get_text(strip=True)
        value = row.find('td', class_='field-value').get_text(strip=True)
        
        match label:
            case 'Established' | 'Ownership Duration':
                data['Established'] = value
            case 'Employees':
                data['Employees'] = value
            case 'Legal Entity':
                data['Legal Entity'] = value
            case 'Reported Sales':
                data['Reported Sales'] = value
            case 'Run Rate Sales':
                data['Run Rate Sales'] = value
            case 'EBITDA Margin':
                data['EBITDA Margin'] = value
            case 'Industries':
                data['Industries'] = value
            case 'Locations':
                data['Locations'] = value
            case 'Local Time':
                data['Local Time'] = value
            case 'Listed By':
                data['Listed By'] = value
            case 'Status':
                data['Status'] = value
    
    documents_title = ""
    for document_item in soup.find_all('div', class_='document-wrapper col-sm-6 col-xs-12'):
        documents_title = document_item.get_text(strip=True) + ", " + documents_title
        
    data['Documents'] = documents_title
    
    section_text_div = soup.find('div', class_='sme-v3-extra-lineheight')
    section_text = section_text_div.get_text(strip=True) if section_text_div else None
    
    # Define section titles
    sections = ["Business Overview", "Products & Services Overview", "Assets Overview", "Facilities Overview", "Capitalization Overview"]

    # Dictionary to store the split content
    content = {}

    # Iterate over the sections and split the text
    for section in sections:
        # Find the start of the section
        start = section_text.find(section)
        if start != -1:
            # Find the end of the section
            end = len(section_text)
            for next_section in sections:
                if next_section != section:
                    next_start = section_text.find(next_section, start + len(section))
                    if next_start != -1 and next_start < end:
                        end = next_start
                        
            data[section] = section_text[start + len(section):end].strip()
    
    tags_div = soup.find('div', class_='business-keywords my-3 fs-2')
    data['Tags'] = tags_div.get_text(strip=True) if tags_div else None

    return data

def parse_data(soup):
    if soup is None:
        return None

    data = []
    
    # Find all elements with class 'listing-card'
    listing_cards = soup.find_all(class_='listing-card')
    
    for card in listing_cards:
        card_data = {}
        
        try:
            page_url = MAIN_URL + card.get('data-url')
            detail_soup = extract_info_site(page_url)
            card_data = parse_detail_data(detail_soup, page_url)            
            if card_data['Title'] is None:
                continue
            data.append(card_data)
        except AttributeError as e:
            print(f"Error parsing card data: {e}")

    return data

def save_to_csv(data, file_path):
    if not data:
        print("No data to save.")
        return
    
    # Flatten the list of lists into a single list of dictionaries
    flat_data = [item for sublist in data for item in sublist]
    
    # Use the first item's keys for the CSV header
    keys = flat_data[0].keys() if flat_data else []
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        dict_writer = csv.DictWriter(csvfile, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(flat_data)

# MySQL database connection
def connect_to_db():
    # Connect to MySQL server (without specifying a database initially)
    db_conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        port=3306
    )
    cursor = db_conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS solution_app")
    cursor.execute("USE solution_app")  # Switch to the new database

    # Create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            page_url VARCHAR(255),
            subtitle TEXT,
            subtitle_summary_details TEXT,
            reason TEXT,
            includes TEXT,
            name_phone_email TEXT,
            business_name TEXT,
            established VARCHAR(50),
            employees VARCHAR(50),
            legal_entity VARCHAR(100),
            reported_sales VARCHAR(100),
            run_rate_sales VARCHAR(100),
            ebitda_margin VARCHAR(50),
            industries TEXT,
            locations TEXT,
            local_time VARCHAR(50),
            listed_by VARCHAR(100),
            status VARCHAR(50),
            documents TEXT,
            business_overview TEXT,
            products_services_overview TEXT,
            assets_overview TEXT,
            facilities_overview TEXT,
            capitalization_overview TEXT,
            tags TEXT
        )
    """)

    return db_conn

# Save to MySQL
def save_to_mysql(data):
    if not data:
        print("No data to save to MySQL.")
        return
    
    db_conn = connect_to_db()
    cursor = db_conn.cursor()
    
    # Flatten the list of lists into a single list of dictionaries
    flat_data = [item for sublist in data for item in sublist]
    
    for record in flat_data:
        try:
            query = """INSERT INTO business_data (title, page_url, subtitle, subtitle_summary_details, reason, includes, name_phone_email, business_name, established, employees, legal_entity, reported_sales, run_rate_sales, ebitda_margin, industries, locations, local_time, listed_by, status, documents, business_overview, products_services_overview, assets_overview, facilities_overview, capitalization_overview, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                record.get('Title'),
                record.get('Page url'),
                record.get('Subtitle'),
                record.get('Subtitle Summary Details'),
                record.get('Reason'),
                record.get('Includes'),
                record.get('Name Phone, Email'),
                record.get('Business name'),
                record.get('Established'),
                record.get('Employees'),
                record.get('Legal Entity'),
                record.get('Reported Sales'),
                record.get('Run Rate Sales'),
                record.get('EBITDA Margin'),
                record.get('Industries'),
                record.get('Locations'),
                record.get('Local Time'),
                record.get('Listed By'),
                record.get('Status'),
                record.get('Documents'),
                record.get('Business Overview'),
                record.get('Products & Services Overview'),
                record.get('Assets Overview'),
                record.get('Facilities Overview'),
                record.get('Capitalization Overview'),
                record.get('Tags'),
            )
            cursor.execute(query, values)
        except Exception as e:
            print(f"Error saving to MySQL: {e}")
            continue
    
    db_conn.commit()
    cursor.close()
    db_conn.close()

if __name__ == "__main__":
    # URL template where the page number can be dynamically added
    base_url = "https://www.smergers.com/businesses-for-sale-and-investment-opportunities/c61c65c78c111b/?page={}"
    
    # List to store the scraped data
    all_data = []
    
    # Loop through pages 1 to 153
    for page_num in range(1, 154):
        url = base_url.format(page_num)
        print(f"Scraping page {page_num}: {url}")
        
        soup = extract_info_site(url)
        data = parse_data(soup)
        if data:
            all_data.append(data)
    
    # Save the scraped data to a CSV file
    save_to_csv(all_data, CSV_FILE)
    save_to_mysql(all_data)