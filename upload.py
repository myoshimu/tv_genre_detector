__author__ = ('kmiki@google.com (Miki Katsuragi)')

import os
from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import pandas as pd
import StringIO
from apiclient import sample_tools
from oauth2client import client
import MeCab

mt = MeCab.Tagger("-Owakati")
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'pdf'])

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('base.html', title='flask test') 
    #return '''
    #<!doctype html>
    #<title>Upload new File</title>
    #<h1>Upload new File</h1>
    #<form action="" method=post enctype=multipart/form-data>
    #  <p><input type=file name=file>
    #     <input type=submit value=Upload>
    #</form>
    #'''


def pred(filename):

    args = ["kmiki/master.txt" "genre-identifier" "starlit-granite-545"]
    service, flags = sample_tools.init(
        args, 'prediction', 'v1.6', __doc__, __file__,
        scope=(
            'https://www.googleapis.com/auth/prediction',
            'https://www.googleapis.com/auth/devstorage.read_only'))
    try:
        # Get access to the Prediction API.
        papi = service.trainedmodels()
        tv = pd.read_csv(filename)
        master = pd.read_csv('master.csv')
        # Generate genre from master file.
        df=pd.merge(tv,master,on='Program',how='left')

        for index,row in df.iterrows():
            #Predict if the genre is nan
            if row.Genre != row.Genre:
                sample_text=mt.parse(row.Program)
                body = {'input': {'csvInstance': [sample_text]}}
                result = papi.predict(body=body, id="genre-identifier", project="starlit-granite-545").execute()
                genre="".join(result["outputLabel"])
                df.loc[index,'Genre'] = genre
        return df

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize.')


@app.route('/<filename>')
def uploaded_file(filename):
    output = StringIO.StringIO()
    df = pred(filename)
    df.to_csv(output,index=False)
#    return send_from_directory(UPLOAD_FOLDER, filename)
    return Response(output.getvalue(), mimetype="text/csv")


if __name__ == '__main__':
    app.run(debug=True, port=8000)
