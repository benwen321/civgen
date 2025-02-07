import os
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from pathlib import Path

# Base output directory
OUTPUT_DIR = 'dmv_site_data'

def get_path_components(url, base_url):
    """Extract path components from URL after removing base_url"""
    # Remove base_url from the full URL
    relative_path = url.replace(base_url, '')
    # Split path into components and filter out empty strings
    components = [comp for comp in relative_path.strip('/').split('/') if comp]
    return components

def create_nested_directory(url, base_url):
    """Create nested directory structure based on URL path"""
    components = get_path_components(url, base_url)
    
    if len(components) >= 2:
        # Take first two path components for directory structure
        dir_path = os.path.join(OUTPUT_DIR, components[0], components[1])
    else:
        # Fallback if URL doesn't have enough components
        dir_path = os.path.join(OUTPUT_DIR, 'root')
    
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def get_safe_filename(url, base_url):
    """Convert last part of URL path to safe filename"""
    components = get_path_components(url, base_url)
    if components:
        # Use the last component of the path as filename
        filename = components[-1]
    else:
        filename = 'index'
    return f"{filename}.json"

def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to fetch {url}")
        return None

def extract_text(soup):
    main_content = soup.find('div', class_='c-wysiwyg')
    return main_content.get_text(separator='\n', strip=True) if main_content else 'No content found'

def extract_submenu_links(soup):
    submenu_links = {}
    for submenu in soup.select('.c-menu__subnav .c-menu__item a'):
        title = submenu.get_text(strip=True)
        url = submenu.get('href')
        if url and title:
            submenu_links[title] = url
    return submenu_links

def extract_attachments(soup, base_url, dir_path):
    attachments = {}
    # Create attachments directory within the current page's directory
    attachments_dir = os.path.join(dir_path, 'attachments')
    os.makedirs(attachments_dir, exist_ok=True)

    for link in soup.find_all('a', href=True):
        file_url = link['href']
        if not file_url.startswith('http'):
            file_url = f"{base_url}{file_url}"
        
        if file_url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
            file_name = os.path.basename(file_url)
            file_path = os.path.join(attachments_dir, file_name)
            
            try:
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    attachments[file_name] = os.path.join('attachments', file_name)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")
    return attachments

def save_page_data(data, url, base_url):
    """Save page data to a JSON file in the appropriate nested directory"""
    dir_path = create_nested_directory(url, base_url)
    filename = get_safe_filename(url, base_url)
    filepath = os.path.join(dir_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"Saved data to {filepath}")
    return dir_path

def main():
    base_url = "https://www.dmv.virginia.gov"
    start_url = f"{base_url}/vehicles/registration/first-reg"
    
    # Create base output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    soup = fetch_page(start_url)
    if not soup:
        return
    
    # Process main page
    dir_path = create_nested_directory(start_url, base_url)
    main_page_data = {
        "url": start_url,
        "text_content": extract_text(soup),
        "attachments": extract_attachments(soup, base_url, dir_path)
    }
    save_page_data(main_page_data, start_url, base_url)
    
    # Process submenu pages
    submenu_links = extract_submenu_links(soup)
    for title, relative_url in submenu_links.items():
        full_url = f"{base_url}{relative_url}"
        submenu_soup = fetch_page(full_url)
        
        if submenu_soup:
            dir_path = create_nested_directory(full_url, base_url)
            submenu_data = {
                "url": full_url,
                "title": title,
                "text_content": extract_text(submenu_soup),
                "attachments": extract_attachments(submenu_soup, base_url, dir_path)
            }
            save_page_data(submenu_data, full_url, base_url)

if __name__ == "__main__":
    main()