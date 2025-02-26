import os
import csv
import re
import time
import shutil
import logging
import boto3
import configparser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

config = configparser.ConfigParser()
config.read('config.ini')

URL_B3 = config.get("DEFAULT", "URL_B3")
BUCKET_NAME = config.get("S3", "BUCKET_NAME")
S3_PREFIX = config.get("S3", "S3_PREFIX")
AWS_ACCESS_KEY_ID = config.get("S3", "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config.get("S3", "AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = config.get("S3", "AWS_SESSION_TOKEN")
AWS_REGION = config.get("S3", "AWS_REGION")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

date_pattern = re.compile(r"IBOVDia_(\d{2})-(\d{2})-(\d{2})\.csv")


def prepare_data_folder():
    data_folder = os.path.join(os.getcwd(), 'bovespa')

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        logging.info(f"Pasta 'bovespa' criada em: {data_folder}")
    else:
        for filename in os.listdir(data_folder):
            file_path = os.path.join(data_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                logging.info(f"Removido: {file_path}")
            except Exception as e:
                logging.exception(f"Erro ao remover {file_path}: {e}")


def download_b3_latest_data():
    options = Options()
    prepare_data_folder()
    current_path = os.getcwd()
    download_path = os.path.join(current_path, "bovespa")
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=options)
    driver.get(URL_B3)
    time.sleep(5)

    try:
        download_button = driver.find_element(By.LINK_TEXT, "Download")
        download_button.click()
        logging.info(
            f"Realizando download dos dados da B3 em: {download_path}")
        time.sleep(10)
    except Exception as e:
        logging.error(f"Erro ao baixar os dados: {e}")
    finally:
        driver.quit()


def upload_to_s3(directory):
    s3_client = boto3.client("s3",
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             aws_session_token=AWS_SESSION_TOKEN,
                             region_name=AWS_REGION)
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            s3_key = S3_PREFIX + filename
            try:
                s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
                logging.info(
                    f"Arquivo {filename} enviado para s3://{BUCKET_NAME}/{s3_key}")
                os.remove(file_path)
                logging.info(
                    f"Arquivo {filename} removido do diretório local.")
            except Exception as e:
                logging.error(f"Erro ao enviar {filename} para S3: {e}")


def main():
    download_b3_latest_data()
    upload_to_s3('./bovespa/')


if __name__ == '__main__':
    main()
