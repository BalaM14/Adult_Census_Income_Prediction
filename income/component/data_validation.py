import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.entity.config_entity import DataValidationConfig
from income.constant import *
from income.entity.artifact_entity import DataIngestionArtifact


class DataVaidation:

    def __init__(self, data_validation_config:DataValidationConfig,data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'='*20}Data Validation log started. {'='*20}")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def is_train_test_file_exists(self):
        try:
            logging.info(f"Checking if train & test data is available")
            is_train_file_exist = False
            is_test_file_exist = False

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)

            is_available = is_train_file_exist and is_test_file_exist

            logging.info(f"Is train & test file exists ? {is_available}")
            return is_available
        
        except Exception as e:
            raise IncomeException(e,sys) from e


    def initiate_data_validation(self) -> DataIngestionArtifact:
        try:

            train_test_file_available = self.is_train_test_file_exists()

            if train_test_file_available 

        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def __del__(self) -> None:
        logging.info(f"{'='*20}Data Validation log Completed. {'='*20}")