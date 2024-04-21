import os,sys
from income.logger import logging
from income.exception import IncomeException
from income.config.configuration import DataIngestionConfig
from income.entity.artifact_entity import DataIngestionArtifact
from income.pipeline.pipeline import Pipeline

def main():
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
    except Exception as e:
        logging.error(f"{e}")
        raise IncomeException(e,sys)
    


if __name__=="__main__":
    main()