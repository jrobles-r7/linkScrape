#!/usr/bin/env python2
# Description: LinkedIn employee enumeration script.
# Developer(s): Nick Sanzotta and Jacob Robles.
"""linkScrape Core."""

import json
import os
import sys
import time
try:
    import requests
    from bs4 import BeautifulSoup
    from linkArguments import *
    from linkMangle import *
except Exception as errmessage:
    print("\n[!] Error: %s" % (errmessage))
    sys.exit(1)

# Authentication URLs
url_base = 'https://www.linkedin.com'
url_login = 'https://www.linkedin.com/uas/login-submit'
# Company search URL.
url_company = 'https://www.linkedin.com/ta/federator?orig=GLHD&verticalSelector=all&query='

# Mangle timestamp.
Mangle_timestamp = time.strftime("%m-%d-%Y_%H:%M")


class LinkScraper:
    """LinkedIn Scraper class."""

    def __init__(self, url_company, username, password):
        """..."""
        self.timestamp = time.strftime("%m-%d-%Y_%H:%M")
        self.username = username
        self.password = password
        self.url_company = url_company
        self.session = self.authenticate(url_base, url_login)
        self.log_path = 'logs/'

        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

    def authenticate(self, url_base, url_login):
        """Create a persistent HTTP session to LinkedIn.com."""
        # LinkedIn's Authentication errors.
        auth_error_password = "Hmm, that's not the right password."
        auth_error_generic = r"We\'re sorry. Something unexpected happened and your request could not be completed. Please try again."
        # HTTP client with persistent cookies..
        session = requests.Session()
        # Set user agent.
        user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11)'}
        session.headers.update(user_agent)
        # HTTP POST parameters
        html = session.get(url_base).content
        soup = BeautifulSoup(html, 'lxml')
        csrf = soup.find(id="loginCsrfParam-login")['value']
        http_params = {
            'session_key': self.username,
            'session_password': self.password,
            'loginCsrfParam': csrf,
        }
        # Authenticate with persistent cookies.
        try:
            response = session.post(url_login, data=http_params)
            print('[linkScrape] Request: %s' % (url_login))
            if response.status_code == 200:
                print('[LinkedIn.com] Response: HTTP/1.1 %s OK' % (response.status_code))
            else:
                print('[LinkedIn.com] Response: HTTP/1.1 %s' % (response.status_code))
            # Password error.
            if auth_error_password in response.text:
                print("[LinkedIn.com] Hmm, that's not the right password.")
                sys.exit(2)
            # Generic error, most likely invalid username.
            elif auth_error_generic in response.text:
                print("[LinkedIn.com] We\'re sorry. Something unexpected happened and your request could not be completed. Please try again.")
                print("[linkScrape] likely an invalid username caused this error.")
                sys.exit(2)
        except Exception as errmessage:
            print('[!] Error: %s' % (errmessage))

        return session

    def company_search(self, company_name):
        """Perform a company search on LinkedIn."""
        # Use the persistent HTTP session to LinkedIn.com
        session = self.session
        try:
            response = session.get(self.url_company + company_name)
            print('[linkScrape] Request: %s' % (response.url))
            if response.status_code == 200:
                print('[LinkedIn.com] Response: HTTP/1.1 %s OK' % (response.status_code))
            else:
                print('[LinkedIn.com] Response: HTTP/1.1 %s' % (response.status_code))
            json_data = json.loads(response.content)
        except ValueError as errmessage:
            print('[linkScrape] Error: %s' % (errmessage))
            print('[linkScrape] This is a common error, for best results try searching with a LinkedIn Company ID.')
            print('[linkScrape] Exiting ...')
            sys.exit(2)

        # Display the number of items in the JSON list "resultList"
        num_results = len(json_data['resultList'])
        # Build a list for searched Companies
        company_list = []
        company_info = []
        for index in range(num_results):
            if 'company' in json_data['resultList'][index]['sourceID']:
                company_list.append(json_data['resultList'][index]['displayName'])
                company_info.append([json_data['resultList'][index]['displayName'],
                                    json_data['resultList'][index]['subLine'],
                                    json_data['resultList'][index]['id'],
                                    json_data['resultList'][index]['url']])
            elif 'school' in json_data['resultList'][index]['sourceID']:
                company_list.append(json_data['resultList'][index]['displayName'])
                company_info.append([json_data['resultList'][index]['displayName'],
                                    json_data['resultList'][index]['subLine'],
                                    json_data['resultList'][index]['id'],
                                    json_data['resultList'][index]['url']])

        return company_list, company_info

    def parser(self, bs4soup):
        """Parse linkedIn employees, locations and occupations from bs4soup."""
        # Return container for employees.
        employee_list = []
        # Soup
        linkedin_soup = bs4soup.find_all('code')
        # locations dic.
        userlocations = {}
        # Set Bool value for myuser
        myuser = True
        for line in linkedin_soup:
            # datalet is not the droid we're looking for
            if 'datalet' not in line.get('id'):
                # print(line.string)
                try:
                    pjson = json.loads(line.string)
                except ValueError:
                    continue

                # Should reduce to one pass, grab all data, then print
                # First pass will grab all of the locations
                for di in pjson['included']:
                    try:
                        location = di['location'].strip().encode('utf-8')
                        profile = di['miniProfile'].strip().encode('utf-8')
                        userlocations[profile] = location
                    except KeyError:
                        pass

                # Second pass will associate locations with users
                for di in pjson['included']:
                    # We only care about dictionaries w/ first/last/occ
                    try:
                        first_name = di['firstName'].strip().encode('utf-8')
                        last_name = di['lastName'].strip().encode('utf-8')
                        occupation = di['occupation'].strip().encode('utf-8')
                        entity = di['entityUrn'].strip().encode('utf-8')
                    except KeyError:
                        continue
                    #
                    try:
                        userlocation = userlocations[entity]
                    except KeyError:
                        userlocation = ''
                        pass

                    # Filter out myuser
                    if myuser:
                        # print("Removing user:", first_name, last_name, ':', userlocation, ':', occupation)
                        myuser = False
                        continue
                    # Filter out empty names
                    if first_name is '' and last_name is '':
                        continue

                    # Parse out spaces in last_name to remove certification titles.
                    try:
                        delimiter = last_name.index(" ")
                        last_name = last_name[:delimiter]
                    except ValueError as errmessage:
                        pass
                    # Parse out commas in last_name to remove certification titles.
                    try:
                        delimiter = last_name.index(",")
                        last_name = last_name[:delimiter]
                    except ValueError as errmessage:
                        pass

                    # Encode name_location_occupation list.
                    try:
                        name_location_occupation = first_name.strip().encode('utf-8'), last_name.strip().encode('utf-8'), userlocation.strip().encode('utf-8'), occupation.strip().encode('utf-8')
                    except UnicodeDecodeError as errmessage:
                        # print(errmessage)
                        continue

                    # Append firstname, lastname, location and occupation to employee list.
                    employee_list.append(name_location_occupation)

        return employee_list

    def log_data(self, employee_list, directory_name):
            """Write parsed data to a log file."""
            # Verify directory exists.
            directory_path = '%s%s' % (self.log_path, directory_name)
            if not os.path.exists(directory_path):
                os.mkdir(directory_path)

            # Create employee-occupation file
            filename = '%s_%s' % ('employee-occupation', self.timestamp)
            file_path_eoccupation = os.path.join(directory_path, filename)
            for item in employee_list:
                # Format.
                employee_occupation = ' '.join(item)
                # Append to employee-occupation.
                with open(file_path_eoccupation, 'a') as f1:
                    f1.write('%s%s' % (employee_occupation, '\n'))

            # Create employee-name file
            filename = '%s_%s' % ('employee-name', self.timestamp)
            file_path_ename = os.path.join(directory_path, filename)
            for item in employee_list:
                # Format.
                employee_name_list = item[0:2]
                employee_name = ' '.join(employee_name_list)
                # Append to employee-occupation.
                with open(file_path_ename, 'a') as f1:
                    # Join and write
                    f1.write('%s%s' % (employee_name, '\n'))

            return file_path_eoccupation, file_path_ename

    def unique(self, file_path):
        """Remove duplicates lines form log file."""
        # Read the file.
        with open(file_path, 'r+') as f1:
            log_content = f1.readlines()
            # Parse unique content.
            unique_content = set(log_content)
        # Remove orginal contents of the file.
        with open(file_path, 'w') as f1:
            pass
        # Write unique contents to the file.
        with open(file_path, 'a+') as f1:
            for line in unique_content:
                f1.write(line)

