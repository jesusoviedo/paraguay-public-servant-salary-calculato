import os
import requests
import zipfile
import pandas as pd


def generate_url(year: int, month: int) -> str:

    return f'https://datos.sfp.gov.py/data/funcionarios_{year}_{month}.csv.zip' 


def download_file(uri: str, filename: str='filezip', extract_to: str= '.') -> str:
    
    zip_filename = os.path.join(extract_to, f"{filename}.zip")
    extracted_filenames = None

    try:
        response = requests.get(uri)
        response.raise_for_status()

        with open(zip_filename, 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            extracted_filenames = zip_ref.namelist()
            zip_ref.extractall(extract_to)

        print(f"Download and extraction completed. Files extracted to {extract_to}")
        os.remove(zip_filename)

        return extracted_filenames[0]

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except zipfile.BadZipFile as e:
        print(f"Error extracting ZIP file: {e}")


def read_data_set(file_name:str) -> pd.DataFrame:

    df = pd.read_csv(file_name, encoding='latin-1')
    os.remove(file_name)

    return df


def download_data_set(year: int, month: int) -> pd.DataFrame:

    url = generate_url(year, month)
    file = download_file(url)
    df = read_data_set(file)
    print("returning df")
    return df