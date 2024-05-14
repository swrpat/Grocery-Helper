import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import detection
import extraction


UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'some_secret_key'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Detect files
            texts = detection.detect(filename, folder='static', debug=True)
            # Extract relevant texts
            result = extraction.parse(texts)
            filename_no_ext = filename.split('.')[0]
            # Write result to file
            with open('result/' + filename_no_ext, mode='w') as file:
                file.writelines(result)

            # Logging the uploading timestamp
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            with open('log.csv', mode='a') as file:
                file.write(f'{filename},{now_str}\n')

            return redirect(url_for('upload_file'))
    
    # Loading history of all uploaded file
    with open('log.csv', mode='r') as file:
        texts = file.readlines()
    logs = []
    for text in texts:
        entry = text.split(',')

        name = entry[0]
        name_noext = name.split('.')[0]
        entry.append(name_noext)
        logs.append(entry)


    return render_template('main.html', logs=logs[::-1])


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/result')
def get_result():
    name = request.args.get('name')
    if not name:
        return "File not found", 404
    name_no_ext = name.split(".")[0]
    result = ''
    with open('result/'+name_no_ext, mode='r') as file:
        result = file.readlines()

    return render_template('result.html', result=result, name=name+'.jpeg')



if __name__ == "__main__":
    app.run(debug=True)