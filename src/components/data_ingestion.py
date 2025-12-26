import sys
import os


from src.logger import logging
from src.exeption import CustomException

import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass

from src.components.data_transformation import DataTransformation
@dataclass
class DataIngestionConfig:
    train_data_path:str=os.path.join('artifacts',"train.csv")
    test_data_path:str=os.path.join('artifacts',"test.csv")
    raw_data_path:str=os.path.join('artifacts',"data.csv")
    source_data_path:str=os.path.join('Notebook','data','customer_churn.csv')
class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()

    def initiate_data_ingestion(self):

        logging.info("Data ingestion starting")

        try:
            df = pd.read_csv(self.ingestion_config.source_data_path)


            logging.info("read data as dataframe")

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)

            df.to_csv(self.ingestion_config.raw_data_path,index=False,header=True)
            
            logging.info("raw data saved")

            train_set , test_set = train_test_split(df,test_size=0.2,random_state=42,stratify=df['churn'])
            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)
            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)
            logging.info("ingestion of data is completed")

            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            logging.info("Exception occured in data ingestion stage")
            raise CustomException(e,sys)
        
if __name__=="__main__":
    obj = DataIngestion()
    train_data,test_data = obj.initiate_data_ingestion()

    data_transf=DataTransformation()
    train_array,test_array,_=data_transf.start_data_transformation(train_data,test_data)