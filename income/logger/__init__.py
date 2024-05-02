import logging
from datetime import datetime
import os
LOG_DIR=f"income_logs/{datetime.now().strftime('%Y_%m_%d')}"
from income.constant import get_current_time_stamp

LOG_FILE_NAME = f"log_{get_current_time_stamp()}.log"
import pandas as pd

os.makedirs(LOG_DIR,exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR,LOG_FILE_NAME)

logging.basicConfig(filename=LOG_FILE_PATH,
                    filemode='w',
                    format='[%(asctime)s]||%(name)s||%(levelname)s||%(message)s',
                    level=logging.INFO)

def get_log_dataframe(file_path):
    data=[]
    with open(file_path) as log_file:
        for line in log_file.readlines():
            data.append(line.split("^;"))

    log_df = pd.DataFrame(data)
    columns=["Time stamp","Log Level","line number","file name","function name","message"]
    log_df.columns=columns
    
    log_df["log_message"] = log_df['Time stamp'].astype(str) +":$"+ log_df["message"]

    return log_df[["log_message"]]