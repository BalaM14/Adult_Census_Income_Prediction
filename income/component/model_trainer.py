
from income.logger import logging
from income.exception import IncomeException
from income.entity.config_entity import ModelTrainerConfig
from income.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
import os,sys
from income.entity.model_factory import ModelFactory,GridSearchedBestModel, MetricInfoArtifact
from typing import List
from income.util.util import read_yaml_file,save_numpy_array_data, load_numpy_array_data, save_object, load_object
from income.entity.model_factory import evaluate_classification_model


class IncomeEstimatorModel:
    def __init__(self,preprocessing_object, trained_model_object):
            """
            TrainedModel constructor
            preprocessing_object: preprocessing_object
            trained_model_object: trained_model_object
            """
            self.preprocessing_object = preprocessing_object
            self.trained_model_object = trained_model_object

    def predict(self, X):
        """
        function accepts raw inputs and then transformed raw input using preprocessing_object
        which gurantees that the inputs are in the same format as the training data
        At last it perform prediction on transformed features
        """
        transfomed_feature = self.preprocessing_object.transform(X)
        return self.trained_model_object.predict(transfomed_feature).round()
    
    def __repr__(self) -> str:
        return f"{type(self.trained_model_object).__name__}()"
    
    def __str__(self) -> str:
        return f"{type(self.trained_model_object).__name__}()"


class ModelTrainer:

    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info(f"{'==' * 20}Model trainer log started.{'==' * 20} ")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise IncomeException(e,sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info(f"Loading transformed training dataset")
            transformed_train_file_path = self.data_transformation_artifact.tranformed_train_file_path
            train_array = load_numpy_array_data(file_path=transformed_train_file_path)
            
            logging.info(f"Loading transformed testing dataset")
            transformed_test_file_path = self.data_transformation_artifact.transformed_test_file_path
            test_array = load_numpy_array_data(file_path=transformed_test_file_path)

            logging.info(f"Splitting tarin & test array into input & target features")
            X_train,y_train,X_test,y_test = train_array[:,:-1],train_array[:,-1],test_array[:,:-1],test_array[:,-1]

            logging.info(f"Extracting model config info")
            model_config_file_path = self.model_trainer_config.model_config_file_path

            logging.info(f"Initalizing model factory class using above model config file: {model_config_file_path}")
            model_factory = ModelFactory(model_config_path=model_config_file_path)

            base_accuracy = self.model_trainer_config.base_accuracy
            logging.info(f"Expected base accuracy score : {base_accuracy}")

            logging.info(f"Initiating operation moddel selection")
            best_model = model_factory.get_best_model(X=X_train,y=y_train,base_accuracy=base_accuracy)

            logging.info(f"Besst model found on training dataset : {best_model} ")

            logging.info(f"Extracting trained model list")
            grid_searched_best_model_list:List[GridSearchedBestModel] = model_factory.grid_searched_best_model_list

            model_list = [model.best_model for model in grid_searched_best_model_list]
            logging.info(f"Evaluation all trained model on training and testing dataset both")

            metric_info: MetricInfoArtifact = evaluate_classification_model(model_list=model_list,
                                                                            X_train=X_train,y_train=y_train,
                                                                            X_test=X_test,y_test=y_test,
                                                                            base_accuracy=base_accuracy)
            
            logging.info(f"Best found model on both training and testing dataset.")
            preprocessing_obj = load_object(self.data_transformation_artifact.preprocessed_object_file_path)
            model_object = metric_info.model_object

            trained_model_file_path = self.model_trainer_config.trained_model_file_path
            income_model = IncomeEstimatorModel(preprocessing_object=preprocessing_obj, trained_model_object=model_object)
            logging.info(f"Saving model at path : [{trained_model_file_path}]")
            save_object(trained_model_file_path,obj = income_model)


            model_trainer_artifact = ModelTrainerArtifact(is_trained=True,
                                                          message=f"Model trained Successfully",
                                                          trained_model_file_path=trained_model_file_path,
                                                          train_accuracy=metric_info.train_accuracy,
                                                          test_accuracy=metric_info.test_accuracy,
                                                          model_accuracy=metric_info.model_accuracy)
            
            logging.info(f"Model Trainer Artifact : {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise IncomeException(e,sys) from e
        
    
    def __del__(self):
        logging.info(f"{'=='*20} Model Trainer log completed. {'=='*20} \n\n")
