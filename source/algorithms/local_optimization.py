from .base_algorithm import BaseAlgorithm
from functools import partialmethod


class LocalOptmizationHeuristics(BaseAlgorithm):

    ## Pairwise exchange (2-opt)

    # swap two edges
    def swap(self, solution, x, y):
        return solution[:x] + solution[x:y + 1][::-1] + solution[y + 1:]

    def pairwise_exchange(self, ga_solution=None):
        solution = ga_solution or self.generate_solution()
        stable, best = False, self.compute_length(solution)
        lengths, tours = [best], [solution]
        while not stable:
            stable = True
            for i in range(1, self.size - 1):
                for j in range(i + 1, self.size):
                    candidate = self.swap(solution, i, j)
                    length_candidate = self.compute_length(candidate)
                    if best > length_candidate:
                        solution, best = candidate, length_candidate
                        tours.append(solution)
                        lengths.append(best)
                        stable = False
        if ga_solution:
            return tours[-1]
        return [self.format_solution(step) for step in tours], lengths

    ## Node and edge insertion

    def substring_insertion(self, k):
        solution = self.generate_solution()
        stable, best = False, self.compute_length(solution)
        lengths, tours = [best], [solution]
        while not stable:
            stable = True
            for i in range(self.size - k):
                for j in range(self.size):
                    substring = solution[i:(i + k)]
                    candidate = solution[:i] + solution[(i + k):]
                    candidate = candidate[:j] + substring + candidate[j:]
                    tour_length = self.compute_length(candidate)
                    if best > tour_length:
                        stable, solution, best = False, candidate, tour_length
                        tours.append(solution)
                        lengths.append(best)
        return [self.format_solution(step) for step in tours], lengths

    node_insertion = partialmethod(substring_insertion, 1)
    edge_insertion = partialmethod(substring_insertion, 2)
    
    ## 3-opt
    def opt3(self):
        '''
        Don't change anything here!
        '''
        tours = self._custom_algorithm()
        lengths = [self.compute_length(tour) for tour in tours]
        return [self.format_solution(step) for step in tours], lengths
    
    def possible_segments(self, N):
        segments = ((i, j, k) for i in range(N) for j in range(i + 2, N-1) for k in range(j + 2, N - 1 + (i > 0)))
        return segments
        
    def reverse_segments(self, route, case, i, j, k):
        """
        Create a new tour from the existing tour
        Args:
            route: existing tour
            case: which case of opt swaps should be used
            i:
            j:
            k:
        Returns:
            new route
        """
        if (i - 1) < (k % len(route)):
            first_segment = route[k% len(route):] + route[:i]
        else:
            first_segment = route[k % len(route):i]
        second_segment = route[i:j]
        third_segment = route[j:k]

        if case == 0:
            pass
        elif case == 1:
            # A'BC
            solution = list(reversed(first_segment)) + second_segment + third_segment
        elif case == 2:
            # ABC'
            solution = first_segment + second_segment + list(reversed(third_segment))
        elif case == 3:
            # A'BC'
            solution = list(reversed(first_segment)) + second_segment + list(reversed(third_segment))
        elif case == 4:
            # A'B'C
            solution = None # need implement
        elif case == 5:
            # AB'C
            solution = None # need implement
        elif case == 6:
            # AB'C'
            solution = None # need implement
        elif case == 7:
            # A'B'C
            solution = None # need implement
        return solution
    
    def _custom_algorithm(self):
        '''
        Please implement the algorithm here
        
        - generate a random route:
            `solution = self.generate_solution()`
        
        - get the distance between the two cities:
            `dist = self.distances[A][B]`
            
        - get route length:
            `length = self.compute_length(tour)`
        '''
        solution = self.generate_solution()
        stable = False
        tours = [solution]
        while not stable:
            stable = True
            for (i, j, k) in self.possible_segments(self.size):
                A, B, C, D, E, F = solution[i - 1], solution[i], solution[j - 1], solution[j], solution[k - 1], solution[k % len(solution)]
                moves_cost = {
                    0: 0,
                    1: self.distances[A][B] + self.distances[E][F] - (self.distances[B][F] + self.distances[A][E]),
                    2: self.distances[C][D] + self.distances[E][F] - (self.distances[D][F] + self.distances[C][E]),
                    3: self.distances[A][B] + self.distances[C][D] + self.distances[E][F] - (self.distances[A][D] + self.distances[B][F] + self.distances[E][C]),
                    4: self.distances[A][B] + self.distances[C][D] + self.distances[E][F] - (self.distances[C][F] + self.distances[B][D] + self.distances[E][A]),
                    5: self.distances[B][A] + self.distances[D][C] - (self.distances[C][A] + self.distances[B][D]),
                    6: self.distances[A][B] + self.distances[C][D] + self.distances[E][F] - (self.distances[B][E] + self.distances[D][F] + self.distances[C][A]),
                    7: self.distances[A][B] + self.distances[C][D] + self.distances[E][F] - (self.distances[A][D] + self.distances[C][F] + self.distances[B][E]),
                }
                
                # Find the item with the max value in `moves_cost`, return dict key
                best_return = None # need implement
                
                if moves_cost[best_return] > 0:
                    solution = self.reverse_segments(solution, best_return, i, j, k)
                    tours.append(solution)
                    stable = False
                    break
        if ga_solution:
            return tours[-1]
        return tours
    
    