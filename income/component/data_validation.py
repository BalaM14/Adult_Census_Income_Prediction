import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.entity.config_entity import DataValidationConfig
from income.constant import *
from income.entity.artifact_entity import DataIngestionArtifact

import pandas as pd


class DataVaidation:

    def __init__(self, data_validation_config:DataValidationConfig,data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'='*20}Data Validation log started. {'='*20}")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def is_train_test_file_exists(self) -> bool:
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

            if not is_available:
                taining_file_path = self.data_ingestion_artifact.train_file_path
                testing_file_path = self.data_ingestion_artifact.test_file_path
                message = f"Training file : {taining_file_path} or Testing file : {testing_file_path} is not present"
                logging.info(message)
                raise Exception(message)
            
            return is_available
        
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def vaidate_datatset_schema(self) -> bool:
        try:
            validation_status = False
            schema = self.data_validation_config.schema_file_path
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            train_df = pd.read_csv(train_file_path)
            test_df = pd.read_csv(test_file_path)

            #check the number of columns 
            if len(schema['columns']) != len(train_df.columns) or len(schema['columns']) != len(test_df.columns):
                message = f"The count of dataset columns were mis-matching"
                logging.info(message)
                raise Exception(message)
            
            #Check the column names are valid
            for i in schema['columns'].keys():
                if i not in train_df.columns or i not in test_df.columns:
                    message = f"The Column name [{i}] is not available in the dataset "
                    logging.info(message)
                    raise Exception(message)
                
            #Check the data type of the columns            
            for i in schema['columns'].keys():
                if schema['columns'][i] != train_df[i].dtype or schema['columns'][i] != test_df[i].dtype:
                    message = f"The Column name [{i}] is having an invalid datatype in the dataset "
                    logging.info(message)
                    raise Exception(message)
            
            #check the categorical column eligible values
            for i in schema['domain_value'].keys():
                unique_values=[j.strip() for j in train_df[i].unique()]
                for k in unique_values:
                    if k not in schema['domain_value'][i]:
                        message = f"The column name [{i}] is having an invalid value"
                        logging.info(message)
                        raise Exception(message)
                    
            validation_status = True
            message = f"The datasets of [{train_df}] & [{test_df}] are validated successfully"
            logging.info(message)
            return validation_status               

        except Exception as e:
            raise IncomeException(e,sys) from e


    def initiate_data_validation(self) -> DataIngestionArtifact:
        try:

            self.is_train_test_file_exists()
            self.vaidate_datatset_schema()

        except Exception as e:
            raise IncomeException(e,sys) from e


    def __del__(self) -> None:
        logging.info(f"{'='*20}Data Validation log Completed. {'='*20}")