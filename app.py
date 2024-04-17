from flask import Flask
from income.logger import logging
from income.exception import IncomeException
import sys
app=Flask(__name__)

@app.route("/",methods=['GET','POST'])
def index():
    try:
        raise Exception("we are testing custom exception")
    except Exception as e:
        income = IncomeException(e,sys)
        logging.info(income.error_message)
        logging.info("Testing the logging module")

    return "Hey Bala"

if __name__=="__main__":
    app.run()