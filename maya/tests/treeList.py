a = [(1, 1), (2, 1), (3, 1), (4, 3), (5, 3), (6, 3), (7, 7), (8, 7), (9, 7)]

# pass 1: create nodes dictionary
nodes = {}
for i in a:
    id, parent_id = i
    nodes[id] = { 'id': id }

# pass 2: create trees and parent-child relations
forest = []
for i in a:
    id, parent_id = i
    node = nodes[id]

    # either make the node a new tree or link it to its parent
    if id == parent_id:
        # start a new tree in the forest
        forest.append(node)
    else:
        # add new_node as child to parent
        parent = nodes[parent_id]
        if not 'children' in parent:
            # ensure parent has a 'children' field
            parent['children'] = []
        children = parent['children']
        children.append(node)

print forest