import requests
import os
import zipfile
import boto3
import json
import pandas as pd
from botocore.exceptions import ClientError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple, Union
from pprint import pprint
import psycopg2
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from mage_ai.orchestration.triggers.api import trigger_pipeline

AWS_REGION = os.getenv('AWS_REGION')
AWS_ENPOINT_LOCAL = os.getenv('AWS_ENPOINT_LOCAL')


def generate_url(year: int, month: int) -> str:

    return f'https://datos.sfp.gov.py/data/funcionarios_{year}_{month}.csv.zip' 


def search_new_file(uri: str) -> bool:

    try:
        head_response = requests.head(uri)
        head_response.raise_for_status()  
        list_content_type = ['application/zip']

        if head_response.headers.get('Content-Type') in list_content_type:
           return True
        else:
           return False

    except requests.exceptions.RequestException as e:
        print(f"Error checking file: {e}")
        return False


def download_file(uri: str, filename: str='filezip', extract_to: str= '.'):
    
    zip_filename = os.path.join(extract_to, f"{filename}.zip")
    extracted_filenames = None

    try:
        response = requests.get(uri, stream=True)
        response.raise_for_status()

        with open(zip_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

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


def init_s3() -> boto3.client:

    s3 = None

    if AWS_ENPOINT_LOCAL:
        s3 = boto3.client('s3', region_name=AWS_REGION, endpoint_url=AWS_ENPOINT_LOCAL)
    else:
        s3 = boto3.client('s3', region_name=AWS_REGION)

    return s3


def generate_key(year: int, month: int) -> str:

    return f"funcionario_publico_{year}_{month}.parquet"


def search_s3_file(bucket_name: str, key: str) -> bool:
    
    s3 = init_s3()

    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e
        

def download_file_from_s3(bucket_name: str, key: str, local_filename: str):

    s3 = init_s3()

    try:
        s3.download_file(bucket_name, key, local_filename)
        print(f"File '{key}' successfully downloaded to '{local_filename}'")
    except Exception as e:
        print(f"Error downloading file: {e}")


def validate_new_dataset(year: int, month: int, bucket_name: str) -> Tuple[int, pd.DataFrame, pd.DataFrame] :
    
    url = generate_url(year, month)
    result = search_new_file(url)
    file_tmp_actual = None

    if not result:
        return 0, pd.DataFrame(), pd.DataFrame()
    else:
        file_tmp_actual = download_file(url)

    key = generate_key(year, month)
    result = search_s3_file(bucket_name, key)

    if result:
        return 0, pd.DataFrame(), pd.DataFrame()

    actual_year_month = datetime(year=year, month=month, day=1)
    last_year_month = actual_year_month - relativedelta(months=1)

    key = generate_key(last_year_month.year, last_year_month.month)
    result = search_s3_file(bucket_name, key)
    file_tmp_last = 'data_last.parquet'

    df_actual = pd.read_csv(file_tmp_actual, encoding='latin-1')
    os.remove(file_tmp_actual)

    if not result:
        return 1, df_actual, pd.DataFrame() #llamar al pipeline de pl_data_preparation_public_servant con el año y mes actual
    else:
        download_file_from_s3(bucket_name, key, file_tmp_last)
        df_last = pd.read_parquet(file_tmp_last)
        os.remove(file_tmp_last)        
        return 2, df_actual, df_last #aplicar tranformacion a df_last y quitar reporte
    

def generate_report_evidently(df_actual:pd.DataFrame, df_referencia:pd.DataFrame, sava_html=False) -> bool:

    reporte = Report(metrics=[DataDriftPreset()])
    reporte.run(reference_data=df_referencia, current_data=df_actual)
    dataset_drift = reporte.as_dict()['metrics'][0]['result']['dataset_drift']

    print(f"Data drift detected: {dataset_drift}")
    if  dataset_drift:
        save_report_evidently(reporte, sava_html)

    return dataset_drift


def summary_report_evidently(reporte: Report) -> dict:
    
    summary_report = reporte.as_dict()['metrics'][0]['result']
    
    return summary_report


def init_postgresql() -> psycopg2.connect:

    try:
        conn = psycopg2.connect(
            dbname= os.getenv('POSTGRES_DB'),
            user= os.getenv('POSTGRES_USER'),
            password= os.getenv('POSTGRES_PASSWORD'),
            host= os.getenv('POSTGRES_HOST'),
            port= os.getenv('POSTGRES_PORT')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
 

def create_table():

    conn = init_postgresql()
    try:
        cursor = conn.cursor()

        table_1 = """
            CREATE TABLE IF NOT EXISTS evidently_report_summary (
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                dataset_drift BOOLEAN NOT NULL,
                drift_share DOUBLE PRECISION NOT NULL,
                share_of_drifted_columns DOUBLE PRECISION NOT NULL,
                number_of_columns NUMERIC NOT NULL,
                number_of_drifted_columns NUMERIC NOT NULL,
                PRIMARY KEY (year, month, day)
            );
        """

        table_2 = """
            CREATE TABLE IF NOT EXISTS evidently_report_detail (
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                drift_detected BOOLEAN NOT NULL,
                drift_score DOUBLE PRECISION NOT NULL,
                stattest_threshold DOUBLE PRECISION NOT NULL,
                stattest_name VARCHAR(255) NOT NULL,
                current JSON NOT NULL,
                reference JSON NOT NULL,
                PRIMARY KEY (year, month, day, column_name),
                FOREIGN KEY (year, month, day) REFERENCES evidently_report_summary (year, month, day)
            );
        """

        cursor.execute(table_1)
        cursor.execute(table_2)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {e}")
    finally:
        cursor.close()


def insert_summary_report_evidently(dic_data: dict):

    conn = init_postgresql()
    try:
        cursor = conn.cursor()
        sql_query = """
            INSERT INTO evidently_report_summary (
                year, month, day, dataset_drift, drift_share, 
                share_of_drifted_columns, number_of_columns, number_of_drifted_columns
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        now = datetime.now()
    
        data = (now.year, 
                now.month, 
                now.day, 
                dic_data.get("dataset_drift"), 
                dic_data.get("drift_share"), 
                dic_data.get("share_of_drifted_columns"), 
                dic_data.get("number_of_columns"), 
                dic_data.get("number_of_drifted_columns"))

        cursor.execute(sql_query, data)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error inserting record: {e}")
    finally:
        cursor.close()


def detail_report_evidently(reporte: Report) -> list:

    data_drift_detail = reporte.as_dict()["metrics"][1]["result"]['drift_by_columns']
    detail_columns = []

    for column, detalles in data_drift_detail.items():
        detail_columns.append({
            'column_name': column,
            'drift_detected': detalles.get('drift_detected'),
            'drift_score': detalles.get('drift_score'),
            'stattest_threshold': detalles.get('stattest_threshold'),
            'stattest_name': detalles.get('stattest_name'),
            'current': detalles.get('current'),
            'reference': detalles.get('reference')
        })

    return detail_columns


def insert_detail_report_evidently(list_data: list):

    conn = init_postgresql()

    for dic_data in list_data:
        try:
            cursor = conn.cursor()
            sql_query = """
                INSERT INTO evidently_report_detail (
                    year, month, day, column_name, drift_detected, drift_score, 
                    stattest_threshold, stattest_name, current, reference
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            now = datetime.now()
        
            data = (now.year, 
                    now.month, 
                    now.day, 
                    dic_data.get("column_name"), 
                    dic_data.get("drift_detected"), 
                    dic_data.get("drift_score"), 
                    dic_data.get("stattest_threshold"), 
                    dic_data.get("stattest_name"),
                    json.dumps(dic_data.get("current")),
                    json.dumps(dic_data.get("reference")))

            cursor.execute(sql_query, data)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error inserting record: {e}")
        finally:
            cursor.close()


def save_report_evidently(reporte: Report, sava_html):

    create_table()

    summary = summary_report_evidently(reporte)
    insert_summary_report_evidently(summary)

    detail = detail_report_evidently(reporte)
    insert_detail_report_evidently(detail)

    if sava_html:
        reporte.save_html("reporte_evidently.html")


def training_flow(year, month, features=None, features_categorica=None, 
                  target=None, test_percentage=None, max_evaluations=None, 
                  models=None, early_stopping_rounds=None, verbose_eval=None):
    
    trigger_pipeline(
        'pl_data_preparation_public_servant',
        variables={"anho": year,
                   "mes": month,
                   "features": features,
                   "features_categorica": features_categorica,
                   "target": target,
                   "test_percentage": test_percentage},
        check_status=True,
        error_on_failure=True,
        schedule_name='tg_data_preparation_public_servant',
        verbose=True
    )

    trigger_pipeline(
        'pl_model_training_scikit_learn_public_servant',
        variables={"max_evaluations": max_evaluations, 
                   "models": models},
        check_status=True,
        error_on_failure=True,
        schedule_name='tg_retrain_model_scikit_learn_public_servant',
        verbose=True
    )


    trigger_pipeline(
        'pl_model_training_xgboost_public_servant',
        variables={"max_evaluations": max_evaluations, 
                   "early_stopping_rounds": early_stopping_rounds, 
                   "verbose_eval": verbose_eval},
        check_status=True,
        error_on_failure=True,
        schedule_name='tg_retrain_model_xgboost_public_servant',
        verbose=True
    )


    trigger_pipeline(
        'pl_model_register',
        variables={},
        check_status=True,
        error_on_failure=True,
        schedule_name='tg_model_register_public_servant',
        verbose=True
    )