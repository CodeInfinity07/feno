import json
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, make_response
# from flask_weasyprint import render_pdf, HTML

from flask_session import Session
import random
from analyse import analyse_messages
from emojisorden import get_emoji_list

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    error = request.args.get('error')
    return render_template('index.html',error=error)


@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('result.html')


@app.route('/analyse', methods=['POST'])
def analyse_data():
    try:
        input_file = request.files.get('input_file')
        if input_file and input_file.content_type != 'text/plain' and not input_file.filename.endswith('.txt'):
            return render_template('index.html', error='Invalid file type, please upload a text file.')

        bytes = input_file.stream.read()
        texto = bytes.decode('utf8')
        result = analyse_messages(texto)
        emojis_count = get_emoji_list(texto)[:609]
        total_sample = len(emojis_count) if len(emojis_count) < 300 else 300
        emojis_count = random.sample(emojis_count, total_sample)

        session['result'] = result
        session['emojis_count'] = emojis_count

        # emj_div = render_template('emoji.html', data=emojis_count)
        #
        #
        # if emj_div:
        #     return emj_div



        if result:
            return render_template('analyse.html', data=result, emojis_count=emojis_count)
        else:
            return redirect(url_for('index',error='Got Some Error, Please Try Again.'))
    except Exception as e:
        print(e)
        return redirect(url_for('index', error='Something went wrong, please try again.'))


@app.route('/analyse_ajax', methods=['POST'])
def analyse_ajax():
    try:
        input_file = request.files.get('input_file')
        if input_file and input_file.content_type != 'text/plain' and not input_file.filename.endswith('.txt'):
            return render_template('index.html', error='Invalid file type, please upload a text file.')

        bytes = input_file.stream.read()
        texto = bytes.decode('utf8')
        result = analyse_messages(texto)
        emojis_count = get_emoji_list(texto)[:609]
        total_sample = len(emojis_count) if len(emojis_count) < 300 else 300
        emojis_count = random.sample(emojis_count, total_sample)

        session['result'] = result
        session['emojis_count'] = emojis_count

        # emj_div = render_template('emoji.html', data=emojis_count)
        #
        #
        # if emj_div:
        #     return emj_div

        if result:
            return {'status':True,'result':result}
        else:
            return {'status':False,'result':None}
    except Exception as e:
        print(e)
        return {'status':False,'result':None}

# @app.route('/topdf', methods=['GET'])
# def topdf():
#     try:
#         result = session.get('result')
#         emojis_count = session.get('emojis_count')
#
#         if result:
#             html = render_template('analyse.html', data=result, emojis_count=emojis_count)
#             response = make_response(render_pdf(HTML(string=html)))
#             response.headers['Content-Disposition'] = 'attachment; filename=result.pdf'
#             return response
#         else:
#             return redirect(url_for('index',error='Got Some Error, Please Try Again.'))
#     except Exception as e:
#         print(e)




if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='192.168.0.104', port=5000)
