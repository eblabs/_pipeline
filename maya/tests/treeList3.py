data = [
    {'value': 'A', 'level': 0},
    {'value': 'B', 'level': 1},
    {'value': 'C', 'level': 2},
    {'value': 'D', 'level': 1},
    {'value': 'E', 'level': 2},
    {'value': 'F', 'level': 2},
    {'value': 'G', 'level': 0},
    {'value': 'H', 'level': 1}
	]

class Node(object):
	"""docstring for Node"""
	def __init__(self, val=None):
		self.value = val
		self.children = []
	def __repr__(self):
		return '<Node {}>'.format(self.value)
		
root = Node()

for record in data:
	last = root
	for _ in range(record['level']):
		last = last.children[-1]
	last.children.append(Node(record['value']))