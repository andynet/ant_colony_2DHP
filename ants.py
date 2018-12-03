from random import random
import numpy as np
import argparse
import copy


def get_possibilities(ground, pheromone_v, pheromone_h, position):
    directions = []
    trails = []

    up = (position[0]-1, position[1])
    if ground[up] == b'.':
        directions.append('U')
        trails.append(pheromone_v[up])

    down = (position[0]+1, position[1])
    if ground[down] == b'.':
        directions.append('D')
        trails.append(pheromone_v[position])

    left = (position[0], position[1]-1)
    if ground[left] == b'.':
        directions.append('L')
        trails.append(pheromone_h[left])

    right = (position[0], position[1]+1)
    if ground[right] == b'.':
        directions.append('R')
        trails.append(pheromone_h[position])

    return directions, trails


def simulate_ant(ground, pheromone_v, pheromone_h, position, sequence, path):

    if len(sequence) == 0:
        # print(ground)
        # print(path)
        return path
    else:
        directions, trails = get_possibilities(ground, pheromone_v, pheromone_h, position)

        if len(directions) == 0:
            return 'X'

        cumsum = np.cumsum(trails)
        cumsum = [0] + list(cumsum)
        chosen = random() * cumsum[-1]

        # print(chosen)
        # print(cumsum)
        chosen_dir = ''
        for i in range(len(trails)):
            if cumsum[i] <= chosen < cumsum[i+1]:
                chosen_dir = directions[i]

        if chosen_dir == 'U':
            new_pos = (position[0]-1, position[1])
        elif chosen_dir == 'D':
            new_pos = (position[0]+1, position[1])
        elif chosen_dir == 'L':
            new_pos = (position[0], position[1]-1)
        elif chosen_dir == 'R':
            new_pos = (position[0], position[1]+1)
        else:
            return path + 'X'*len(sequence)

        ground[new_pos] = sequence[0]

        path = simulate_ant(ground, pheromone_v, pheromone_h, new_pos, sequence[1:], path + chosen_dir)

        return path


def count_bonds(ground_copy):

    count = 0
    # vertically
    for i in range(ground_copy.shape[0] - 1):
        for j in range(ground_copy.shape[1]):
            if ground_copy[i, j] == ground_copy[i+1, j] == b'h':
                count += 1

    for i in range(ground_copy.shape[0]):
        for j in range(ground_copy.shape[1] - 1):
            if ground_copy[i, j] == ground_copy[i, j+1] == b'h':
                count += 1

    return count


def add_pheromone(pheromone_v, pheromone_h, position, route, added_pheromone):

    if len(route) == 0:
        return
    else:
        direction = route[0]

        if direction == 'U':
            new_pos = (position[0]-1, position[1])
            pheromone_v[new_pos] += added_pheromone
        if direction == 'D':
            new_pos = (position[0]+1, position[1])
            pheromone_v[position] += added_pheromone
        if direction == 'L':
            new_pos = (position[0], position[1]-1)
            pheromone_h[new_pos] += added_pheromone
        if direction == 'R':
            new_pos = (position[0], position[1]+1)
            pheromone_h[position] += added_pheromone

        add_pheromone(pheromone_v, pheromone_h, new_pos, route[1:], added_pheromone)


def reconstruct_the_best(ground, pheromone_v, pheromone_h, position, sequence, path):

    if len(sequence) == 0:
        # print(ground)
        # print(path)
        return path
    else:
        directions, trails = get_possibilities(ground, pheromone_v, pheromone_h, position)

        max_i = int(np.argmax(trails))
        chosen_dir = directions[max_i]

        if chosen_dir == 'U':
            new_pos = (position[0]-1, position[1])
        elif chosen_dir == 'D':
            new_pos = (position[0]+1, position[1])
        elif chosen_dir == 'L':
            new_pos = (position[0], position[1]-1)
        elif chosen_dir == 'R':
            new_pos = (position[0], position[1]+1)
        else:
            return path + 'X'*len(sequence)

        ground[new_pos] = sequence[0]

        path = reconstruct_the_best(ground, pheromone_v, pheromone_h, new_pos, sequence[1:], path + chosen_dir)

        return path


def main():

    parser = argparse.ArgumentParser(description='Ant colony simulation')
    parser.add_argument('-s', '--sequence', required=True)
    args = parser.parse_args()

    space_ydim = (2 * len(args.sequence)) - 3
    space_xdim = (2 * len(args.sequence)) - 4
    sequence = args.sequence.upper()

    # np.full((space_ydim, space_xdim), ' ', dtype='|S1')
    first_pos = (space_ydim//2, space_xdim//2 - 2)
    second_pos = (space_ydim//2, space_xdim//2 - 1)

    ground = np.chararray((space_ydim, space_xdim))
    ground[:] = '.'
    ground[first_pos] = args.sequence[0]
    ground[second_pos] = args.sequence[1]

    pheromone_v = np.ones((space_ydim - 1, space_xdim))
    pheromone_h = np.ones((space_ydim, space_xdim - 1))

    # print(ground)
    # print(pheromone_h)
    # print(pheromone_v)

    trivial = 0
    for i in range(1, len(sequence)):
        if sequence[i-1] == sequence[i] == 'H':
            trivial += 1

    for i in range(1000):

        ground_copy = copy.deepcopy(ground)
        route = simulate_ant(ground_copy, pheromone_v, pheromone_h, second_pos, args.sequence[2:], 'R')
        # print(ground_copy)
        # print(route)
        if 'X' in route:
            print('invalid path')
            continue

        bond = count_bonds(ground_copy) - trivial
        added_pheromone = bond/len(sequence)
        # print(added_pheromone)

        add_pheromone(pheromone_v, pheromone_h, first_pos, route, added_pheromone)

    # print(pheromone_v)
    # print(pheromone_h)
    route = reconstruct_the_best(ground, pheromone_v, pheromone_h, second_pos, args.sequence[2:], 'R')
    bond = count_bonds(ground) - trivial
    print(ground)
    print(route)
    print(bond)


if __name__ == '__main__':
    main()

# TODO:
#  tidy the code
#  solve invalid paths
#  solve argmax: line 124 ValueError
#  do not recalculate the best, but store it
