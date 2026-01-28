#!/usr/bin/env python3
from flask import Flask, request, render_template_string, send_from_directory
import subprocess
import os

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>BSBF Installer</title>
</head>
<body>
    <h2>Submit Parameters</h2>
    <form method="post">
        TARGET: <input type="text" name="TARGET"><br><br>
        SUBTARGET: <input type="text" name="SUBTARGET"><br><br>
        PROFILE: <input type="text" name="PROFILE"><br><br>
        SPEED: <input type="text" name="SPEED"><br><br>
        SERVER: <input type="text" name="SERVER"><br><br>
        Optional arguments for bsbf-client-openwrt-imagebuilder-config-generator: <input type="text" name="ICG"><br><br>
        <input type="submit" value="Submit">
    </form>
    {% if output %}
    <h3>Script Output:</h3>
    <pre>{{ output }}</pre>
    {% endif %}
    {% if download_url %}
    <h3>Download Files:</h3>
    <a href="{{ download_url }}">Click here to browse generated images</a>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    download_url = None
    if request.method == "POST":
        target = request.form.get("TARGET", "")
        subtarget = request.form.get("SUBTARGET", "")
        profile = request.form.get("PROFILE", "")
        speed = request.form.get("SPEED", "")
        server = request.form.get("SERVER", "")
        icg = request.form.get("ICG", "")

        try:
            result = subprocess.run(
                ["/usr/sbin/bsbf-generate-openwrt-image",
                 target, subtarget, profile, speed, server, icg],
                capture_output=True, text=True, check=True
            )
            output = result.stdout

            # Construct path to generated files
            build_dir = f"./openwrt-imagebuilder-24.10.5-{target}-{subtarget}.Linux-x86_64/bin/targets/{target}/{subtarget}"
            if os.path.isdir(build_dir):
                # Provide a link to browse files
                download_url = f"/download/{target}/{subtarget}/"
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.stderr}"

    return render_template_string(HTML_FORM, output=output, download_url=download_url)

@app.route("/download/<target>/<subtarget>/")
def download(target, subtarget):
    build_dir = f"./openwrt-imagebuilder-24.10.5-{target}-{subtarget}.Linux-x86_64/bin/targets/{target}/{subtarget}"
    if not os.path.isdir(build_dir):
        return "No build directory found", 404
    files = os.listdir(build_dir)
    links = [f"<li><a href='/download/{target}/{subtarget}/{fname}'>{fname}</a></li>" for fname in files]
    return f"<h2>Available files</h2><ul>{''.join(links)}</ul>"

@app.route("/download/<target>/<subtarget>/<path:filename>")
def download_file(target, subtarget, filename):
    build_dir = f"./openwrt-imagebuilder-24.10.5-{target}-{subtarget}.Linux-x86_64/bin/targets/{target}/{subtarget}"
    return send_from_directory(build_dir, filename, as_attachment=True)
