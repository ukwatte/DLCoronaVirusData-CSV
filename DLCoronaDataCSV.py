from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from functools import wraps
import logging
import time
import csv
import argparse

logger = logging.getLogger(__name__)
log_format = "%(asctime)s %(levelname)s -- %(message)s"
##Set the Log file path below - /tmp/log.log
logfilename = ''
logging.basicConfig(filename=logfilename,level=logging.DEBUG,format=log_format)
def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(func.__name__, round(end - start, 2)))
        return result
    return wrapper
@timed
def scrape_page(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
def log_error(e):
    logging.debug(e)
# @timed
def print_to_file(Data):
    Fields = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths', 'Total Recovered']
    filename = filepath
    logging.debug("Writing to file "+filename)
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(Fields)
        # writing the data rows
        csvwriter.writerows(Data)
    logging.debug("Susccefully written to "+filename)
    print("Susccefully written to ",filename)

@timed
def data_scraper(html):
    tableid="main_table_countries_today"
    tableData = html.find('table', id=tableid)
    rows = tableData.findAll('tr')
    data = [[td.findChildren(text=True) for td in tr.findAll("td")] for tr in rows]
    Data = []
    for i in data:
        if i and len(i[0]) <= 1 and i[0][0] != 'Total:':
            CountryData = []
            Country = i[0][0]
            TotalCases = i[1][0]
            try:
                NewCases = i[2][0]
            except Exception as e:
                NewCases = 0
            try:
                TotalDeaths = i[3][0]
            except Exception as e:
                TotalDeaths = 0
            try:
                NewDeaths = i[4][0]
            except Exception as e:
                NewDeaths = 0
            try:
                TotalRecovered = i[5][0]
            except Exception as e:
                TotalRecovered = 0
            CountryData.append(Country)
            CountryData.append(TotalCases)
            CountryData.append(NewCases)
            CountryData.append(TotalDeaths)
            CountryData.append(NewDeaths)
            CountryData.append(TotalRecovered)
            Data.append(CountryData)
    print_to_file(Data)
@timed
def main():
    logging.debug("------Start------")
    logging.debug("Staring to scrape www.worldometers.info/coronavirus/")
    url = 'https://www.worldometers.info/coronavirus/'
    response = scrape_page(url)
    html = BeautifulSoup(response, 'html.parser')
    maincounter = html.find_all(class_='maincounter-number')
    for i in maincounter:
        index = maincounter.index(i)
        if index == 0:
            prefix = "Total Case "
            print(prefix,i.text.strip())
        elif index == 1:
            prefix = "Total Deaths "
            print(prefix,i.text.strip())
        elif index == 2:
            prefix = "Total Recovered "
            print(prefix,i.text.strip())
    data_scraper(html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Getting the file to write data to.")
    parser.add_argument('filepath', action="store")
    args = parser.parse_args()
    filepath = args.filepath
    main()
    logging.debug("------End------")
