from flask import Flask, request, render_template
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    code = ""

    if request.method == "POST":
        code = request.form.get("code", "")  # Safer than request.form["code"]
        temp_filename = f"temp_{uuid.uuid4().hex}.brainrot"

        with open(temp_filename, "w") as f:
            f.write(code)

        try:
            output = subprocess.check_output(
                ["python", "main.py", temp_filename],
                stderr=subprocess.STDOUT,
                timeout=5
            ).decode()
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
        except subprocess.TimeoutExpired:
            output = "❌ Execution timed out."
        finally:
            os.remove(temp_filename)

    return render_template("index.html", code=code, output=output)

if __name__ == "__main__":
    # Run Flask server on port 8084
    app.run(host="127.0.0.1", port=8084, debug=True)
