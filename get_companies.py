import pandas as pd
import os
import re
import datetime
import shutil

def get_companies():
    """
    Get the list of companies from the csv file.
    
    Returns:
        pd.DataFrame: A dataframe with the list of companies.
    """
    # list of files in the daily_data folder
    files = os.listdir('daily_data')

    # create a unique list of companies
    companies = []

    # read all files
    for file in files:
        if file.endswith('.parquet'):
            data = pd.read_parquet(os.path.join('daily_data', file))
            cleaned_companies = [company for company in data['company'].unique() if company is not None]
            companies.extend(cleaned_companies)
            #break

    #for company in companies:
    #    print(company)
    #    company = re.sub(r'[^\w\s]', '', company)
    #    print(company)

    # clean each name in the list from special characters/punctuations using regex
    companies = [re.sub(r'[^\w\s]', '', company) for company in companies] 

    # sort and remove duplicates

    companies = list(sorted(set(companies)))

    # remove nan values
    #companies = [company for company in companies if str(company) != 'nan']

    return companies

def read_companies():
    """
    Read the list of companies from the text file.
    
    Returns:
        list: A list of companies.
    """
    files = os.listdir()

    company_file = [file for file in files if (file.startswith('companies') and file.endswith('.txt'))]
    if len(company_file) == 0:
        raise Exception('No companies file found.')
    else:
        company_file = company_file[0]

    companies = []
    with open(company_file, 'r', encoding="utf-8") as f:
        companies = f.readlines()
    companies = [company.strip() for company in companies]
    return company_file, companies

def copy_and_save_file(source):
    """
    Copy the file and save it.
    
    Args:
        file_name: str -> Name of the file to copy.
    
    Returns:
        None
    """
    destination = 'backup_companies.txt'
    shutil.copyfile(source, destination)

def delete_file(file_name):
    """
    Delete the file.
    
    Args:
        file_name: str -> Name of the file to delete.
    
    Returns:
        None
    """
    os.remove(file_name)


def list_to_text(companies):
    """
    Convert the list of companies to a text file.
    
    Args:
        companies: list -> List of companies.
    
    Returns:
        None
    """
    # file name with today's date
    file_name = 'companies_' + str(datetime.datetime.now().date()) + '.txt'
    with open(file_name, 'w', encoding="utf-8") as f:
        for company in companies:
            f.write(company + '\n')

def collect_companies():
    companies = get_companies()
    #print(companies)
    company_filename, saved_companies = read_companies()
    #print(company_filename)
    copy_and_save_file(company_filename)
    delete_file(company_filename)
    list_to_text(list(set(saved_companies+companies)))


if __name__ == '__main__':
    collect_companies()


