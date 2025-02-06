import os
import requests
from bs4 import BeautifulSoup
import json

# Fetch the webpage
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to fetch {url}")
        return None

# Extract main content
def extract_text(soup):
    main_content = soup.find('div', class_='c-wysiwyg')
    return main_content.get_text(separator='\n', strip=True) if main_content else 'No content found'

# Extract submenu links
def extract_submenu_links(soup):
    submenu_links = {}
    for submenu in soup.select('.c-menu__subnav .c-menu__item a'):
        title = submenu.get_text(strip=True)
        url = submenu.get('href')
        if url and title:
            submenu_links[title] = url
    return submenu_links

# Extract and download attached files
def extract_attachments(soup):
    attachments = {}
    for link in soup.find_all('a', href=True):
        file_url = link['href']
        # add base url if the link is relative
        if not file_url.startswith('http'):
            file_url = f"{base_url}{file_url}"
        if file_url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
            file_name = os.path.basename(file_url)
            # file_path = os.path.join('/data', file_name)
            file_path = file_name
            try:
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    attachments[file_name] = file_path
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")
    return attachments

# Main URL
base_url = "https://www.dmv.virginia.gov"
start_url = f"{base_url}/vehicles/registration/first-reg"
soup = fetch_page(start_url)

if soup:
    text_content = extract_text(soup)
    submenu_links = extract_submenu_links(soup)
    attachments = extract_attachments(soup)

    # Process submenu links
    submenu_data = {}
    for title, relative_url in submenu_links.items():
        full_url = f"{base_url}{relative_url}"
        submenu_soup = fetch_page(full_url)
        if submenu_soup:
            submenu_text = extract_text(submenu_soup)
            submenu_attachments = extract_attachments(submenu_soup)
            submenu_data[title] = {
                "url": full_url,
                "text_content": submenu_text,
                "attachments": submenu_attachments
            }

    # Save extracted data
    extracted_data = {
        "main_page": {
            "url": start_url,
            "text_content": text_content,
            "attachments": attachments
        },
        "submenu_pages": submenu_data
    }

    output_file = 'extracted_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4)

    print(f"Extracted data saved to {output_file}")
