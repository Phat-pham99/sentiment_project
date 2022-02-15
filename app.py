from flask import Flask, render_template, request
from crawling import crawling_data
from predict import prediction_data

app = Flask(__name__)
@app.route('/', methods=['GET'])
def Home():
    return render_template('home.html')

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        word = request.form['word']
        data = crawling_data(word)
        y_pred = prediction_data(data)
    cf1 = y_pred
    return render_template('index.html', prediction_text=cf1)
if __name__=="__main__":
    app.run(debug=True)


