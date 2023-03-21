import random
from classes import Graph, Weekdays

def repairUnavailables(schedule):
    unavailables = findUnavailables(schedule) #list of all pairs that have been assigned with unavailable staff
    while unavailables is not []:
        unavailable = random.choice(unavailables)
        schedule = repairUnavailable(schedule, unavailable)
        unavailables = findUnavailables(schedule)

def repairUnavailable(schedule, unavailable):
    for length in range(2, len(schedule)):
        #find all cycles starting and ending at unavailable of length 'length'
        #if there are no cycles, continue
        #else, pick a random cycle, make the necessary swaps (indicated by the cycle), and break
        break
    return schedule

def findUnavailables(schedule):
    return list()

def findConnections(schedule):
    '''
    connection based on staff in one pair being open to work
    (not yet working on the day) another pair's role
    '''
    connections = []
    for pair in schedule:
        staff = pair[1]

        allDays = {day for day in Weekdays}
        daysStaffIsWorking = {pair[0].day for pair in schedule if pair[1] is staff}
        daysNotWorking = allDays - daysStaffIsWorking

        for connectedPair in schedule:
            if connectedPair[0].day in daysNotWorking:
                connections.append((pair,connectedPair))
    return connections

def dfs_withoutYield(graph, start, end):
    result = []
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            result.append(path)
            continue
    for nextState in graph[state]:
        if nextState in path:
            continue
        fringe.append((nextState, path + [nextState]))
    return result

def dfs(graph, start, end):
     # https://stackoverflow.com/a/40834276
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            fringe.append((next_state, path+[next_state]))


def depth_first_search(graph, start):
    # https://codereview.stackexchange.com/a/247370
    stack = [start]
    visited = set()
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        yield node
        visited.add(node)
        for neighbor in graph[node]:
            stack.append(neighbor)

graph = { 1: [2,3,5], 2: [1], 3: [1], 4: [2], 5: [2]}

paths = list(depth_first_search(graph, 1))

cycles = []
for node in graph:
    cycles.append(path for path in dfs_withoutYield(graph, node, node))

cyclesComp = [
    [node] + path for node in graph for path in dfs(graph,node, node)
]

print(cyclesComp)
