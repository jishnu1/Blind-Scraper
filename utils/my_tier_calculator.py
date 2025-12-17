# DESCRIPTION
# This tier calculator assigns scores based on overall, work-life balance, company culture, size.
# It also excludes certain companies based on specific criteria.

exclusions = {

    "Audible":                  "fully onsite",
    "Dell":                     "fully onsite",

    "Discover Financial Services":  "bad location (Riverwoods, IL)",
    "IMC":                          "bad location (Chicago, IL)",
    "Lululemon":                    "bad location (Seattle, WA)",
    "Nike":                         "bad location (Beaverton, OR)",
    "Nintendo":                     "bad location (Redmond, WA)",
    "Redfin":                       "bad location (Seattle, WA)",
    "Riot Games":                   "bad location (Los Angeles, CA)",
    "Vertex Pharmaceuticals":       "bad location (Boston, MA)",
    "Viasat":                       "bad location (Carlsbad, CA)",
    "World Wide Technology":        "bad location (St. Louis, MO)",

}

def calculate_tier(company_data):
    if (company_data["company_name"]) in exclusions or company_data["overall"] == '' or company_data["work_life_balance"] == '' or company_data["company_culture"] == '':
        return 'X'
    elif float(company_data["overall"]) < 3.2 \
        or float(company_data["work_life_balance"]) < 3.4 \
        or float(company_data["company_culture"]) < 3.1 \
        or company_data["size"] == "1 to 50 employees" \
        or company_data["size"] == "51 to 200 employees":
        return 'C'
    elif float(company_data["overall"]) < 3.5 \
        or float(company_data["work_life_balance"]) < 3.8 \
        or float(company_data["company_culture"]) < 3.5:
        return 'B'
    elif float(company_data["overall"]) < 3.8 \
        or float(company_data["work_life_balance"]) < 4.2 \
        or float(company_data["company_culture"]) < 3.9:
        return 'A'
    else:
        return '$'