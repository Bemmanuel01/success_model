import os
import sys

from src.exception import CustomException
from src.logger import logging

from catboost import CatBoostRegressor
from sklearn.ensemble import (AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor)
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score

from src.utils import save_object, evaluate_models
from dataclasses import dataclass

@dataclass
class ModelTrainerConfig:
    trained_model_path = os.path.join("artifacts", "model.pkl")
    
class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        
    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info("Split training and testing input data")
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1],                
            )
            
            models = {
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "K-Neighbor Regressor": KNeighborsRegressor(),
                "Decision Tree Regressor": DecisionTreeRegressor(),
                "Random Forest Regressor": RandomForestRegressor(),
                "XGB Regressor": XGBRegressor(),
                "Cat Boost Regressor": CatBoostRegressor(verbose = False),
                "AdaBoostRegressor": AdaBoostRegressor()
                
            }
            params = {
                "Decision Tree Regressor": {
                    'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'splitter': ['best', 'random'],
                    # 'max_features': ['sqrt', 'log2'],
                },
                "Random Forest Regressor": {
                    # 'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'max_features': ['sqrt', 'log2'],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                },
                "Gradient Boosting": {
                    # 'loss': ['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate': [.1, .01, .05, .001],
                    'subsample': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    # 'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'max_features': ['auto', 'sqrt', 'log2'],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                },
                "Linear Regression": {},
                "K-Neighbor Regressor": {
                    'n_neighbors': [5, 7, 9, 11],
                    # 'weight': ['uniform', 'distance'],
                    # 'algorithm': ['ball_tree', 'kd_tree', 'brute'],
                },
                'XGB Regressor': {
                    'learning_rate': [.1, .01, .05, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                },
                "Cat Boost Regressor": {
                    'learning_rate': [.1, .01, .05, .001],
                    # 'n_estimators': [8, 16, 32, 64, 128, 256],
                    'iterations': [30, 50, 100],
                },
                "AdaBoostRegressor": {
                    # 'depth': [6, 8, 10],
                    'learning_rate': [.1, .01, .05, .001],
                    # 'loss': ['linear', 'square', 'exponential'],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                }
            }
            
            model_report: dict = evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, param=params)
            
            ## Best Model
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            
            if best_model_score < 0.6:
                raise CustomException("No Best Model Found")
            logging.info(f"Best model found on both training and testing dataset")
            
            save_object(
                file_path=self.model_trainer_config.trained_model_path,
                obj = best_model
            )
            
            predicted = best_model.predict(X_test)
            score = r2_score(y_test, predicted)
            
            return score
        except Exception as e:
            raise CustomException(e, sys)
