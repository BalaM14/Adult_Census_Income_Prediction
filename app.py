import os,sys,pip,json
import pandas as pd
from matplotlib.style import context
from flask import Flask,request,send_file,abort,render_template,url_for

from income.logger import logging, get_log_dataframe
from income.exception import IncomeException
from income.config.configuration import Configuration
from income.constant import *
from income.pipeline.pipeline import Pipeline
from income.util.util import read_yaml_file,write_yaml_file
from income.entity.income_predictor import IncomeData,IncomePredictor




ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "income_logs"
PIPELINE_FOLDER_NAME = "income"
SAVED_MODELS_DIR_NAME = "saved_models"
BATCH_DATA = 'adult.csv'
MODEL_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, "model.yaml")
LOG_DIR = os.path.join(ROOT_DIR,LOG_FOLDER_NAME)
PIPELINE_DIR = os.path.join(ROOT_DIR,PIPELINE_FOLDER_NAME)
MODEL_DIR = os.path.join(ROOT_DIR,SAVED_MODELS_DIR_NAME)

INCOME_DATA_KEY = "income_data"
PREDICTION_VALUE_KEY = "salary"


app=Flask(__name__)


@app.route('/artifact', defaults={'req_path': 'income'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    try:
        os.makedirs("income", exist_ok=True)
        # Joining the base and the requested path
        print(f"req_path: {req_path}")
        abs_path = os.path.join(req_path)
        print(abs_path)
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            if ".html" in abs_path:
                with open(abs_path, "r", encoding="utf-8") as file:
                    content = ''
                    for line in file.readlines():
                        content = f"{content}{line}"
                    return content
            return send_file(abs_path)

        # Show directory contents
        files = {os.path.join(abs_path, file_name): file_name for file_name in os.listdir(abs_path) if
                 "artifact" in os.path.join(abs_path, file_name)}

        result = {
            "files": files,
            "parent_folder": os.path.dirname(abs_path),
            "parent_label": abs_path
        }
        return render_template('files.html', result=result)
    
    except Exception as e:
        raise IncomeException(e,sys) from e


@app.route('/', methods=['GET', 'POST'])
def index():
        try:
            return render_template('index.html')
        except Exception as e:
            return str(e)


@app.route('/view_experiment_hist', methods=['GET', 'POST'])
def view_experiment_history():
    try:
        experiment_df = Pipeline.get_experiments_status()
        context = {
            "experiment": experiment_df.to_html(classes='table table-striped col-12')
        }
        return render_template('experiment_history.html', context=context)
    
    except Exception as e:
        raise IncomeException(e,sys) from e


@app.route('/train', methods=['GET', 'POST'])
def train():
    try:
        message = ""
        pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
        if not Pipeline.experiment.running_status:
            message = "Training started."
            pipeline.start()
        else:
            message = "Training is already in progress."
        context = {
            "experiment": pipeline.get_experiments_status().to_html(classes='table table-striped col-12'),
            "message": message
        }
        return render_template('train.html', context=context)
    
    except Exception as e:
        raise IncomeException(e,sys) from e


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    try:
       
        context = {
        INCOME_DATA_KEY: None,
        PREDICTION_VALUE_KEY: None
    }

        if request.method == 'POST':
            age = int(request.form['age'])
            workclass = str(request.form['workclass'])
            fnlwgt = int(request.form['fnlwgt'])
            education = str(request.form['education'])
            education_num = int(request.form['education_num'])
            marital_status = str(request.form['marital_status'])
            occupation = str(request.form['occupation'])
            relationship = str(request.form['relationship'])
            race = str(request.form['race'])
            sex = str(request.form['sex'])
            capital_gain = int(request.form['capital_gain'])
            capital_loss = int(request.form['capital_loss'])
            hours_per_week = int(request.form['hours_per_week'])
            country = str(request.form['country'])

            print(age,workclass,fnlwgt,education,education_num,marital_status,occupation,relationship,race,sex,capital_gain,capital_loss,hours_per_week,country)
            income_data = IncomeData(age=age,
            workclass = workclass,fnlwgt = fnlwgt,education = education,education_num = education_num,marital_status = marital_status,
            occupation = occupation,relationship = relationship,race = race,sex = sex,capital_gain = capital_gain,
            capital_loss = capital_loss,hours_per_week = hours_per_week,country=country)
            income_df = income_data.get_income_input_data_frame()
            income_predictor = IncomePredictor(model_dir=MODEL_DIR)
            output = int(income_predictor.predict(X=income_df))
            if output == 0:
                prediction_value = "<=50K"
            else:
                prediction_value = ">50K"
            context = {
            INCOME_DATA_KEY: income_data.get_income_data_as_dict(),
            PREDICTION_VALUE_KEY: prediction_value
            }
            return render_template('predict.html', context=context)
        return render_template("predict.html", context=context)
    
    except Exception as e:
            raise IncomeException(e, sys) from e

@app.route('/saved_models', defaults={'req_path': 'saved_models'})
@app.route('/saved_models/<path:req_path>')
def saved_models_dir(req_path):
    try:
        os.makedirs("saved_models", exist_ok=True)
        # Joining the base and the requested path
        print(f"req_path: {req_path}")
        abs_path = os.path.join(req_path)
        print(abs_path)
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            return send_file(abs_path)

        # Show directory contents
        files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

        result = {
            "files": files,
            "parent_folder": os.path.dirname(abs_path),
            "parent_label": abs_path
        }
        return render_template('saved_models_files.html', result=result)
    
    except Exception as e:
        raise IncomeException(e,sys) from e


@app.route("/update_model_config", methods=['GET', 'POST'])
def update_model_config():
    try:
        if request.method == 'POST':
            model_config = request.form['new_model_config']
            model_config = model_config.replace("'", '"')
            print(model_config)
            model_config = json.loads(model_config)

            write_yaml_file(file_path=MODEL_CONFIG_FILE_PATH, data=model_config)

        model_config = read_yaml_file(file_path=MODEL_CONFIG_FILE_PATH)
        return render_template('update_model.html', result={"model_config": model_config})

    except  Exception as e:
        logging.exception(e)
        return str(e)


@app.route(f'/income_logs', defaults={'req_path': 'income_logs'})
@app.route('/income_logs/<path:req_path>')
def render_log_dir(req_path):
    try:
        os.makedirs("income_logs", exist_ok=True)
        # Joining the base and the requested path
        print(f"req_path: {req_path}")
        abs_path = os.path.join(req_path)
        print(abs_path)
        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            log_df = get_log_dataframe(abs_path)
            context = {"log": log_df.to_html(classes="table-striped", index=False)}
            return render_template('log.html', context=context)

        # Show directory contents
        files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

        result = {
            "files": files,
            "parent_folder": os.path.dirname(abs_path),
            "parent_label": abs_path
        }
        return render_template('income_log_files.html', result=result)
    
    except Exception as e:
        raise IncomeException(e,sys) from e



if __name__ == "__main__":
    app.run(debug=True)



"""
@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():
    try:
        log_count = 0
        trained_count = 0
        for root_dir, cur_dir, files  in os.walk(LOG_FOLDER_NAME):
            log_count += len(files)
        
        for root_dir, cur_dir, files in os.walk(SAVED_MODELS_DIR_NAME):
            trained_count += len(files)
        return render_template('dashboard.html', dashboard=True, log_count=log_count, trained_count=trained_count)
    except Exception as e:
        income = IncomeException(e,sys)
        logging.info(income.error_message)

@app.route("/",methods=['GET','POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        income = IncomeException(e,sys)
        logging.info(income.error_message)


@app.route("/train",methods = ['GET','POST'])
def train():
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    context = {"experiment" : Pipeline.get_experiments_status().to_html(classes='table table-striped col-12')}
    return render_template('train.html', context=context)


@app.route("/initiate_train",methods = ['GET','POST'])
def initiate_train():
    message = ""
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    if not Pipeline.experiment.running_status:
        print("NOT",Pipeline.experiment.running_status)
        message = "Training started successfully"
        pipeline.start()
    else:
        print("Progress STATUS ", Pipeline.experiment.running_status)
        message = "Training is already in progress"
    
    context = {"experiment": pipeline.get_experiments_status().to_html(classes = 'table table-striped col-12'),
               "message": message,
               "status": Pipeline.experiment.running_status}
    return render_template('initiate_training.html', context=context)



@app.route('/predict', methods=['GET', 'POST'])
def predict():
    try:
       
        context = {
        INCOME_DATA_KEY: None,
        PREDICTION_VALUE_KEY: None
    }

        if request.method == 'POST':
            age = int(request.form['age'])
            workclass = str(request.form['workclass'])
            fnlwgt = int(request.form['fnlwgt'])
            education = str(request.form['education'])
            education_num = int(request.form['education_num'])
            marital_status = str(request.form['marital_status'])
            workingday = str(request.form['workingday'])
            occupation = str(request.form['occupation'])
            relationship = str(request.form['relationship'])
            race = str(request.form['race'])
            sex = str(request.form['sex'])
            capital_gain = int(request.form['capital_gain'])
            capital_loss = int(request.form['capital_loss'])
            hours_per_week = int(request.form['hours_per_week'])
            country = str(request.form['country'])

            print(age,workclass,fnlwgt,education,education_num,marital_status,workingday,occupation,relationship,race,sex,capital_gain,capital_loss,hours_per_week,country)
            income_data = IncomeData(age=age,
            workclass = workclass,fnlwgt = fnlwgt,education = education,education_num = education_num,marital_status = marital_status,
            workingday = workingday,occupation = occupation,relationship = relationship,race = race,sex = sex,capital_gain = capital_gain,
            capital_loss = capital_loss,hours_per_week = hours_per_week,country=country)
            income_df = income_data.get_income_input_data_frame()
            income_predictor = IncomePredictor(model_dir=MODEL_DIR)
            prediction_value = income_predictor.predict(X=income_df)
            context = {
            INCOME_DATA_KEY: income_data.get_income_data_as_dict(),
            PREDICTION_VALUE_KEY: int(prediction_value),
            }
            return render_template('predict.html', context=context)
        return render_template("predict.html", context=context)
    
    except Exception as e:
            raise IncomeException(e, sys) from e


@app.route('/batch_predict')
def batch_predict():
    try:
        batch_data_path = os.path.join(ROOT_DIR,BATCH_DATA)
        df = pd.read_csv(batch_data_path)
        income_predictor = IncomePredictor(model_dir=MODEL_DIR)
        batch_prediction = income_predictor.predict(df)
        df.to_html("batch_prediction.html")
        return render_template('batch.html',data=batch_prediction)
    except Exception as e:
            raise IncomeException(e, sys) from e


@app.route('/view_experiment_hist', methods=['GET', 'POST'])
def view_experiment_history():
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    experiment_df = pipeline.get_experiments_status()
    context = {
        "experiment": experiment_df.to_html(classes='table table-striped col-12')
    }
    return render_template('experiment_history.html', context=context)


@app.route(f'/logs', defaults={'req_path': f'{LOG_FOLDER_NAME}'})
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')
def render_log_dir(req_path):
    os.makedirs(LOG_FOLDER_NAME, exist_ok=True)
    # Joining the base and the requested path
    logging.info(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        log_df = get_log_dataframe(abs_path)
        context = {"log": log_df.to_html(classes="table-striped", index=False)}
        return render_template('log.html', context=context,dashboard=False)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('log_files.html', result=result, dashboard=False)


@app.route('/saved_models', defaults={'req_path': 'saved_models'})
@app.route('/saved_models/<path:req_path>')
def saved_models_dir(req_path):
    os.makedirs("saved_models", exist_ok=True)
    # Joining the base and the requested path
    abs_path = os.path.join(req_path)
    # Return 404 if path doesn't exist

    if not os.path.exists(abs_path):
        return abort(404) 

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('saved_models_files.html', result=result)


@app.route('/artifact', defaults={'req_path': 'sharing'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    os.makedirs("income", exist_ok=True)
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print("abs_path",abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        if ".html" in abs_path:
            with open(abs_path, "r", encoding="utf-8") as file:
                content = ''
                for line in file.readlines():
                    content = f"{content}{line}"
                return content
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file_name): file_name for file_name in os.listdir(abs_path) if
             "artifact" in os.path.join(abs_path, file_name)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('files.html', result=result)


@app.route('/reports')
def reports():
    return render_template('reports.html')

"""