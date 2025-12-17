# DESCRIPTION
# This tier calculator assigns scores based on overall.

def calculate_tier(company_data):
    if float(company_data["overall"]) < 3.4:
        return 'C'
    elif float(company_data["overall"]) < 3.8:
        return 'B'
    elif float(company_data["overall"]) < 4.2:
        return 'A'
    else:
        return '$'