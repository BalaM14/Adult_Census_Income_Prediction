from income.config.configuration import Configuration
from income.component.data_ingestion import DataIngestion
from income.component.data_validation import DataValidation
from income.component.data_transformation import DataTransformation
from income.component.model_trainer import ModelTrainer
from income.component.model_evaluation import ModelEvaluation
from income.component.model_pusher import ModelPusher

from income.entity.artifact_entity import DataIngestionArtifact
from income.entity.artifact_entity import DataValidationArtifact
from income.entity.artifact_entity import DataTransformationArtifact
from income.entity.artifact_entity import ModelTrainerArtifact
from income.entity.artifact_entity import ModelEvaluationArtifact
from income.entity.artifact_entity import ModelPusherArtifact
from income.logger import logging
from income.exception import IncomeException
import os,sys
from threading import Thread
from collections import namedtuple

import uuid
from datetime import datetime
from income.constant import *
import pandas as pd

Experiment = namedtuple("Experiment",["experiment_id","initialization_timestamp","artifact_timestamp",
                                      "running_status","start_time","stop_time","execution_time",
                                      "message","experiment_file_path","accuracy","is_model_accepted"])





class Pipeline(Thread):
    experiment: Experiment = Experiment(*([None]*11))
    experiment_file_path = None

    def __init__(self, config: Configuration ) -> None:
        try:
            os.makedirs(config.training_pipeline_config.artifact_dir,exist_ok=True)
            Pipeline.experiment_file_path = os.path.join(config.training_pipeline_config.artifact_dir,EXPERIMENT_DIR,EXPERIMENT_FILE_NAME)
            super().__init__(daemon=False,name='Pipeline')
            self.config = config
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    
    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(
                data_ingestion_config=self.config.get_data_ingestion_config()
                )

            return data_ingestion.initiate_data_ingestion()
        
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_data_validation(self,data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            data_validation = DataValidation(
                data_validation_config=self.config.get_data_validation_config(),
                data_ingestion_artifact=data_ingestion_artifact
                )

            return data_validation.initiate_data_validation()
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_data_transformation(self,data_ingestion_artifact: DataIngestionArtifact,
                                   data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            data_transformation = DataTransformation(
                data_transformation_config=self.config.get_data_transformation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
                )
            
            return data_transformation.initiate_data_transformation()
        except Exception as e:
            raise IncomeException(e,sys) from e

    def start_model_training(self,data_transformation_artifact:DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(model_trainer_config=self.config.get_model_trainer_config(),
                                         data_transformation_artifact=data_transformation_artifact)
            
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_model_evaluation(self,data_ingestion_artifact: DataIngestionArtifact,
                                    data_validation_artifact: DataValidationArtifact,
                                    model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:
        try:
            model_evaluation = ModelEvaluation(model_evaluation_config=self.config.get_model_evaluation_config(),
                                               data_ingestion_artifact=data_ingestion_artifact,
                                               data_validation_artifact=data_validation_artifact,
                                               model_trainer_artifact=model_trainer_artifact)
            return model_evaluation.initiate_model_evaluation()
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    def start_model_pusher(self, model_evaluation_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(model_pusher_config=self.config.get_model_pusher_config(),
                                       model_evaluation_artifact=model_evaluation_artifact)
            return model_pusher.initiate_model_pusher()
        except Exception as e:
            raise IncomeException(e,sys) from e
        

    def run_pipeline(self):
        try:
            if Pipeline.experiment.running_status:
                logging.info("Pipeline is already running")
                return Pipeline.experiment
            
            logging.info("Pipeine Starting")

            experiment_id = str(uuid.uuid4())

            Pipeline.experiment = Experiment(experiment_id=experiment_id,initialization_timestamp=self.config.time_stamp,
                                             artifact_timestamp=self.config.time_stamp,running_status=True,
                                             start_time=datetime.now(),stop_time=None,execution_time=None,
                                             message="Pipeline has been started",experiment_file_path=Pipeline.experiment_file_path,
                                             accuracy=None,is_model_accepted=None)
            
            logging.info(f"Pipeine Experiment : [{Pipeline.experiment}]")
            self.save_experiment()


            #Data Ingestion Piipeline
            data_inegstion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_inegstion_artifact)
            data_transformation_artifact = self.start_data_transformation(
                                                data_ingestion_artifact=data_inegstion_artifact,
                                                data_validation_artifact=data_validation_artifact
                                                )
            model_trainer_artifact = self.start_model_training(
                                                data_transformation_artifact=data_transformation_artifact
                                                )
            model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_inegstion_artifact,
                                                                    data_validation_artifact=data_validation_artifact,
                                                                    model_trainer_artifact=model_trainer_artifact)
            if model_evaluation_artifact.is_model_accepted:
                model_pusher_artifact = self.start_model_pusher(model_evaluation_artifact=model_evaluation_artifact)
                logging.info(f"Model Pusher Artifact : [{model_pusher_artifact}]")
            else:
                logging.info(f"Trained Model Rejected")
            
            logging.info(f"Pipeline Completed")

            stop_time = datetime.now()
            Pipeline.experiment = Experiment(experiment_id=Pipeline.experiment.experiment_id,initialization_timestamp=self.config.time_stamp,
                                             artifact_timestamp=self.config.time_stamp,running_status=False,
                                             start_time=Pipeline.experiment.start_time,stop_time=stop_time,execution_time=stop_time - Pipeline.experiment.start_time,
                                             message="Pipeline has been completed",experiment_file_path=Pipeline.experiment_file_path,
                                             accuracy=model_trainer_artifact.model_accuracy,is_model_accepted=model_evaluation_artifact.is_model_accepted)
            logging.info(f"Pipeline Experiment : [{Pipeline.experiment}]")
            self.save_experiment()

        except Exception as e:
            raise IncomeException(e,sys) from e

    
    def run(self):
        try:
            self.run_pipeline()
        except Exception as e:
            raise IncomeException(e,sys) from e
        

    def save_experiment(self):
        try:
            if Pipeline.experiment is not None:
                experiment = Pipeline.experiment
                experiment_dict = experiment._asdict()
                experiment_dict: dict = {key: [value] for key,value in experiment_dict.items()}

                experiment_dict.update({
                    "Created_time_stamp": [datetime.now()],
                    "experiment_file_path": [os.path.basename(Pipeline.experiment.experiment_file_path)]
                })

                experiment_report = pd.DataFrame(experiment_dict)

                os.makedirs(os.path.dirname(Pipeline.experiment_file_path),exist_ok=True)
                if os.path.exists(Pipeline.experiment_file_path):
                    experiment_report.to_csv(Pipeline.experiment_file_path, index=False, header=False, mode ='a')
                else:
                    experiment_report.to_csv(Pipeline.experiment_file_path,mode='w',index=False,header = True)
            else:
                print("First start experiment")

        except Exception as e:
            raise IncomeException(e,sys) from e
        
    @classmethod
    def get_experiments_status(cls, limit: int = 5) -> pd.DataFrame:
        try:
            if os.path.exists(Pipeline.experiment_file_path):
                df = pd.read_csv(Pipeline.experiment_file_path)
                limit = -1 * int(limit)
                return df[limit:].drop(columns=["experiment_file_path", "initialization_timestamp"], axis=1)
            else:
                return pd.DataFrame()
        except Exception as e:
            raise IncomeException(e, sys) from e