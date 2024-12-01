from flask import Flask, render_template, request
from script import genetic_algorithm

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    locations = {}
    index = 1
    truck_capacity = {
        "T1": ("Motor", 18, 48, 10000),
        "T2": ("Mobil Van", 54, 13.5, 10000),
        "T3": ("Mobil Pick-Up", 66, 13, 10000),
        "T4": ("Truck Cold Diesel", 112, 6, 13050)
    }

    # Tambahkan lokasi gudang sebagai default
    locations["G"] = (-6.390800, 106.724300, 0)  # Gudang

    while f"latitude-{index}" in request.form:
        latitude = float(request.form.get(f"latitude-{index}"))
        longitude = float(request.form.get(f"longitude-{index}"))
        demands = float(request.form.get(f"items-{index}"))
        locations[f"L{index}"] = (latitude, longitude, demands)
        index += 1
    
    # Jalankan algoritma genetika
    individual_best_vehicle = genetic_algorithm(locations, truck_capacity, population_size=20, generations=100)

    # Render ke template
    return render_template(
        'result.html', 
        locations=locations,
        individual_best_vehicle=individual_best_vehicle
    )

if __name__ == '__main__':
    app.run(debug=True)
