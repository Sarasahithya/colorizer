from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from colorize import colorize_image
from PIL import Image

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
OUTPUT_FOLDER = os.path.join(app.static_folder, "output")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def is_allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file selected", 400

        filename = secure_filename(file.filename)
        if not is_allowed_file(filename):
            return "Unsupported file type", 400

        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        restore_faces = request.form.get("restore") == "on"

        base, ext = os.path.splitext(filename)
        output_filename = f"{base}_colorized{ext.lower()}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        if not os.path.exists(output_path):
            colorize_image(input_path, output_path, restore_faces)

        resize_width = request.form.get("resize_width")
        resize_height = request.form.get("resize_height")
        try:
            if resize_width and resize_height:
                with Image.open(output_path) as img:
                    resized_img = img.resize((int(resize_width), int(resize_height)))
                    resized_img.save(output_path)
        except Exception as e:
            print(f"Resize error: {e}")
            return f"Resize error: {e}", 500

        return redirect(url_for("result", filename=filename))

    return render_template("index.html")

@app.route("/result/<filename>")
def result(filename):
    base_name, ext = os.path.splitext(filename)
    colorized_filename = f"{base_name}_colorized{ext}"
    return render_template(
        "result.html",
        original_image=f"uploads/{filename}",
        colorized_image=f"output/{colorized_filename}",
    )

@app.route("/history")
def history():
    uploaded_images = sorted(os.listdir(UPLOAD_FOLDER))
    colorized_images = sorted(os.listdir(OUTPUT_FOLDER))
    return render_template(
        "history.html",
        uploaded_images=uploaded_images,
        colorized_images=colorized_images,
    )

@app.route("/clear_uploads")
def clear_uploads():
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    return redirect(url_for("history"))

if __name__ == "__main__":
    app.run(debug=True)
