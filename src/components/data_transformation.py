import sys
import os 

from src.logger import logging
from src.exeption import CustomException
from src.utils import save_object

import pandas as pd
import numpy as np 

from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer




from dataclasses import dataclass


@dataclass
class DataTransformationConfig:
    target_column='churn'
    preprocessor_obj_file_path:str=os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_preprocessor(self,df):

        try:

            logging.info("data transformation started")

            target_col=self.data_transformation_config.target_column
            X = df.drop(columns=[target_col],axis=1)

            num_cols = X.select_dtypes(include=['int64','float64']).columns
            cat_cols = X.select_dtypes(include=['object']).columns

            num_pipe= Pipeline(
                steps=[
                    ('imputer',SimpleImputer(strategy='median')),
                    ('scaler',StandardScaler())
                ]
            )

            cat_pipe = Pipeline(
                steps=[
                    ('imputer',SimpleImputer(strategy='most_frequent')),
                    ('one_hot_encoder',OneHotEncoder(handle_unknown='ignore')),
                    
                ]
            )
            preprocessor = ColumnTransformer(
                [
                    ('num_pipe',num_pipe,num_cols),
                    ('cat_pipe',cat_pipe,cat_cols)
                ]
            )
            logging.info("preprocessor object created")

            return preprocessor
        
        except Exception as e:
            logging.info("Exception occured in data transformation stage")
            raise CustomException(e,sys)
        
    def start_data_transformation(self,train_path,test_path):
        try:
            logging.info("starting")

            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("reading completed")

            preprocessor_obj=self.get_preprocessor(train_df)

            target_col=self.data_transformation_config.target_column

            input_feature_train_df = train_df.drop(columns=[target_col],axis=1)
            target_feature_train_df = train_df[target_col]

            input_feature_test_df = test_df.drop(columns=[target_col],axis=1)
            target_feature_test_df = test_df[target_col]

            logging.info("preprocessing")

            input_train_arr = preprocessor_obj.fit_transform(input_feature_train_df)
            input_test_arr = preprocessor_obj.transform(input_feature_test_df)
            
            train_arr = np.c_[input_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_test_arr, np.array(target_feature_test_df)]

            logging.info("preprocessing completed") 

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessor_obj
            )

            logging.info("preprocessor saved as pkl file")
            return(train_arr,test_arr,self.data_transformation_config.preprocessor_obj_file_path)
        

        except Exception as e:
            logging.info("Exception occured in the data transformation stage")
            raise CustomException(e,sys)

    
