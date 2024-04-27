import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact
from income.pipeline.pipeline import Pipeline
from income.config.configuration import Configuration

def main():
    try:
        #pipeline = Pipeline()
        #pipeline.run_pipeline()
        #data_validation_config = Configuration().get_data_validation_config()
        #print(data_validation_config)
        #data_transformation_config = Configuration().get_data_transformation_config()
        #print(data_transformation_conffig)
        model_trainer_config = Configuration().get_model_trainer_config()
        print(model_trainer_config)
    except Exception as e:
        logging.error(f"{e}")
        raise IncomeException(e,sys)
    


if __name__=="__main__":
    main()