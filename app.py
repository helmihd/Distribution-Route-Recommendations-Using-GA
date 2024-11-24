from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    # Ambil data dari form
    locations = []
    index = 0
    while f"latitude-{index}" in request.form:
        latitude = request.form.get(f"latitude-{index}")
        longitude = request.form.get(f"longitude-{index}")
        items = request.form.get(f"items-{index}")
        locations.append({
            "latitude": latitude,
            "longitude": longitude,
            "items": items
        })
        index += 1
    
    # Render ke template result.html dengan data yang diinputkan
    return render_template('result.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
