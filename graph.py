# https://www.python.org/doc/essays/graphs/


graph = {
    'A': ['B','C'],
    'B': ['C', 'q','D'],
    'C': ['D'],
    'D': ['C'],
    'E': ['F'],
    'F': ['C']
}

def find_path(graph, start, end, pathMemory=[]):
    path = pathMemory + [start]
    if start == end:
        return path
    if start not in graph:
        print(f'no path out from {start}')
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

path = find_path(graph, 'A', 'D')
print('Path: ', path)

def find_all_paths(graph, start, end, pathMemory=[]):
    path = pathMemory + [start]
    if start == end:
        return [path]
    if start not in graph:
        print(f'In {path} no arc out from {start}')
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newPaths = find_all_paths(graph, node, end, path)
            for newPath in newPaths:
                paths.append(newPath)
    return paths

paths = find_all_paths(graph, 'A', 'D')
print('All paths: ', paths)

def find_shortest_path(graph, start, end, pathMemory=[]):
    path = pathMemory + [start]
    if start == end:
        return path
    if start not in graph:
        return(f'no arc out from {start}')
    shortest = None
    for node in graph[start]:
        if node not in path:
            newPath = find_shortest_path(graph, node, end, path)
            if newPath:
                if not shortest or len(newPath) < len(shortest):
                    shortest = newPath
    return shortest

shortestPath = find_shortest_path(graph, 'A', 'D')
print(f'Shortest path: {shortestPath}')

