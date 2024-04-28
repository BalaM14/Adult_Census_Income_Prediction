from collections import namedtuple


DataIngestionArtifact = namedtuple("DataIngestionArtifact",["is_ingested", "message", "train_file_path", "test_file_path"])

DataValidationArtifact = namedtuple("DataValidationArtifact",["is_validated","message","schema_file_path","report_file_path","report_page_file_path"])

DataTransformationArtifact = namedtuple("DataTransformationArtifact",["is_transfomred","message","tranformed_train_file_path","transformed_test_file_path","preprocessed_object_file_path"])

ModelTrainerArtifact = namedtuple("ModelTrainerArtifact",["is_trained","message","trained_model_file_path","train_accuracy","test_accuracy","model_accuracy"])