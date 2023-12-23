from flask import Flask, request, redirect, url_for, render_template

from analysis import get_chart

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/charts', methods=['POST'])
def charts():
    city = request.get_json().get('city')
    chart = request.get_json().get('chart')
    return get_chart(city, chart)


if __name__ == '__main__':
    app.run()
