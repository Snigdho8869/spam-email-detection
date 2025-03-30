from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_mail import Mail, Message
import smtplib
import tensorflow
import re
import nltk
import numpy as np
import pandas as pd
import joblib
import json
from nltk.tokenize import RegexpTokenizer
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from textblob import Word



app = Flask(__name__, template_folder='templates', static_folder='static')


model = joblib.load('spam_svm.pkl')
transformer = joblib.load('tfidf.pkl')



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/resources.html')
def resources():
    return render_template('resources.html')


@app.route('/spam-detector', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    text = data['text']
    
    text_df = pd.DataFrame({'text': [text]})
    text_df['text'] = text_df['text'].apply(lambda x: x.lower().strip().replace('\n', ' ').replace('\r', ' '))
    text_df['text'] = text_df['text'].str.replace(r'^.+@[^\.].*\.[a-z]{2,}$', 'emailaddress', regex=True)
    text_df['text'] = text_df['text'].str.replace(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$', 'webaddress', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'£|\$', 'moneysymb', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$','phonenumbr', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'\d+(\.\d+)?', 'numbr', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'[^\w\d\s]', ' ', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'\s+', ' ', regex=True)
    text_df['text'] =  text_df['text'].str.replace(r'^\s+|\s+?$', '', regex=True)
    stops = stopwords.words('english')
    text_df['text'] =  text_df['text'].apply(lambda x: ' '.join(term for term in x.split() if term not in stops))
    text_df['text'] = text_df['text'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

    text_vec = transformer.transform([text_df['text'][0]])
  
    prediction = model.predict(text_vec)
    prediction_list = prediction.tolist()
    response_dict = {'category': prediction_list}
    response_json = json.dumps(response_dict)
    response = app.response_class(response=response_json, status=200, mimetype='application/json')
    
    return response


@app.route('/send-email', methods=['POST'])
def send_email():

    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    subject = 'Contact Form Submission from ' + name
    body = 'Name: ' + name + '\nEmail: ' + email + '\nMessage: ' + message

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('zahidulislam2225@gmail.com', 'valb mmmn awhg snpd')
    
    server.sendmail('zahidulislam2225@gmail.com', 'rafin3600@gmail.com', subject + '\n\n' + body)
    server.quit()
    
    return render_template('thank-you.html')


if __name__ == '__main__':
    app.run(debug=True)