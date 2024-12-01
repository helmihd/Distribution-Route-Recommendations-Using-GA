import random
import math

# Fungsi untuk menghitung jarak antara dua koordinat dengan formula Haversine
def haversine(coord1, coord2):
    # Koordinat dalam bentuk (latitude, longitude)
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Radius bumi dalam kilometer
    R = 6371.0

    # Konversi latitude dan longitude dari derajat ke radian
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Rumus Haversine
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Hasil jarak dalam kilometer
    distance = R * c
    
    return distance

# Matriks jarak antar lokasi
def create_matrix_distance(locations):
    distance_matrix = {}
    for loc1, (lat1, lon1, _) in locations.items():
        distance_matrix[loc1] = {}
        for loc2, (lat2, lon2, _) in locations.items():
            if loc1 != loc2:
                distance_matrix[loc1][loc2] = haversine((lat1, lon1), (lat2, lon2))
            else:
                distance_matrix[loc1][loc2] = 0.0
    return distance_matrix

# Fungsi untuk membuat rute acak
def create_random_route(locations):
    location_keys = list(locations.keys())
    location_keys.remove("G")  # Hilangkan Gudang dari rute
    random.shuffle(location_keys)
    return location_keys

# Fungsi untuk membuat kromosom dari rute
def create_chromosome(locations, route, truck_capacity):
    chromosome = []
    current_load = truck_capacity
    current_location = "G"
    distance_matrix = create_matrix_distance(locations)

    for next_location in route:
        _, _, demand = locations[next_location]

        # Jika muatan melebihi kapasitas kendaraan
        if demand > truck_capacity:
            return None

        # Jika muatan cukup untuk drop
        if current_load >= demand:
            distance = distance_matrix[current_location][next_location]
            chromosome.append((current_location, next_location, distance, current_load - demand))
            current_load -= demand
            current_location = next_location
        else:
            # Jika muatan tidak cukup, kembali ke gudang
            distance_to_gudang = distance_matrix[current_location]["G"]
            current_load = truck_capacity  # Isi ulang kapasitas
            current_location = "G"
            chromosome.append((current_location, "G", distance_to_gudang, current_load))
            
            # Lanjutkan ke lokasi berikutnya
            distance = distance_matrix[current_location][next_location]
            chromosome.append((current_location, next_location, distance, current_load - demand))
            current_load -= demand
            current_location = next_location

    # Kembali ke gudang setelah selesai
    if current_location != "G":
        distance_to_gudang = distance_matrix[current_location]["G"]
        chromosome.append((current_location, "G", distance_to_gudang, current_load))
    
    return chromosome


# Fungsi untuk membuat populasi awal
def create_population(locations, population_size, truck_capacity):
    population = []
    for _ in range(population_size):
        random_route = create_random_route(locations)
        chromosome = create_chromosome(locations, random_route, truck_capacity)

        if chromosome is None:
            return None
        
        population.append(chromosome)
    
    return population

# Fungsi untuk melakukan mutasi pada rute
def mutate(chromosome, locations, truck_capacity):
    # Ekstrak rute dari kromosom (tanpa Gudang)
    route = [gene[1] for gene in chromosome if gene[1] != "G"]
    # Pertukaran dua lokasi di rute
    idx1, idx2 = random.sample(range(len(route)), 2)
    route[idx1], route[idx2] = route[idx2], route[idx1]
    # Buat ulang kromosom berdasarkan rute baru
    return create_chromosome(locations, route, truck_capacity)

# Fungsi untuk melakukan crossover pada dua kromosom
def crossover(parent1, parent2, locations, truck_capacity):
    size = len(parent1)
    point = random.randint(1, size - 2)
    
    # Ambil rute pelanggan dari kromosom (tanpa Gudang)
    parent1_route = [gene[1] for gene in parent1 if gene[1] != "G"]
    parent2_route = [gene[1] for gene in parent2 if gene[1] != "G"]

    # Lakukan crossover untuk membuat anak
    child_route1 = parent1_route[:point] + [loc for loc in parent2_route if loc not in parent1_route[:point]]
    child_route2 = parent2_route[:point] + [loc for loc in parent1_route if loc not in parent2_route[:point]]

    # Buat ulang kromosom anak berdasarkan rute hasil crossover
    child1 = create_chromosome(locations, child_route1, truck_capacity)
    child2 = create_chromosome(locations, child_route2, truck_capacity)

    return child1, child2

# Fungsi untuk menghitung fitness (1 / total jarak)
def calculate_fitness(chromosome):
    total_distance = sum(gene[2] for gene in chromosome)
    if total_distance == 0:
        return float('inf') 
    return 1 / total_distance

# Fungsi untuk melakukan seleksi dengan metode roulette wheel
def selection(population):
    # Hitung fitness untuk semua individu
    fitness_scores = [calculate_fitness(ind) for ind in population]
    total_fitness = sum(fitness_scores)

    # Normalisasi fitness menjadi probabilitas
    probabilities = [fitness / total_fitness for fitness in fitness_scores]

    # Pilih individu berdasarkan probabilitas (roulette wheel selection)
    selected_indices = random.choices(range(len(population)), weights=probabilities, k=len(population))

    # Kembalikan populasi hasil seleksi
    selected_population = [population[i] for i in selected_indices]
    return selected_population

# Fungsi untuk melakukan iterasi algoritma genetika
def genetic_algorithm(locations, truck_capacity, population_size, generations):
    individual_best_vehicle = []

    for vehicle, (vehicle_name, max_capacity, km_per_liter, price_per_liter) in truck_capacity.items():
        # Buat populasi awal
        population = create_population(locations, population_size, max_capacity)
        
        if population is None:
            continue

        for generation in range(1, generations + 1):
            # Hitung fitness
            fitness_scores = [calculate_fitness(ind) for ind in population]

            # Seleksi
            selected_population = selection(population)

            # Individu Baru
            next_generation = []

            # Crossover
            for i in range(0, len(selected_population) - 1, 2):
                parent1 = selected_population[i]
                parent2 = selected_population[i + 1]
                child1, child2 = crossover(parent1, parent2, locations, max_capacity)
                next_generation.extend([child1, child2])

            # Mutasi
            for i in range(len(selected_population)):
                if random.random() < 0.1:  # Probabilitas mutasi 10%
                    mutated_chromosome = mutate(selected_population[i], locations, max_capacity)
                    next_generation[i] = mutated_chromosome

            # Update populasi untuk generasi berikutnya
            population = next_generation[:population_size]

        # Hitung fitness untuk populasi akhir
        fitness_scores = [calculate_fitness(ind) for ind in population]

        # Temukan individu dengan fitness terbaik
        best_index = fitness_scores.index(max(fitness_scores))
        best_individual = population[best_index]
        best_fitness = fitness_scores[best_index]
        best_total_distance = sum(gene[2] for gene in best_individual)

        liters_needed = best_total_distance / km_per_liter
        cost = liters_needed * price_per_liter

        individual_best_vehicle.append((vehicle, vehicle_name, best_individual, best_fitness, best_total_distance, cost))

    # Kembalikan populasi akhir
    return individual_best_vehicle