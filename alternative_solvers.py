import random
from math import sqrt
from container_instances import create_basic_instances, create_challenging_instances
from visualisation import visualise_packing
# Shared placement and repair utilities (same as GA)

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
                    placed.append({'x': x, 'y': y, 'r': r, 'w': cyl.weight})
                    placed_flag = True
                y += step
            x += step

        if not placed_flag:
            return None

    return placed


def repair_centre_of_mass(placed, container):
    total_weight = sum(c['w'] for c in placed)
    cx = sum(c['x'] * c['w'] for c in placed) / total_weight
    cy = sum(c['y'] * c['w'] for c in placed) / total_weight

    dx = (0.5 * container.width) - cx
    dy = (0.5 * container.depth) - cy

    dx_min = -min(c['x'] - c['r'] for c in placed)
    dx_max = min(container.width - (c['x'] + c['r']) for c in placed)
    dy_min = -min(c['y'] - c['r'] for c in placed)
    dy_max = min(container.depth - (c['y'] + c['r']) for c in placed)

    dx = max(dx_min, min(dx, dx_max))
    dy = max(dy_min, min(dy, dy_max))

    for c in placed:
        c['x'] += dx
        c['y'] += dy


def fitness(placed, container):
    total_weight = sum(c['w'] for c in placed)
    cx = sum(c['x'] * c['w'] for c in placed) / total_weight
    cy = sum(c['y'] * c['w'] for c in placed) / total_weight

    if not (0.2 * container.width <= cx <= 0.8 * container.width):
        return 1
    if not (0.2 * container.depth <= cy <= 0.8 * container.depth):
        return 1

    return 0

# Algorithm 1: Greedy Heuristic

def greedy_solver(instance):
    order = sorted(range(len(instance.cylinders)),
                   key=lambda i: -instance.cylinders[i].weight)

    placed = place_cylinders(order, instance.cylinders, instance.container)
    repair_centre_of_mass(placed, instance.container)
    score = fitness(placed, instance.container)

    return order, score

# Algorithm 2: Random-Restart Heuristic

def random_restart_solver(instance, attempts=200):
    n = len(instance.cylinders)
    best_order, best_score = None, float('inf')

    for _ in range(attempts):
        order = list(range(n))
        random.shuffle(order)
        placed = place_cylinders(order, instance.cylinders, instance.container)
        if placed is None:
            continue
        repair_centre_of_mass(placed, instance.container)
        score = fitness(placed, instance.container)
        if score < best_score:
            best_order, best_score = order[:], score
        if score == 0:
            break

    return best_order, best_score

# Run all reference instances

if __name__ == "__main__":
    instances = create_basic_instances() + create_challenging_instances()

    print("KV6018 – ALTERNATIVE ALGORITHMS RESULTS")

    for inst in instances:
        print(f"\nInstance: {inst.name}")

        order, score = greedy_solver(inst)
        print("Greedy order:", order)
        print("Greedy fitness:", score)

        order, score = random_restart_solver(inst)
        print("Random-restart order:", order)
        print("Random-restart fitness:", score)

order, score = greedy_solver(inst)
placed = place_cylinders(order, inst.cylinders, inst.container)
repair_centre_of_mass(placed, inst.container)

visualise_packing(
    placed,
    inst.container,
    title=f"Greedy Solution – {inst.name}"
)

order, score = random_restart_solver(inst)
placed = place_cylinders(order, inst.cylinders, inst.container)
repair_centre_of_mass(placed, inst.container)

visualise_packing(
    placed,
    inst.container,
    title=f"Random Restart – {inst.name}"
)
