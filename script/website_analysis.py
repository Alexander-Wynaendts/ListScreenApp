import openai
import re
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_software_hardware_screen(website_data):
    prompt = f"""
You are an expert in classifying companies' products/services as "Software" or "Hardware" based on the following dictionary of website links and their corresponding content.
The dictionary is structured as link1: content1, link2: content2, etc. Based on this data, determine if the company is primarily a Software or Hardware company.

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
    gpt_answer = ''.join(filter(str.isdigit, gpt_analysis))
    return gpt_answer[-1] if gpt_answer else None

def gpt_software_service_screen(website_data):
    prompt = f"""
You are an expert in classifying companies as "Software" or "Service" based on the following dictionary of website links and their corresponding content.
The dictionary is structured as link1: content1, link2: content2, etc. Based on this data, determine if the company is primarily offering Software or Service.

{website_data}

Give a binary output:
- "1" for Software
- "2" for Service
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    gpt_analysis = response['choices'][0]['message']['content'].strip()
    gpt_answer = ''.join(filter(str.isdigit, gpt_analysis))
    return gpt_answer[-1] if gpt_answer else None

def gpt_enterprise_analysis(website_data):
    prompt = f"""
You are an expert in analyzing companies based on the following dictionary of website links and their corresponding content. You are provided with a company's website scraped content stored in the following dictionary format (link1:content1, link2:content2, ...):

{website_data}

Analyze the content and return the following details in the exact format specified:

Product/Service: <Short, straightforward description of the company’s main product or service, e.g., "Automated quality control inspection for fresh produce to reduce waste.">
Industry: <Simplified industry classification, e.g., "E-commerce," "EdTech," "Fashion.">
Client Type: <B2B or B2C>
Revenue Model: <Use only one or two words like "subscription," "transaction fee," or "commission.">
Market Region: <Return only "Global" or a specific country, continent, or region, e.g., "Global," "Europe," "USA.">
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    gpt_analysis = response['choices'][0]['message']['content'].strip()

    description_match = re.search(r"Product/Service: (.+?)\n", gpt_analysis)
    industry_match = re.search(r"Industry: (.+?)\n", gpt_analysis)
    client_match = re.search(r"Client Type: (.+?)\n", gpt_analysis)
    revenue_match = re.search(r"Revenue Model: (.+?)\n", gpt_analysis)
    region_match = re.search(r"Market Region: (.+?)(?:\n|$)", gpt_analysis)

    # Check if 'Global' is in the region and replace it with "-"
    region = region_match.group(1) if region_match else "N.A."
    if "Global" in region:
        region = "-"

    formatted_analysis = {
        "GPT Description": description_match.group(1) if description_match else "N.A.",
        "GPT Industry": industry_match.group(1) if industry_match else "N.A.",
        "GPT Client Type": client_match.group(1) if client_match else "N.A.",
        "GPT Revenue Model": revenue_match.group(1) if revenue_match else "N.A.",
        "GPT Region": region,
    }

    return gpt_analysis, formatted_analysis

def website_analysis(company_info):
    """
    Running the GPT analysis sequentially for a single company.
    company_info is a dictionary that must contain 'Website Data' (a dictionary of link:content)
    """

    website_data = company_info.get('Website Data', {})
    total_length = sum(len(content) for content in website_data.values())

    print(f"The length is {total_length}")

    # Step 1: Perform the first GPT screening (Software vs Hardware)
    gpt_answer = gpt_software_hardware_screen(website_data)
    company_info['GPT Website Screen'] = gpt_answer  # Save the result

    if gpt_answer == "1":
        # Step 2: Perform the second GPT screening (Software vs Service)
        gpt_answer = gpt_software_service_screen(website_data)
        company_info['GPT Website Screen'] = gpt_answer  # Update the result

    # Step 3: Check the total length of website data
    if total_length <= 500:
        # Mark fields as '-'
        company_info['GPT Raw Analysis'] = "-"
        company_info['GPT Description'] = "-"
        company_info['GPT Industry'] = "-"
        company_info['GPT Client Type'] = "-"
        company_info['GPT Revenue Model'] = "-"
        company_info['GPT Region'] = "-"
    else:
        # Process based on 'GPT Website Screen' value
        screen_result = company_info['GPT Website Screen']
        if screen_result == "0":
            # Hardware
            company_info['GPT Raw Analysis'] = "Hardware"
            company_info['GPT Description'] = "Hardware"
            company_info['GPT Industry'] = "Hardware"
            company_info['GPT Client Type'] = "Hardware"
            company_info['GPT Revenue Model'] = "Hardware"
            company_info['GPT Region'] = "Hardware"
        elif screen_result == "2":
            # Service
            company_info['GPT Raw Analysis'] = "Service"
            company_info['GPT Description'] = "Service"
            company_info['GPT Industry'] = "Service"
            company_info['GPT Client Type'] = "Service"
            company_info['GPT Revenue Model'] = "Service"
            company_info['GPT Region'] = "Service"
        elif screen_result == "1":
            # Software, proceed with analysis
            gpt_analysis, formatted_analysis = gpt_enterprise_analysis(website_data)
            company_info.update(formatted_analysis)
            company_info['GPT Raw Analysis'] = gpt_analysis
        else:
            # Unexpected result, mark as 'N.A.'
            company_info['GPT Raw Analysis'] = "N.A."
            company_info['GPT Description'] = "N.A."
            company_info['GPT Industry'] = "N.A."
            company_info['GPT Client Type'] = "N.A."
            company_info['GPT Revenue Model'] = "N.A."
            company_info['GPT Region'] = "N.A."

    return company_info
