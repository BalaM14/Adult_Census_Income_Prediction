import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact
from income.pipeline.pipeline import Pipeline
from income.config.configuration import Configuration

def main():
    try:
        config_path = os.path.join("config","config.yaml")
        pipeline = Pipeline(Configuration(config_file_path=config_path))
        #pipeline.run_pipeline()
        pipeline.start()
        logging.info("main function execution completed")
        #data_validation_config = Configuration().get_data_validation_config()
        #print(data_validation_config)
        #data_transformation_config = Configuration().get_data_transformation_config()
        #print(data_transformation_conffig)
        #model_trainer_config = Configuration().get_model_trainer_config()
        #print(model_trainer_config)
    except Exception as e:
        logging.error(f"{e}")
        raise IncomeException(e,sys)
    


if __name__=="__main__":
    main()