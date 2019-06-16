data = [
		{'importModel': {}},
		{'blueprints': {}},
		{'blueprintJoints': {'parent': 'blueprints'}},
		{'blueprintCurve': {'parent': 'blueprints'}},
		{'build': {}},
		{'components': {'parent': 'build'}},
		{'createComponents': {'parent': 'components'}},
		{'connectComponents': {'parent': 'components'}},
		{'deformer': {}}
		]

def get_child(tree, data):
	key = data.keys()[0]
	if 'parent' in data[key]:
		parentTask = data[key]['parent']
		if parentTask:
			for treeInfo in tree:
				keyTree = treeInfo.keys()[0]
				if parentTask == keyTree:
					treeInfo[parentTask]['children'].append({key:{'children': []}})
					return True
				else:
					isParent = get_child(treeInfo[keyTree]['children'], data)
					if isParent:
						return True
	else:
		tree.append({key:{'children': []}})
					
	
tree = []

for dataInfo in data:
	get_child(tree, dataInfo)