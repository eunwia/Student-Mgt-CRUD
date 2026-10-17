import sys
import os
sys.path.insert(0,"db/")
from db.dbhelper import *

from flask import Flask, render_template, request, redirect, url_for, flash

upload_folder = "static/images"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = "my_super_secret_123!"

app.config['MAX_FORM_MEMORY_SIZE'] = 50 * 1024 * 1024   # 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route("/savestudent", methods=['POST'])
def savestudent():
    if request.method == "POST":
        idno = request.form.get('idno')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        course = request.form.get('course')
        level = request.form.get('level')
        file = request.files.get('webcam')
        camera_data = request.form.get('cameraImage')


        # Save image if uploaded
        filename = None

        if file and file.filename != '':
            # Uploaded file
            filename = os.path.join(upload_folder, f"{lastname}.png")
            file.save(filename)

        elif camera_data and camera_data.startswith("data:image"):
            # Camera capture
            import base64
            img_data = camera_data.split(",")[1]
            img_bytes = base64.b64decode(img_data)

            filename = os.path.join(upload_folder, f"{lastname}.png")
            with open(filename, "wb") as f:
                f.write(img_bytes)


        # Check if student exists (edit)
        existing = getrecord('students', idno=idno)
        if existing:
            # Update existing student
            update_data = {
                'idno': idno,
                'lastname': lastname,
                'firstname': firstname,
                'course': course,
                'level': level
            }
            if filename:
                update_data['image'] = filename
            ok = updaterecord('students', **update_data)
            flash("Student updated successfully!" if ok else "Error updating student", "success" if ok else "error")
        else:
            # Add new student
            ok = addrecord('students', idno=idno, lastname=lastname, firstname=firstname,
                           course=course, level=level, image=filename if filename else "")
            flash("Student added successfully!" if ok else "Error adding student", "success" if ok else "error")

    return redirect(url_for('index'))


@app.route("/deleteuser")
def deleteuser():
    idno = request.args.get('id')
    if idno:
        ok = deleterecord('students', idno=idno)
        flash("Student deleted successfully!" if ok else "Error deleting student", "success" if ok else "error")
    else:
        flash("No ID provided", "error")
    return redirect(url_for('index'))


@app.route("/")
def index():
    students = getall("students")
    students = sorted(students, key=lambda s: s["idno"])
    return render_template("index.html", students=students)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
