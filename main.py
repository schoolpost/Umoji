from flask import Flask
from flask import request, render_template, redirect, url_for, send_from_directory
import os
import glob
from werkzeug import secure_filename
from detect import create_umoji
import uuid


app = Flask(__name__, static_url_path='',
            static_folder='static')

UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello():
    return render_template("index.html")


@app.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file'].read()
        result = create_umoji(f, debug=False)
        files = glob.glob(UPLOAD_FOLDER + "/*")
        for fi in files:
            os.remove(fi)
        img_key = str(uuid.uuid4())
        result.save(os.path.join(UPLOAD_FOLDER, img_key + ".png"))
        return img_key
        # return redirect(url_for("download_file", filename=img_key+".png"))


if __name__ == "__main__":
    app.run(debug=True)
