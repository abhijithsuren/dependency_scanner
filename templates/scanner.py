import requests
from flask import Flask , render_template, request

app = Flask(__name__)

#osvurl used to call the api; api endpoit.
OSV_URL = "https://api.osv.dev/v1/query"

#funciton used to parse file contents; dependencies.
def parse_file(file, file_type):
    dependencies = []

    lines = file.read().decode("utf-8")

    if file_type == "txt":
        for line in lines.splitlines():
            if "==" in line:
                name, version = line.strip().split("==")
                dependencies.append((name,version))

    elif file_type == "json":
        pass

    else:
        return []
    
    return dependencies

#function used to OSV api call
def scan_dependencies(dependencies):
    results = []

    for name, version in dependencies:
        payload = {
            "package": {
                "name": name,
                "ecosystem": "PyPI"
            },
            "version": version
        }
        try:
            osv_response = requests.post(OSV_URL, json=payload, timeout=10)
            if osv_response.status_code == 200:
                data = osv_response.json()
            else:
                data = {"vulns": [], "error":f"HTTP {osv_response.status_code}"}
        except requests.exceptions.RequestException as e:
            data = {"vulns": [], "error": str(e)}

        results.append({
            "name": name,
            "version": version,
            "vulns": data.get("vulns", []),
            "error": data.get("error")
        })
    return results


@app.route('/', methods=["GET", "POST"])
def index():
    report = None
    if request.method == "POST":
        file = request.files["file"]
        file_type = request.form["file_type"]
        if file:  
            dependencies = parse_file(file, file_type)
            report = scan_dependencies(dependencies)

    return render_template("index.html", report=report)



if __name__ == '__main__':
    app.run()