import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig) :
        try:
            logging.info(f"{'='*20}Data Ingestion log started. {'='*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def download_income_data(self) -> str:
        pass

    def extract_tgz_file(self,tgz_file_path:str):
        pass

    def split_data_as_train_test(self):
        pass

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e