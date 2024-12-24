from flask import Flask, render_template, request, jsonify
from zap_scanner import ZAPScanner  # Importing the ZAP scanning logic

app = Flask(__name__)

# Initialize the ZAP Scanner without an API key
zap_scanner = ZAPScanner(zap_url="http://localhost:8080")  # Replace with your ZAP instance URL if needed

@app.route('/')
def index():
    return render_template('index.html')  # Main homepage

# Route for the login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile_dynamic.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        print(f"Message from {name} ({email}): {subject} - {message}")
    return render_template('contact.html')  # Separate contact page

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        # Retrieve form data
        url = request.form['url']
        scan_type = request.form['scan_type']
        max_depth = int(request.form.get('depth', 100))

        # Perform scan based on the selected scan type
        if scan_type == 'spider':
            result = zap_scanner.spider_scan(url, max_depth)
        elif scan_type == 'active':
            result = zap_scanner.active_scan(url)
        elif scan_type == 'comprehensive':
            result = zap_scanner.comprehensive_scan(url)
        else:
            result = {"error": "Invalid scan type selected"}

        # Render the results.html page with the scan results
        return render_template('results.html', url=url, scan_type=scan_type, result=result)

    # Render the scanning.html page for GET requests
    return render_template('scanning.html')

@app.route('/scan_progress', methods=['GET'])
def scan_progress():
    """
    Check the progress of the current scan.
    """
    # Retrieve scan ID and scan type from query parameters
    scan_id = request.args.get('scan_id')
    scan_type = request.args.get('scan_type')

    # Check progress based on scan type
    if scan_type == 'spider':
        progress = zap_scanner.check_spider_progress(scan_id)
    elif scan_type == 'active':
        progress = zap_scanner.check_active_progress(scan_id)
    else:
        progress = {"error": "Invalid scan type provided"}

    # Return progress data as JSON
    return jsonify(progress)


if __name__ == '__main__':
    app.run(debug=True)
