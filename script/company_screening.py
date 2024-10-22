from .website_screening import website_screen_process
from .website_analysis import website_analysis_process

def company_screening(company_info):

    # Add status directly to the dictionary
    company_info['Status'] = "To Screen"

    # Perform website screening (now expects a dictionary)
    company_info = website_screen_process(company_info)

    # Perform website analysis (now expects a dictionary)
    company_info = website_analysis_process(company_info)

    # Return the final processed result as a success message
    return company_info
