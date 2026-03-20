import requests, json
from flask import Flask , render_template, request

app = Flask(__name__)

#osvurl used to call the api; api endpoit.
OSV_URL = "https://api.osv.dev/v1/query"

#file size limit
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

#funciton used to parse file contents; dependencies.
def parse_file(file, file_type):
    dependencies = []
    error = None
    try:
        lines = file.read().decode("utf-8")
        if file_type == "txt":
            for line in lines.splitlines():
                if "==" in line:
                    try:
                        name, version = line.strip().split("==")
                        dependencies.append((name,version))
                    except ValueError:
                        continue #skip the invalid lines in dependency file

        elif file_type == "json":
            try:
                data = json.loads(lines)

                # standard package.json structure
                dependencies_json = data.get("dependencies", {})

                for name, version in dependencies_json.items():
                    # clean versions like "^1.2.3", "~2.0.0"
                    clean_version = version.strip("^~><= ")
                    dependencies.append((name, clean_version))

            except json.JSONDecodeError:
                error = "Invalid JSON format"

        else:
            error = "Unsupported file type"
    except UnicodeDecodeError:
        error = "File decoding failed (not UTF-8)"
    except Exception as e:
        error = str(e)
    
    return dependencies, error

#function used to OSV api call
def scan_dependencies(dependencies, ecosystem):
    results = []
    for name, version in dependencies:
        payload = {
            "package": {
                "name": name,
                "ecosystem": ecosystem
            },
            "version": version
        }
        try:
            osv_response = requests.post(OSV_URL, json=payload, timeout=10)
            if osv_response.status_code == 200:
                try:
                    data = osv_response.json()
                except ValueError:
                    data = {"vulns": [], "error": "Invalid JSON response"}
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
            dependencies, error = parse_file(file, file_type)
            
            if error:
                return render_template("index.html", report=None, error=error)
            
            #ecosytem 
            if file_type == "txt":
                ecosystem = "PyPI"
            else:
                ecosystem = "npm"
            
            report = scan_dependencies(dependencies, ecosystem)

    return render_template("index.html", report=report)



if __name__ == '__main__':
    app.run()