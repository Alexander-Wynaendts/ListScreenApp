import openai
import re
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_software_hardware_screen(website_data, prompt_templates):
    # Retrieve the prompt template for Software-Hardware Classification
    prompt_template = prompt_templates.get("Website Software-Hardware Classification", "")
    if not prompt_template:
        print("Error: 'Software-Hardware Classification' prompt template not found.")
        return None

    # Format the prompt with website_data
    prompt = prompt_template.format(data=website_data)

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    gpt_analysis = response['choices'][0]['message']['content'].strip()
    gpt_answer = ''.join(filter(str.isdigit, gpt_analysis))
    return gpt_answer[-1] if gpt_answer else None

def gpt_software_service_screen(website_data, prompt_templates):
    # Retrieve the prompt template for Software-Service Classification
    prompt_template = prompt_templates.get("Website Software-Service Classification", "")
    if not prompt_template:
        print("Error: 'Software-Service Classification' prompt template not found.")
        return None

    # Format the prompt with website_data
    prompt = prompt_template.format(data=website_data)

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    gpt_analysis = response['choices'][0]['message']['content'].strip()
    gpt_answer = ''.join(filter(str.isdigit, gpt_analysis))
    return gpt_answer[-1] if gpt_answer else None

def gpt_enterprise_analysis(website_data, prompt_templates):
    # Retrieve the prompt template for Enterprise Analysis
    prompt_template = prompt_templates.get("Website Analysis", "")
    if not prompt_template:
        print("Error: 'Website Analysis' prompt template not found.")
        return None

    # Format the prompt with website_data
    prompt = prompt_template.format(data=website_data)

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

def website_analysis(website_data, prompt_templates):
    """
    Running the GPT analysis sequentially for a single company.
    website_data is a dictionary that must contain 'Website Data' (a dictionary of link:content).
    """

    company_screened = {"Website Data": website_data}
    total_length = sum(len(content) for content in website_data.values())

    # Step 1: Perform the first GPT screening (Software vs Hardware)
    gpt_answer = gpt_software_hardware_screen(website_data, prompt_templates)
    company_screened['GPT Website Screen'] = gpt_answer  # Save the result

    if gpt_answer == "1":
        # Step 2: Perform the second GPT screening (Software vs Service)
        gpt_answer = gpt_software_service_screen(website_data, prompt_templates)
        company_screened['GPT Website Screen'] = gpt_answer  # Update the result

    # Step 3: Check the total length of website data
    if total_length <= 500:
        # Mark fields as '-'
        company_screened['GPT Raw Analysis'] = "-"
        company_screened['GPT Description'] = "-"
        company_screened['GPT Industry'] = "-"
        company_screened['GPT Client Type'] = "-"
        company_screened['GPT Revenue Model'] = "-"
        company_screened['GPT Region'] = "-"
    else:
        # Process based on 'GPT Website Screen' value
        screen_result = company_screened['GPT Website Screen']
        if screen_result == "0":
            # Hardware
            company_screened['GPT Raw Analysis'] = "Hardware"
            company_screened['GPT Description'] = "Hardware"
            company_screened['GPT Industry'] = "Hardware"
            company_screened['GPT Client Type'] = "Hardware"
            company_screened['GPT Revenue Model'] = "Hardware"
            company_screened['GPT Region'] = "Hardware"
        elif screen_result == "2":
            # Service
            company_screened['GPT Raw Analysis'] = "Service"
            company_screened['GPT Description'] = "Service"
            company_screened['GPT Industry'] = "Service"
            company_screened['GPT Client Type'] = "Service"
            company_screened['GPT Revenue Model'] = "Service"
            company_screened['GPT Region'] = "Service"
        elif screen_result == "1":
            # Software, proceed with analysis
            gpt_analysis, formatted_analysis = gpt_enterprise_analysis(website_data, prompt_templates)
            company_screened.update(formatted_analysis)
            company_screened['GPT Raw Analysis'] = gpt_analysis
        else:
            # Unexpected result, mark as 'N.A.'
            company_screened['GPT Raw Analysis'] = "N.A."
            company_screened['GPT Description'] = "N.A."
            company_screened['GPT Industry'] = "N.A."
            company_screened['GPT Client Type'] = "N.A."
            company_screened['GPT Revenue Model'] = "N.A."
            company_screened['GPT Region'] = "N.A."

    company_screened.pop('GPT Website Screen', None)
    company_screened.pop('GPT Raw Analysis', None)

    return company_screened
