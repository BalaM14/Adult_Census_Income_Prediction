import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig) :
        try:
            logging.info(f"{'='*20}Data Ingestion log started. {'='*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e