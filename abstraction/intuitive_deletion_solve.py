from graph import Graph
from solving_step import SolvingStep
import os, argparse, time, pickle, itertools

class Abstraction():
    def __init__(self):
        self.graphs = []
        self.cached_graphs = []
        self.solving_steps = dict()
        self.nodes = ''

    def main(self, args):
        #ABSTRACT
        start_abstract = time.time()
        # assumping there's only one connected subgraph in this instance (if the value > 1, means there are disjoint subgraphs)
        disjoint_graphs = 1
        self.graphs.append(Graph.build_graph_from_instance(args.instance, "benchmark"))
        self.graphs[-1].to_png()
        i = 1
        # stop abstracting when there're no more edges between the abstracted vertices (to allow abstraction of disjoint graphs)
        while len(self.graphs[-1].vertices) > disjoint_graphs:
            try:
                with open(f'graphs/benchmark_{i}.pickle', 'rb') as file:
                    self.graphs.append(pickle.load(file))
                print("Found cached abstraction level", i)
            except FileNotFoundError:
                print("\nGenerating abstraction level", i)
                disjoint_graphs, abstracted_graph = self.graphs[-1].abstract_graph_incremental(args.abstraction)
                self.graphs.append(abstracted_graph)
                print(abstracted_graph.to_asp())
                # Set cache to True to enable abstraction caching
                self.graphs[-1].safe(cache=False)
                self.graphs[-1].to_png()
            i += 1
        end_abstract = time.time()
            
        
        #SOLVE
        start_solve = time.time()
        print("\nFinding paths on abstraction level", len(self.graphs)-1)
        solving_step = SolvingStep(len(self.graphs)-1)
        solving_step.solve_incremental(args.solver, self.graphs[-1], len(self.graphs[-1].starts), 1, False)
        self.solving_steps[len(self.graphs)-1] = solving_step
        for level in reversed(range(len(self.graphs)-1)):
            print("\nFinding paths on abstraction level", level)
            previous_step = self.solving_steps[level+1]
            solving_step = SolvingStep(level)
            self.solving_steps[level] = solving_step
            for permutation in itertools.permutations(sorted(previous_step.assignments, key=lambda start_goal: -abs(start_goal[0]-start_goal[1]))):
                for start_goal in permutation:
                    # Determine all robots with the selected goal vertex
                    robots, goals = zip(*previous_step.assignments[start_goal])
                    visited = set()
                    for robot in robots:
                        for vertex in previous_step.visited[robot]:
                            visited.update(self.graphs[level+1].child_vertices[vertex])
                    # Generate corresponding subgraph
                    starts = self.graphs[level+1].child_vertices[start_goal[0]]
                    goals = self.graphs[level+1].child_vertices[start_goal[1]]
                    graph = self.graphs[level].get_subgraph(list(visited), starts, goals)
                    # Solve subproblem and add to plan
                    maxtime = 2
                    if previous_step.plan:
                        previous_time = max(previous_step.plan, key=lambda move: move.arguments[3].number).arguments[3].number
                        maxtime = 3*previous_time+2
                    solving_step.solve_incremental(args.solver, graph, len(robots), 2*maxtime, level==0)
                    if solving_step.unsat:
                        break
                if not solving_step.unsat:
                    break
            if solving_step.unsat:
                print("UNSATISFIABLE")
            else:
                # Print out combined paths in right order
                print(*(str(atom)+'.' for atom in sorted(solving_step.plan, key=lambda move: (move.arguments[3].number, move.arguments[0].number))))
                print()
                print(solving_step.asprilo)
                print()
        end_solve = time.time()
        
        print(f"Abstraction: {end_abstract-start_abstract:.3f}s, Solving: {end_solve-start_solve:.3f}s, Total: {end_solve-start_abstract:.3f}s")

def parse():
    '''Reads the program arguments as flagged parameters'''
    parser = argparse.ArgumentParser(
        description="Abstraction solver for asprilo instances"
    )
    parser.add_argument('--graph', '-g', metavar='<file>',
                        help='Encoding turning grid instance into graph with vertices and edges', required=True)
    parser.add_argument('--abstraction', '-a', metavar='<file>',
                        help='Encoding abstracting the map', required=True)
    parser.add_argument('--solver', '-s', metavar='<file>',
                        help='Encoding solving on a graph', required=True)
    parser.add_argument('--instance', '-i', metavar='<file>',
                        help='Map instance', required=True)
    args = parser.parse_args()
    if not os.path.isfile(args.graph):
        raise IOError("file %s not found!" % args.graph)
    if not os.path.isfile(args.abstraction):
        raise IOError("file %s not found!" % args.abstraction)
    if not os.path.isfile(args.solver):
        raise IOError("file %s not found!" % args.solver)
    if not os.path.isfile(args.instance):
        raise IOError("file %s not found!" % args.instance)
    return args

# Run application with commandline arguments
Abstraction().main(parse())