def cls():
    """Clear screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_company_profile(company_profile):
    """Print company profie to STDOUT."""
    company_name = company_profile[0]
    industry_employees = company_profile[1]
    cid = company_profile[2]
    company_url = company_profile[3]
    # The last 4 entries in the sublist appears to always be correct.
    print('\n')
    print(' Company Name: %s' % (company_name))
    print(' Industry / Employees: %s' % (industry_employees))
    print(' LinkedIn Company ID: %s' % (cid))
    print(' URL: %s' % (company_url))
    print('\n')


def return_page_range(page_range):
    """Parse argument args.range, and returns page ranges to scrape."""
    if not '-' in page_range:
        page_start = 1
        page_end = int(page_range)
    elif '-' in page_range:
        page = page_range.split('-')
        page_start = page[0]
        page_end = page[1]
    else:
        print('[linkScrape] Please enter a valid integer or range:')
        sys.exit(2)

    return page_start, page_end


def url_builder(cid, university):
    """Build URL for employee scraping."""
    url_search_base = 'https://www.linkedin.com/search/results/people/?'
    url_search_people_company = '%sfacetCurrentCompany=["''%s''"]&page=' % (url_search_base, cid)
    url_search_people_university = '%s&facetSchool=["''%s''"]&origin=FACETED_SEARCH&page=' % (url_search_base, cid)
    if not university:
        url_employee_scraper = url_search_people_company
    else:
        url_employee_scraper = url_search_people_university

    return url_employee_scraper


def name(company_name, output, format_value, domain):
    """Managle function."""
    # Check if directory exists.
    directory_path = '%s%s' % ('logs/', company_name)
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
    # Create filename.
    filename = '%s%s_%s' % ('mangle', str(format_value), Mangle_timestamp)
    file_path = os.path.join(directory_path, filename)
    # Check if input file exists.
    if not os.path.isfile(output):
        print("[linkMangle] Error: name file not found.")
        print("[linkMangle] Exiting...")
        sys.exit(2)

    names = []
    # Generate a list of first and last name, then call mangle
    for line in open(output, 'r'):
        full_name = ''.join([c for c in line if c == " " or c.isalpha()])
        full_name = full_name.lower().split()
        names.append([full_name[0], full_name[-1]])

    if format_value == 1:
        newname = mangleOne(names, company_name, domain, file_path)
    elif format_value == 2:
        newname = mangleTwo(names, company_name, domain, file_path)
    elif format_value == 3:
        newname = mangleThree(names, company_name, domain, file_path)
    elif format_value == 4:
        newname = mangleFour(names, company_name, domain, file_path)
    elif format_value == 5:
        newname = mangleFive(names, company_name, domain, file_path)
    elif format_value == 6:
        newname = mangleSix(names, company_name, domain, file_path)
    elif format_value == 7:
        newname = mangleSeven(names, company_name, domain, file_path)
    elif format_value == 8:
        newname = mangleEight(names, company_name, domain, file_path)
    elif format_value == 9:
        newname = mangleNine(names, company_name, domain, file_path)
    elif format_value == 10:
        newname = mangleTen(names, company_name, domain, file_path)
    elif format_value == 11:
        newname = mangleEleven(names, company_name, domain, file_path)
    elif format_value == 12:
        newname = mangleTwelve(names, company_name, domain, file_path)
    elif format_value == 13:
        newname = mangleThirteen(names, company_name, domain, file_path)
    elif format_value == 14:
        newname = mangleFourteen(names, company_name, domain, file_path)
    elif format_value == 15:
        newname = mangleFifteen(names, company_name, domain, file_path)
    elif format_value == 16:
        newname = mangleSixteen(names, company_name, domain, file_path)
    elif format_value == 99:
        mangleAll(names, company_name, domain, file_path)
    else:
        sys.exit(2)

    print('[linkMangle] Created mangle file: %s' % (file_path))


if __name__ == "__main__":
    '''Main Menu.'''
    cls()
    print(banner)
    # Argparse vars
    args = parse_args()
    company_name = args.company
    page_range = args.range
    university = args.university
    # Code from version 1.x
    if args.input:
        print(args.input)
        name(args.company, args.input, args.mangle, args.domain)
        sys.exit(0)
    # ClassInstance
    linkScrape = LinkScraper(url_company, args.email, args.password)

    if company_name.isdigit():
        company_selected = True
        cid = company_name
        print('[linkScrape] Detected LinkedIn Company ID: %s' % (cid))
    else:
        company_selected = False
        # Company search - while loop, outer
        company_choice = 0
        while not company_selected:
            company_list, company_profile = linkScrape.company_search(company_name)

            # Index selection - while loop, inner
            index_select = False
            num_companies = len(company_list)
            while not index_select:
                print('\n %s: %s' % (str(0), 'Search again'))
                for index in range(num_companies):
                    print(' %s: %s: %s' % (str(index + 1), company_list[index], company_profile[index][1]))
                # Get input, if not num, prompt again
                try:
                    company_choice = int(raw_input('\n[linkScrape] Please select a menu item: '))
                except ValueError:
                    continue
                if company_choice == 0:
                    index_select = True
                    company_name = raw_input('[linkScrape] Enter new company search: ').strip()
                else:
                    company_choice = company_choice - 1
                    # If valid, we can move on. else reprompt
                    try:
                        print('[linkScrape] ENTERED: "%s"' % (company_list[company_choice]))
                    except IndexError:
                        continue

                    company_name = company_list[company_choice]
                    company = company_profile[company_choice]
                    cid = company_profile[company_choice][2]
                    # Print Company Profile.
                    print_company_profile(company)
                    # Terminate while loop.
                    index_select = True
                    company_selected = True
    raw_input('[linkScrape] Press <Enter> to scrape:')
    # Page Range - STDOUT
    page_start, page_end = return_page_range(args.range)
    print('[linkScrape] Scraping Pages: %s-%s' % (str(page_start), str(page_end)))
    # Build URL based on company or school.
    url_employee_scraper = url_builder(cid, university)
    # List containers
    employee_list = []
    employee_title = []
    # Create authentication session to LinkedIn.com
    session = linkScrape.authenticate(url_base, url_login)
    try:
        for index in range(int(page_start), int(page_end) + 1):
            # sleep
            time.sleep(args.timeout)
            # URL with page - STDOUT
            print('[linkScrape] Request: %s%s' % (url_employee_scraper, str(index)))
            # Downloading
            response = session.get(url_employee_scraper + str(index))
            html = response.content
            if response.status_code == 200:
                print('[LinkedIn.com] Response: HTTP/1.1 %s OK' % (response.status_code))
            else:
                print('[LinkedIn.com] Response: HTTP/1.1 %s' % (response.status_code))
            # soup
            bs4soup = BeautifulSoup(html, "lxml")
            # Parse employee names and titles.
            print('[linkScrape] Parsing Page: %s/%s' % (str(index), str(page_end)))
            print('\n')
            employee_list = linkScrape.parser(bs4soup)
            for item in employee_list:
                print('%s: %s :%s' % (' '.join(item[0:2]), item[3], item[2]))
            print('\n')
            # Write to log.
            employee_occupation_log, employee_name_log = linkScrape.log_data(employee_list, company_name)
            print('[linkScrape] Appended to: %s' % (employee_occupation_log))
            print('[linkScrape] Appended to: %s' % (employee_name_log))
    except KeyboardInterrupt:
        print('\n')
        print('[linkScrape] Ctrl+C pressed, executing linkMangle then exiting...')
    # Remove duplicates lines from "employee_name" log file.
    linkScrape.unique(employee_name_log)
    print('[linkScrape] Removed duplicates from: %s' % (employee_occupation_log))
    # Remove duplicates lines from "employee_occupation" log file.
    linkScrape.unique(employee_occupation_log)
    print('[linkScrape] Removed duplicates from: %s' % (employee_name_log))
    # Code from version 1.x
    name(company_name, employee_name_log, args.mangle, args.domain)
