import requests
from bs4 import BeautifulSoup
import csv
import time

def add_launch_vehicles(input_file, output_file):
    """
    Takes a CSV with INTLDES column and adds launch_vehicle column
    """
    print(f"Reading {input_file}...")
    
    # Read input CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)
    
    # Add launch_vehicle column if it doesn't exist
    if 'launch_vehicle' not in fieldnames:
        fieldnames.append('launch_vehicle')
    
    # Fetch launch data from Gunter's Space Page
    cache = {}
    
    for idx, row in enumerate(rows, 1):
        intldes = row.get('intldes', '').strip()
        
        if not intldes:
            row['launch_vehicle'] = ''
            continue
        
        # Extract year from INTLDES (e.g., '2023-001' -> 2023)
        try:
            year = int(intldes.split('-')[0])
        except:
            row['launch_vehicle'] = 'INVALID'
            continue
        
        # Fetch year data if not cached
        if year not in cache:
            print(f"Fetching data for year {year}...")
            url = f"https://space.skyrocket.de/doc_chr/lau{year}.htm"
            
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse table
                cache[year] = {}
                table = soup.find('table')
                
                if table:
                    for tr in table.find_all('tr'):
                        cols = tr.find_all('td')
                        if len(cols) >= 4:
                            id_col = cols[0].get_text(strip=True)
                            lv_col = cols[3].get_text(strip=True)
                            if id_col and lv_col:
                                cache[year][id_col] = lv_col
                
                time.sleep(2)  # Be nice to the server
            except Exception as e:
                print(f"Error fetching {year}: {e}")
                cache[year] = {}
        
        # Look up launch vehicle
        if intldes in cache[year]:
            row['launch_vehicle'] = cache[year][intldes]
            print(f"[{idx}/{len(rows)}] {intldes} -> {cache[year][intldes]}")
        else:
            row['launch_vehicle'] = 'NOT FOUND'
            print(f"[{idx}/{len(rows)}] {intldes} -> NOT FOUND")
    
    # Write output CSV
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Done! Processed {len(rows)} rows.")

if __name__ == "__main__":
    # Usage - just change these filenames
    add_launch_vehicles('input.csv', 'output.csv')
