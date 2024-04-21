from income.config.configuration import Configuration
from income.entity.config_entity import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact
from income.component.data_ingestion import DataIngestion
from income.logger import logging
from income.exception import IncomeException
import os,sys

class Pipeline:

    def __init__(self, config: Configuration = Configuration()) -> None:
        try:
            self.config = config
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    
    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())

            return data_ingestion.initiate_data_ingestion()
        
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_data_validation(self) -> DataValidationArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_data_transformation(self) -> DataTransformationArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e

    def start_model_training(self) -> ModelTrainingArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_model_pusher(self) -> ModelPusherArtifact:
        try:
            pass
        except Exception as e:
            raise IncomeException(e,sys) from e
        

    def run_pipeline(self):
        try:
            #Dataa Ingestion Piipeline
            data_inegstion_artifact = self.start_data_ingestion()
        except Exception as e:
            raise IncomeException(e,sys) from e