import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact

#import tarfile
import zipfile
from six.moves import urllib
import pandas as pd
import numpy as np
import shutil

from sklearn.model_selection import StratifiedShuffleSplit

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig) :
        try:
            logging.info(f"{'=='*20}Data Ingestion log started. {'=='*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def download_income_data(self) -> str:
        try:
            #Downloading the dataset 
            download_url = self.data_ingestion_config.dataset_download_url
            #Folder location to download file 
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir
            #To cheeck if the folder exists, but in this case it won't bcoz we using timestamp
            if os.path.exists(tgz_download_dir):
                os.remove(tgz_download_dir)
            #Create the tgz_download directory
            os.makedirs(tgz_download_dir,exist_ok=True)
            #To get the filename from the url
            income_file_name = os.path.basename(download_url)
            #Download data in the below path
            tgz_file_path = os.path.join(tgz_download_dir,income_file_name)

            logging.info(f"Downloading file from [{download_url}] into [{tgz_file_path}]")
            #Downloading the data from the url & saving it to tgz_file_path
            urllib.request.urlretrieve(download_url,tgz_file_path)
            logging.info(f"File : [{tgz_file_path}] has beeen downloaded successfully")

            return tgz_file_path

        except Exception as e:
            raise IncomeException(e,sys) from e

    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)
            #Create the raw_data_dir directory
            os.makedirs(raw_data_dir,exist_ok=True)
            
            logging.info(f"Extracting the tgz_file : [{tgz_file_path}] into the dir: [{raw_data_dir}]")
            """with tarfile.open(tgz_file_path) as income_tgz_file_obj:
                income_tgz_file_obj.extractall(path=raw_data_dir)"""
            
            shutil.copy(tgz_file_path, raw_data_dir)

            logging.info(f"Extraction completed successfully")

        except Exception as e:
            raise IncomeException(e,sys) from e

    def split_data_as_train_test(self):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            #The below cmnd will fetch all filenames in raw_data_dir and return the first file name from the list
            file_name = os.listdir(raw_data_dir)[0]

            income_file_path = os.path.join(raw_data_dir,file_name)
            income_data_frame = pd.read_csv(income_file_path)
            income_data_frame["age_cat"]=pd.cut(income_data_frame['age'],bins=[15,30,45,60,75,np.inf],
                                                labels=[1,2,3,4,5])
            
            strat_train_set = None
            strat_test_set = None

            split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
            logging.info(f"Splitting data into train & test data")
            for train_index, test_index in split.split(income_data_frame,income_data_frame['age_cat']):
                strat_train_set = income_data_frame.loc[train_index].drop("age_cat",axis=1)
                strat_test_set = income_data_frame.loc[test_index].drop("age_cat",axis=1)

                train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,file_name)
                test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,file_name)

                if strat_train_set is not None:
                    os.makedirs(self.data_ingestion_config.ingested_train_dir)
                    logging.info(f"Exporting training dataset to file : [{train_file_path}]")
                    strat_train_set.to_csv(train_file_path,index=False)
                
                if strat_test_set is not None:
                    os.makedirs(self.data_ingestion_config.ingested_test_dir)
                    logging.info(f"Exporting testing dataset to file : [{test_file_path}]")
                    strat_test_set.to_csv(test_file_path,index=False)

                data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                                                test_file_path=test_file_path,
                                                                is_ingested=True,
                                                                message=f"Data Ingestion completed successfully")
                
                logging.info(f"Data Ingestion Artifact : [{data_ingestion_artifact}]")

                return data_ingestion_artifact          
            
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            tgz_file_path = self.download_income_data()
            self.extract_tgz_file(tgz_file_path=tgz_file_path)
            
            return self.split_data_as_train_test()

        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def __del__(self) -> None:
        logging.info(f"{'=='*20}Data Ingestion log Completed. {'=='*20} \n\n")