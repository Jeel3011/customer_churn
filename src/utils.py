import os
import sys
import pandas as pd
import numpy as np
from src.exeption import CustomException
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import GridSearchCV

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        pd.to_pickle(obj, file_path)
    except Exception as e:
        raise CustomException(f"Error saving object: {e}", sys)

def load_object(file_path):
    try:
        obj = pd.read_pickle(file_path)
        return obj
    except Exception as e:
        raise CustomException(f"Error loading object: {e}", sys)