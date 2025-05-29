import csv
import json
import requests
import time
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from utils.tier_calculator import calculate_tier

# CONFIGURATION FILE PATH (MODIFY THIS)

CONFIG_FILE_PATH = "config/config.json"

# Load configuration from config.json
with open(CONFIG_FILE_PATH, "r") as config_file:
    config = json.load(config_file)

# Access configuration values
INPUT_FILE_PATH = config["INPUT_FILE_PATH"]
OUTPUT_FILE_PATH = config["OUTPUT_FILE_PATH"]
DATABASE_FILE_PATH = config["DATABASE_FILE_PATH"]
OUTPUT_FILE_HEADERS = config["OUTPUT_FILE_HEADERS"]
TIME_DELAY = config["TIME_DELAY"]
MAX_REQUESTS = config["MAX_REQUESTS"]
MAX_AGE = config["MAX_AGE"]
HTTP_HEADERS = config["HTTP_HEADERS"]

BLIND_URL = "https://www.teamblind.com/company/"

# HELPER FUNCTIONS

def build_url(input_company_name):
    formatted_name = format_company_name(input_company_name)
    return f"{BLIND_URL}{formatted_name}"

def format_company_name(input_company_name):
    return input_company_name.replace(" & ", "&").replace(" ", "-")

def read_database_file():
    try:
        with open(DATABASE_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_database_file(database):
    with open(DATABASE_FILE_PATH, "w") as file:
        json.dump(database, file, indent=4)

def read_input_file():
    with open(INPUT_FILE_PATH, "r") as file:
        company_names = file.readlines()
    return [name.strip() for name in company_names]

def get_company_data_from_database(database, company_name):
    if company_name in database:
        company_data = database[company_name]
        current_date = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
        last_updated = datetime.strptime(company_data["last_updated"], "%Y-%m-%d")
        if (current_date - last_updated).days > MAX_AGE:
            print(f"\tData for {company_name} is stale. Fetching new data.", flush=True)
            del database[company_name]
            return None
        return company_data
    else:
        return None

def get_company_data_from_blind(database, input_company_name):
    url = build_url(input_company_name)
    response = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    if response.status_code != 200:
        print(f"\tFAILURE: Status Code = {response.status_code}", flush=True)
        return None
    else:
        try:
            # general
            company_name_tag = soup.find("div", class_="text-center text-2xl font-bold lg:text-left")
            company_name = company_name_tag.text.strip() if company_name_tag else None
            link_tag = soup.find("link", rel="canonical")
            url = link_tag["href"] if link_tag and "href" in link_tag.attrs else None

            # overview
            website = soup.find("h3", class_="text-base font-semibold sm:text-lg").text.strip()
            overview_div_list = soup.find_all("div", class_="text-base font-semibold sm:text-lg")
            industry = overview_div_list[0].text.strip()
            locations = overview_div_list[1].text.strip()
            founded = overview_div_list[2].text.strip()
            size = overview_div_list[3].text.strip()
            salary = overview_div_list[4].text.strip()

            # reviews
            overall_score = soup.find("div", class_="flex items-start gap-2 border-b border-gray-300 pb-1 pr-4 lg:flex-col lg:border-b-0 lg:border-r").find("div", class_="text-xl font-semibold").text.strip()
            reviews_div_list = soup.find("div", class_="grid grid-flow-row grid-cols-1 gap-x-10 gap-y-4 lg:ml-9 lg:grid-cols-2").find_all("div", class_="font-semibold")
            career_growth_score = reviews_div_list[0].text.strip()
            work_life_balance_score = reviews_div_list[1].text.strip()
            compensation_benefits_score = reviews_div_list[2].text.strip()
            company_culture_score = reviews_div_list[3].text.strip()
            management_score = reviews_div_list[4].text.strip()

            # compensation
            median_total_compensation = soup.find("p", class_="font-bold text-blue-system sm:text-lg").text.strip()
            compensation_h5_list = soup.find_all("h5", class_="text-md font-semibold")
            _25th_percentile = compensation_h5_list[0].text.strip()
            _70th_percentile = compensation_h5_list[1].text.strip()
            _90th_percentile = compensation_h5_list[2].text.strip()
            
            # other
            current_date = time.strftime("%Y-%m-%d")

            company_data = {
                # general
                "company_name": company_name,
                "url": url,
                # overview
                "website": website,
                "industry": industry,
                "locations": locations,
                "founded": founded,
                "size": size,
                "salary": salary,
                # reviews
                "overall": overall_score,
                "career_growth": career_growth_score,
                "work_life_balance": work_life_balance_score,
                "compensation_benefits": compensation_benefits_score,
                "company_culture": company_culture_score,
                "management": management_score,
                # compensation
                "median_total_compensation": median_total_compensation,
                "25th_percentile": _25th_percentile,
                "70th_percentile": _70th_percentile,
                "90th_percentile": _90th_percentile,
                # other
                "last_updated": current_date
            }
            database[input_company_name] = company_data
            return company_data
        except Exception as e:
            print(f"\tFAILURE: {e}", flush=True)
            traceback.print_exc()
            return None

def process_data(input_company_names):
    with open(OUTPUT_FILE_PATH, "w", newline="") as file:
        failed_companies = []
        requests_made = 0
        writer = csv.writer(file)
        header_row = []
        for key, value in OUTPUT_FILE_HEADERS.items():
            if value:
                header_row.append(key)
        writer.writerow(header_row)
        for i, input_company_name in enumerate(input_company_names):
            print(f"Processing {i + 1}/{len(input_company_names)}: {input_company_name}", flush=True)
            if not input_company_name:
                print("\tSKIPPED: Empty company name", flush=True)
                writer.writerow("")
                continue
            company_data = get_company_data_from_database(database, input_company_name)
            if company_data:
                print("\tSUCCESS: Got data from database", flush=True)
            else:
                if requests_made >= MAX_REQUESTS:
                    print("\tSKIPPED: Maximum number of requests reached", flush=True)
                else:
                    company_data = get_company_data_from_blind(database, input_company_name)
                    if company_data:
                        print("\tSUCCESS: Got data from Blind", flush=True)
                    requests_made += 1
                    time.sleep(TIME_DELAY)
            data_row = []
            if company_data:
                for key, value in OUTPUT_FILE_HEADERS.items():
                    if value:
                        if key == "tier":
                            tier = calculate_tier(company_data)
                            data_row.append(tier)
                        elif key in company_data:
                            data_row.append(company_data[key])
                        else:
                            data_row.append("")
            else:
                failed_companies.append(input_company_name)
            writer.writerow(data_row)
        if failed_companies:
            print("\nFailed to retrieve data for the following companies:", flush=True)
            for company in failed_companies:
                print(f"\t- {company}")

# MAIN FUNCTION

if __name__ == "__main__":
    input_company_names = read_input_file()
    database = read_database_file()
    process_data(input_company_names)
    write_database_file(database)
