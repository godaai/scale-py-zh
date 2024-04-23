import os
import shutil
import urllib

def nyc_taxi(data_path: str = "../data/nyc-taxi"):

    folder_path = os.path.join(os.getcwd(), "../data/nyc-taxi")
    download_url = [
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet",
    ]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for url in download_url:
        file_name = url.split("/")[-1]
        parquet_file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(os.path.join(folder_path, file_name)):
            print(f"正在下载 {file_name}")
            with urllib.request.urlopen(url) as response, open(parquet_file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

    return folder_path


def nyc_flights(data_path: str = "../data/"):
    folder_path = os.path.join(os.getcwd(), data_path)
    download_url = "https://dp.godaai.org/nyc-flights.zip"
    zip_file_path = os.path.join(folder_path, "nyc-flights.zip")
    if not os.path.exists(os.path.join(folder_path, "nyc-flights")):
        print(f"正在下载 nyc-flights.zip")
        with urllib.request.urlopen(download_url) as response, open(zip_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            zf = ZipFile(zip_file_path, 'r')
            zf.extractall(folder_path)
            zf.close()

    folder_path = os.path.join(folder_path, "nyc-flights")
    return folder_path