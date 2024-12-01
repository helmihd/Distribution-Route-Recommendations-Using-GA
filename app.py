from flask import Flask, render_template, request
from script import genetic_algorithm
import folium
from folium.plugins import AntPath


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
    locations["G"] = (-7.547778, 110.864367, 0)  # Gudang

    while f"latitude-{index}" in request.form:
        latitude = float(request.form.get(f"latitude-{index}"))
        longitude = float(request.form.get(f"longitude-{index}"))
        demands = float(request.form.get(f"items-{index}"))
        locations[f"L{index}"] = (latitude, longitude, demands)
        index += 1
    
    # Jalankan algoritma genetika
    individual_best_vehicle = genetic_algorithm(locations, truck_capacity, population_size=20, generations=100)

    # Function to generate a map for the vehicle's route
    def generate_map(vehicle_data, locations):
        start_location = locations[vehicle_data[2][0][0]]  # First 'from' location
        m = folium.Map(location=[start_location[0], start_location[1]], zoom_start=12)

        for gene in vehicle_data[2]:
            from_location = locations[gene[0]]
            to_location = locations[gene[1]]
            
            folium.Marker(
                location=[from_location[0], from_location[1]],
                popup=f"From: {gene[0]}",
                icon=folium.Icon(color='blue')
            ).add_to(m)
            
            folium.Marker(
                location=[to_location[0], to_location[1]],
                popup=f"To: {gene[1]}",
                icon=folium.Icon(color='red')
            ).add_to(m)

            # Add a Polyline with an arrow at the end using AntPath for animated path
            AntPath(
                locations=[[from_location[0], from_location[1]], [to_location[0], to_location[1]]],
                color='green',
                weight=3,
                opacity=0.8
            ).add_to(m)
        
        map_filename = f"static/vehicle_map_{vehicle_data[0]}.html"
        m.save(map_filename)
        return map_filename

    # Generate map filenames for each vehicle
    map_filenames = {}
    for vehicle_data in individual_best_vehicle:
        map_filenames[vehicle_data[0]] = generate_map(vehicle_data, locations)

    return render_template(
        'result.html', 
        locations=locations,
        individual_best_vehicle=individual_best_vehicle,
        map_filenames=map_filenames
    )

if __name__ == '__main__':
    app.run(debug=True)
