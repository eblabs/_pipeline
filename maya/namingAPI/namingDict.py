dNameConvension = {
	'type': {
		'group': 'grp',
		'null': 'null',
		'locator': 'loc',
		'joint': 'jnt',
		'mesh': 'mesh',
		'curve': 'crv',
		'surface': 'surf',
		'control': 'ctrl',
		'skinCluster': 'skin',
		'xtrans': 'xtrs',
		'blendshape': 'bs',
		'cluster': 'cls',
		'lattice': 'lat',
		'wrap': 'wrap',
		'blueprint': 'bpJnt',
		'bindJoint': 'bindJnt',
		'ikHandle': 'ikHnd',
		'plusMinusAverage': 'pmav',
		'multiplyDivide': 'multDv',
		'addDoubleLinear': 'add',
		'multDoubleLinear': 'mult',
		'condition': 'cond',
		'reverse': 'rvs',
		'remapValue': 'remap',
		'curveInfo': 'crvInfo',
		'distanceBetween': 'disBtw',
		'composeMatrix': 'compMatrix',
		'decomposeMatrix': 'decompMatrix',
		'multMatrix': 'multMatrix',
		'addMatrix': 'addMatrix',
		'blendColors': 'blend',
		'clamp': 'clamp',
		'closetPointOnMesh': 'clsPntOnMesh',
		'closetPointOnSurface': 'clsPntOnSurf',
		'nearestPointOnCurve': 'clsPntOnCrv',
		'pointOnCurveInfo': 'pntOnCrvInfo',
		'pointOnSurfaceInfo': 'pntOnSurfInfo',
		}

	'side': {
		'left': 'l',
		'right': 'r',
		'middle': 'm',
		'up': 'u',
		'down': 'd',
		'front': 'f',
		'back': 'b',
		'leftFront': 'lf',
		'leftBack': 'lb',
		'leftUp': 'lu',
		'leftDown': 'ld',
		'rightFront': 'rf',
		'rightBack': 'rb',
		'rightUp': 'ru',
		'rightDown': 'rd',
		'middleFront': 'mf',
		'middleBack': 'mb',
		'middleUp': 'mu',
		'middleDown': 'md'
	}

	'resolution':{
		'high': 'high',
		'middle': 'mid',
		'low': 'low',
		'proxy': 'proxy',
		'simulation': 'sim'
	}
}

dNameConvensionInverse = {v: k for k, v in dNameConvension.iteritems()}