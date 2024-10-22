from .website_screening import website_screen_process
from .website_analysis import website_analysis_process

def company_screening(company_info):

    company_info['Status'] = "To Screen"
    company_info = website_screen_process(company_info)
    company_info = website_analysis_process(company_info)

    return company_info
