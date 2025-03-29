import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import shutil
import logging

URL_B3 = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def prepare_data_folder():
    data_folder = os.path.join(os.getcwd(), 'bovespa')

    if not os.path.exists(data_folder):  # Create data folder if it doesn't exist
        os.makedirs(data_folder)
        logging.info(f"Pasta 'bovespa' criada em: {data_folder}")
    else:
        # Remove all files in data folder
        for filename in os.listdir(data_folder):
            file_path = os.path.join(data_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove path
                logging.info(f"Removido: {file_path}")
            except Exception as e:
                logging.exception(f"Erro ao remover {file_path}: {e}")


def download_b3_latest_data():
    options = Options()

    prepare_data_folder()  # Prepare data folder
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

    search_button = driver.find_element(
        By.ID, "segment")  # Search for "Setor de Atuação"
    search_button.send_keys("Setor de Atuação")
    time.sleep(5)

    download_button = driver.find_element(
        By.LINK_TEXT, "Download")  # Download the data
    download_button.click()
    logging.info(f"Realizando download dos dados da B3 em: {download_path}")
    time.sleep(5)
    driver.quit()


def main():
    download_b3_latest_data()  # Download the latest data from B3


if __name__ == '__main__':
    main()