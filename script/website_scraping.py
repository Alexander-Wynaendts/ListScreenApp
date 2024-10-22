import openai
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
scraping_bee_api = os.getenv("SCRAPING_BEE")

def website_scraping(website_url):
    """
    Scrapes the content of the given website URL and extracts structured information.
    Returns the content and a set of links found on the page.
    """
    important_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'li', 'strong', 'em']
    structured_text = []
    links = set()
    client = ScrapingBeeClient(api_key=scraping_bee_api)

    # Ensure the URL starts with 'https://' or 'http://'
    if not website_url.startswith('http'):
        website_url = 'https://' + website_url

    def scrape_page(url):
        try:
            response = client.get(url)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except Exception:
            return None

    # Try with 'https://'
    soup = scrape_page(website_url)
    if soup is None:
        # Try with 'http://'
        website_url = website_url.replace('https://', 'http://')
        soup = scrape_page(website_url)
        if soup is None:
            print(f"Failed to retrieve content from {website_url}")
            return None, None

    # Extract the page title
    if soup.title:
        page_title = soup.title.get_text(strip=True)
        structured_text.append(f"H1: {page_title}")
    else:
        structured_text.append("No Title")

    # Extract the meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description and 'content' in meta_description.attrs:
        structured_text.append(f"DESCRIPTION: {meta_description['content']}")

    # Extract important tags from the page
    for tag in soup.find_all(important_tags):
        if tag.name in ['h1', 'h2', 'h3']:
            structured_text.append(f"{tag.name.upper()}: {tag.get_text(strip=True)}")
        elif tag.name == 'p':
            text = tag.get_text(strip=True)
            if len(text) > 10:
                structured_text.append(f"PARAGRAPH: {text}")
        elif tag.name == 'ul':
            structured_text.append("LIST:")
        elif tag.name == 'li':
            structured_text.append(f"- {tag.get_text(strip=True)}")
        elif tag.name == 'strong':
            structured_text.append(f"**{tag.get_text(strip=True)}**")
        elif tag.name == 'em':
            structured_text.append(f"*{tag.get_text(strip=True)}*")

    # Find all links on the page
    for link in soup.find_all('a', href=True):
        full_link = urljoin(website_url, link['href'])
        # Ensure the link is within the same domain
        if urlparse(website_url).netloc == urlparse(full_link).netloc:
            links.add(full_link)

    website_content = "\n".join(structured_text)
    return website_content, links

def gpt_link_selection(website_links):
    link_list_text = '\n'.join(website_links)
    prompt = f"""
From the following list of URLs on a company website, choose the 2 most relevant pages to determine if the company is a SaaS startup. Prioritize URLs that:

- Clearly describe the company's product or services.
- Provide information on pricing, subscription plans, or service delivery methods.
- Include details about the types of clients the company serves.

Ignore URLs related to blogs, careers, or unrelated marketing content.

Return the top 2 URLs, each on a new line, with no additional text or formatting.

**Link list**
{link_list_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    gpt_response = response['choices'][0]['message']['content'].strip()

    links = re.findall(r'(https?://[^\s]+)', gpt_response)
    return links[:2]

def website_scaping(website_url):
    # Step 1: Scrape the landing page content and links
    website_content, link_list = website_scraping(website_url)
    if website_content is None:
        # If failed to scrape the website, return '1' and empty data
        return "1", {}

    # Step 2: Select the most relevant links using GPT
    selected_links = gpt_link_selection(link_list)

    # Step 3: Scrape all relevant website links and store in a dictionary
    website_data = {website_url: website_content}
    for selected_link in selected_links:
        link_content, _ = website_scraping(selected_link)
        if link_content:
            website_data[selected_link] = link_content

    return website_data
