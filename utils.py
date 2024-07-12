import os
import shutil
import urllib
from zipfile import ZipFile
import functools


def get_data(data_path, download_url: list[str]):
    folder_path = os.path.join(os.getcwd(), "../data", data_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for url in download_url:
        file_name = url.split("/")[-1]
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            print(f"正在下载 {file_name}")
            with urllib.request.urlopen(url) as response, open(
                file_path, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)
            if file_name.endswith(".zip"):
                with ZipFile(file_path, "r") as zf:
                    zf.extractall(folder_path)

    return folder_path


def data_path_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        data_path = func.__name__
        download_url = func()
        folder_path = get_data(data_path, download_url)
        return folder_path

    return wrapper


@data_path_decorator
def nyc_taxi():
    return [
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-02.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-04.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-05.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet",
    ]


@data_path_decorator
def nyc_flights():
    return ["https://scale-py.godaai.org/nyc-flights.zip"]


@data_path_decorator
def citi_bike():
    return [
        "https://s3.amazonaws.com/tripdata/JC-202301-citibike-tripdata.csv.zip",
        "https://s3.amazonaws.com/tripdata/JC-202302-citibike-tripdata.csv.zip",
        "https://s3.amazonaws.com/tripdata/JC-202303-citibike-tripdata.csv.zip",
        "https://s3.amazonaws.com/tripdata/JC-202304-citibike-tripdata.csv.zip",
    ]


@data_path_decorator
def more_citi_bike():
    return [
        "https://s3.amazonaws.com/tripdata/JC-202310-citibike-tripdata.csv.zip",
        "https://s3.amazonaws.com/tripdata/JC-202311-citibike-tripdata.csv.zip",
        "https://s3.amazonaws.com/tripdata/JC-202312-citibike-tripdata.csv.zip",
    ]


@data_path_decorator
def adult():
    return ["https://archive.ics.uci.edu/static/public/2/adult.zip"]


@data_path_decorator
def mark_twain():
    return [
        "https://www.booksatwork.org/wp-content/uploads/2014/06/Twain-Million-Pound-Note.pdf"
    ]
