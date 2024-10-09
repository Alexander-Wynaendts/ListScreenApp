import openai
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
import re
import os
from dotenv import load_dotenv
from pyppeteer import launch
import time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

async def fetch_page_content(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setUserAgent(headers['User-Agent'])
    await page.goto(url, {'waitUntil': 'networkidle2'})
    content = await page.content()
    await browser.close()
    return content

async def website_scraping(website_url):
    important_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'li', 'strong', 'em']
    structured_text = []
    try:
        page_content = await fetch_page_content(website_url)
    except Exception as e:
        return f"Failed to scrape the website. Error: {str(e)}"
    soup = BeautifulSoup(page_content, 'html.parser')
    page_title = soup.title.get_text(strip=True) if soup.title else "No Title"
    structured_text.append(f"H1: {page_title}")
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        structured_text.append(f"DESCRIPTION: {meta_description['content']}")
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
    return "\n".join(structured_text)

async def website_links(website_url):
    important_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'li', 'strong', 'em']
    structured_text = []
    links = set()
    try:
        page_content = await fetch_page_content(website_url)
    except Exception as e:
        return f"Failed to scrape the website. Error: {str(e)}", set()
    soup = BeautifulSoup(page_content, 'html.parser')
    page_title = soup.title.get_text(strip=True) if soup.title else "No Title"
    structured_text.append(f"H1: {page_title}")
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        structured_text.append(f"DESCRIPTION: {meta_description['content']}")
    for tag_name in important_tags:
        for tag in soup.find_all(tag_name):
            if tag_name in ['h1', 'h2', 'h3']:
                structured_text.append(f"{tag_name.upper()}: {tag.get_text(strip=True)}")
            elif tag_name == 'p':
                text = tag.get_text(strip=True)
                if len(text) > 10:
                    structured_text.append(f"PARAGRAPH: {text}")
            elif tag_name == 'ul':
                structured_text.append("LIST:")
            elif tag_name == 'li':
                structured_text.append(f"- {tag.get_text(strip=True)}")
            elif tag_name == 'strong':
                structured_text.append(f"**{tag.get_text(strip=True)}**")
            elif tag_name == 'em':
                structured_text.append(f"*{tag.get_text(strip=True)}*")
    for link in soup.find_all('a', href=True):
        full_link = urljoin(website_url, link['href'])
        if full_link.startswith(website_url) and full_link != website_url and urlparse(full_link).path != '/':
            links.add(full_link)
    return "\n".join(structured_text), links

def gpt_link_selection(website_links):
    prompt = f"""
    From the following list of URLs on a company website, choose the 2 most relevant pages to determine if the company is a SaaS startup. Prioritize URLs that:

    - Clearly describe the company's product or services.
    - Provide information on pricing, subscription plans, or service delivery methods.
    - Include details about the types of clients the company serves.

    Ignore URLs related to blogs, careers, or unrelated marketing content.

    **Link list**
    {website_links}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    gpt_response = response['choices'][0]['message']['content'].strip()
    links = re.findall(r'(https?://[^\s]+)', gpt_response)

    # Clean links by removing unwanted trailing characters like **, ', ", etc.
    cleaned_links = []
    for link in links:
        cleaned_link = re.sub(r'[\*\',"]+$', '', link)
        cleaned_links.append(cleaned_link)
    return cleaned_links[:2]

def gpt_website_screen(website_data):
    prompt = f"""
    You are an expert in classifying companies product/service as "Software" or "Hardware" based on the following dictionary of website links and their corresponding content.
    The dictionary following dictionary is structured as link1: content1, link2: content2, etc. Based on this data, determine if the company is primarily a Software or Hardware company.

    {website_data}

    Give a binary output:
    - "1" for a Software company
    - "0" for a Hardware company
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    gpt_analysis = response['choices'][0]['message']['content'].strip()
    gpt_answer = [char for char in gpt_analysis if char.isdigit()][-1]
    return gpt_answer, gpt_analysis

async def website_screening(website_url):
    try:
        website_page, link_list = await website_links(website_url)
        selected_links = gpt_link_selection(link_list)
        website_data = {website_url: website_page}
        for selected_link in selected_links:
            link_content = await website_scraping(selected_link)
            website_data[selected_link] = link_content
        website_screen, gpt_analysis = gpt_website_screen(website_data)
        return website_screen, website_data
    except Exception as e:
        return None, str(e)

async def website_sreen_process(startup_data):
    all_results = []
    for website_url in startup_data['Website URL']:
        result = await website_screening(website_url)
        all_results.append(result)
        time.sleep(1)  # Sleep between requests to avoid overload
    startup_data['GPT Website Screen'], startup_data['Website Data'] = zip(*all_results)
    return startup_data
