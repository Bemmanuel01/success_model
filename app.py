import numpy as np
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for

from sklearn.preprocessing import StandardScaler
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

application = Flask(__name__)

app = application

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predictdata', methods = ['GET', 'POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    
    else:
        data = CustomData(
            gender = request.form.get('gender'),
            race_ethnicity = request.form.get('race_ethnicity'),
            parental_level_of_education = request.form.get('parental_level_of_education'),
            lunch = request.form.get('lunch'),
            test_preparation_course = request.form.get('test_preparation_course'),
            reading_score = float(request.form.get('reading_score')),
            writing_score = float(request.form.get('writing_score'))
        )
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        
        return redirect(url_for('result_page', prediction=results[0]))
    
    
@app.route('/result')
def result_page():
    prediction = request.args.get('prediction')
    return render_template('results.html', results=prediction)

@app.route('/about')
def about():
    return render_template('about.html', year=2025)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)