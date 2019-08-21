from flask import (Flask, request, abort, session, flash,
    redirect, render_template, url_for, make_response, jsonify)

from werkzeug.utils import secure_filename
import datetime
import os
import time

app = Flask(__name__)
app.secret_key = '6^74$sjxisA62Tfa'

### FILE UPLOADS PARAMETERS
# UPLOAD FOLDER will have to change based on your own needs/deployment scenario
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = os.path.join(BASE_DIR, './uploads')
UPLOAD_FOLDER = '/home/pi/Videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['mp4', 'MP4', 'MOV', 'jpg', 'jpeg', 'gif'])

@app.route('/')
def index():
    token = session.get('auth_token')
    if token:
        return render_template('main.html')
    else:
        abort(401, 'The request requires token authentication.  Please contact sysadmin for details.')

@app.route('/login/<token>')
def login(token):
    """set up the session token"""
    session['auth_token'] = token
    return 'token accepted'

@app.route('/logout')
def logout():
    session.pop('auth_token')
    return 'logged out'



@app.route('/_delete', methods=['POST'])
def file_delete():
    """handle file deletion from form"""
    items = request.form
    for item in items:
        pathname = os.path.join(app.config['UPLOAD_FOLDER'], item)
        if os.path.isfile(pathname):
            os.remove(pathname)
            flash('deleted {}'.format(item))
    return redirect(url_for('file_view'))

@app.route('/_stop')
def stop_video():
    """stop the video stream"""
    print("STOP VIDEO")
    # kill the videoplayer scripts
    os.system('kill -9 `pgrep videoplayer.sh`')
    os.system('kill -9 `pgrep omxplayer`')
    return redirect(url_for('index'))

@app.route('/_restart')
def restart_video():
    """restart the video stream"""
    print("RESTART VIDEO")
    # kill the videoplayer scripts
    os.system('kill -9 `pgrep videoplayer.sh`')
    os.system('kill -9 `pgrep omxplayer`')
    time.sleep(2)
    # start the videoplayer
    os.system('~/videoplayer.sh &')
    return redirect(url_for('index'))


def allowed_file(filename):
  """return True if filename is allowed for upload, False if not allowed"""
  return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """save the file to the proper location, rename if necessary"""

    # sanitize the filename
    filename = secure_filename(file.filename)
    pathname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # handle name collision if needed
    # filename will add integers at beginning of filename in dotted fashion
    # hello.jpg => 1.hello.jpg => 2.hello.jpg => ...
    # until it finds an unused name
    i=1
    while os.path.isfile(pathname):
        parts = filename.split('.')
        parts.insert(0,'copy')

        filename = '.'.join(parts)
        i += 1
        if i > 100:
            # probably under attack, so just fail
            raise ValueError("too many filename collisions, administrator should check this out")
    
        pathname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # ensure directory where we are storing exists, and create it
        directory = app.config['UPLOAD_FOLDER']
        if not os.path.exists(directory):
            os.makedirs(directory)
        # finally, save the file AND create its resource object in database
        file.save(pathname)
        return True
    except:
        flash("The upload failed")
        return False

@app.route('/files')
def file_view():
    """render the file upload form"""
    session['no_csrf'] = True
    file_list = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return render_template('files.html', file_list=file_list)

@app.route("/upload-video", methods=["GET", "POST"])
def upload_video():
    """render upload page and upload file"""
    if request.method == "POST":

        file = request.files["file"]

        print("File uploaded")
        print(file)
        save_file(file)

        res = make_response(jsonify({"message": "File uploaded"}), 200)

        return res

    return render_template("upload_video.html")

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
