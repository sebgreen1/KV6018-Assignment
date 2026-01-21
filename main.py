import random
from math import sqrt
from container_instances import create_basic_instances, create_challenging_instances
from visualisation import visualise_packing
# Placement heuristic

def place_cylinders(order, cylinders, container):
    placed = []

    for idx in order:
        cyl = cylinders[idx]
        r = cyl.diameter / 2
        step = min(r, 1.0)
        placed_flag = False

        x = r
        while x <= container.width - r and not placed_flag:
            y = r
            while y <= container.depth - r and not placed_flag:
                collision = False
                for p in placed:
                    d = sqrt((x - p['x'])**2 + (y - p['y'])**2)
                    if d < r + p['r']:
                        collision = True
                        break
                if not collision:
                    placed.append({
                        'x': x,
                        'y': y,
                        'r': r,
                        'w': cyl.weight
                    })
                    placed_flag = True
                y += step
            x += step

        if not placed_flag:
            return None

    return placed

# Centre-of-mass repair operator

def repair_centre_of_mass(placed, container):
    total_weight = sum(c['w'] for c in placed)
    cx = sum(c['x'] * c['w'] for c in placed) / total_weight
    cy = sum(c['y'] * c['w'] for c in placed) / total_weight

    dx = (0.5 * container.width) - cx
    dy = (0.5 * container.depth) - cy

    # Compute safe shift limits
    dx_min = -min(c['x'] - c['r'] for c in placed)
    dx_max = min(container.width - (c['x'] + c['r']) for c in placed)
    dy_min = -min(c['y'] - c['r'] for c in placed)
    dy_max = min(container.depth - (c['y'] + c['r']) for c in placed)

    # Clamp the shift ONCE (not per cylinder)
    dx = max(dx_min, min(dx, dx_max))
    dy = max(dy_min, min(dy, dy_max))

    # Apply uniform shift
    for c in placed:
        c['x'] += dx
        c['y'] += dy

# Fitness evaluation

def fitness(order, cylinders, container):
    placed = place_cylinders(order, cylinders, container)
    if placed is None:
        return 10_000

    # Repair balance
    repair_centre_of_mass(placed, container)

    # Overlap and boundary checks
    for i in range(len(placed)):
        c = placed[i]
        if c['x'] - c['r'] < 0 or c['x'] + c['r'] > container.width:
            return 1
        if c['y'] - c['r'] < 0 or c['y'] + c['r'] > container.depth:
            return 1
        for j in range(i + 1, len(placed)):
            d = sqrt((c['x'] - placed[j]['x'])**2 +
                     (c['y'] - placed[j]['y'])**2)
            if d < c['r'] + placed[j]['r']:
                return 1

    # Centre-of-mass constraint
    total_weight = sum(c['w'] for c in placed)
    cx = sum(c['x'] * c['w'] for c in placed) / total_weight
    cy = sum(c['y'] * c['w'] for c in placed) / total_weight

    if not (0.2 * container.width <= cx <= 0.8 * container.width):
        return 1
    if not (0.2 * container.depth <= cy <= 0.8 * container.depth):
        return 1

    return 0

# Genetic operators

def tournament_selection(population, scores, k=3):
    selected = random.sample(list(zip(population, scores)), k)
    selected.sort(key=lambda x: x[1])
    return selected[0][0][:]

def crossover(p1, p2):
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    child = [None] * n
    child[a:b] = p1[a:b]
    fill = [x for x in p2 if x not in child]
    idx = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill[idx]
            idx += 1
    return child

def mutate(order, rate=0.1):
    if random.random() < rate:
        i, j = random.sample(range(len(order)), 2)
        order[i], order[j] = order[j], order[i]

# Genetic Algorithm

def genetic_algorithm(cylinders, container,
                      pop_size=30, generations=500, mutation_rate=0.15):

    n = len(cylinders)

    # Initial population (half random, half weight-aware)
    population = []
    for _ in range(pop_size // 2):
        perm = list(range(n))
        random.shuffle(perm)
        population.append(perm)
    for _ in range(pop_size // 2):
        perm = sorted(range(n), key=lambda i: -cylinders[i].weight)
        population.append(perm)

    best, best_score = None, float('inf')

    for gen in range(generations):
        scores = [fitness(ind, cylinders, container) for ind in population]

        for ind, s in zip(population, scores):
            if s < best_score:
                best, best_score = ind[:], s

        if best_score == 0:
            break

        new_population = []
        while len(new_population) < pop_size:
            p1 = tournament_selection(population, scores)
            p2 = tournament_selection(population, scores)
            child = crossover(p1, p2)
            mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

    return best, best_score

# Solve all reference instances

if __name__ == "__main__":
    instances = create_basic_instances() + create_challenging_instances()

    print("SOLUTIONS FOR REFERENCE INSTANCES")

    for inst in instances:
        order, score = genetic_algorithm(inst.cylinders, inst.container)
        print(f"\nInstance: {inst.name}")
        print("Best order:", order)
        print("Fitness:", score)

order, score = genetic_algorithm(inst.cylinders, inst.container)

placed = place_cylinders(order, inst.cylinders, inst.container)
repair_centre_of_mass(placed, inst.container)

visualise_packing(
    placed,
    inst.container,
    title=f"GA Solution – {inst.name} (Fitness = {score})"
)

for inst in instances:
    order, score = genetic_algorithm(inst.cylinders, inst.container)

    placed = place_cylinders(order, inst.cylinders, inst.container)
    repair_centre_of_mass(placed, inst.container)

    visualise_packing(
        placed,
        inst.container,
        title=f"{inst.name} – Fitness {score}"
    )

