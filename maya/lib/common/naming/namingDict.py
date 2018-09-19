dNameConvension = {
				'type': {	
							#transform
							'group': 'grp',
							'null': 'null',
							'locator': 'loc',
							'follicle': 'fol',
							
							#geometry
							'mesh': 'mesh',
							'surface': 'surf',
							'curve': 'crv',

							#rigging
							'joint': 'jnt',
							'bind', 'bind',
							'blueprintJoint': 'bpJnt',
							'blueprintCurve': 'bpCrv',
							'blueprintSurface': 'bpSurf',
							'blueprintMesh': 'bpMesh',
							'ikHandle': 'ikHnd',

							#deformer
							'skinCluster': 'skin',
							'blendshape': 'bs',
							'cluster': 'cls',
							'clusterHandle': 'clsHnd'
							'lattice': 'lat',
							'latticeBase': 'latBase',
							'deltaMesh': 'delMush',
							'wrap': 'wrp',
							'wire': 'wire',
							'sculpt': 'scpt',
							'softMode': 'softMo',
							'jiggle': 'jiggle',
							'bend': 'bend',
							'bendHandle': 'bendHnd',
							'flare': 'flare',
							'flareHandle': 'flareHnd',
							'sine': 'sine',
							'sineHandle': 'sineHnd',
							'squash': 'squash',
							'squashHandle': 'squashHnd',
							'twist': 'twist',
							'twistHandle': 'twistHnd',
							'wave': 'wave',
							'waveHandle': 'waveHnd',

							#controller
							'control': 'ctrl',
							'outputControl': 'output',
							'stack': 'stack',
							'space': 'space',
							'passer': 'passer',
							'zero': 'zero',
							'controlShape': 'ctrlShape',

							#muscle
							'muscle': 'mus',
							'fat': 'fat',
							'bone': 'bone',

							#utility
							'plusMinusAverage': 'pmav',
							'multiplyDivide': 'multDv',
							'addDoubleLinear': 'add',
							'multDoubleLinear': 'mult',
							'condition': 'cond',
							'reverse': 'rvs',
							'remapValue': 'remap',
							'setRange': 'range',
							'curveInfo': 'crvInfo',
							'distanceBetween': 'disBtw',
							'composeMatrix': 'compMatrix',
							'decomposeMatrix': 'decompMatrix',
							'multMatrix': 'multMatrix',
							'addMatrix': 'addMatrix',
							'inverseMatrix': 'inverseMatrix',
							'fourByFourMatrix': 'matrix4x4',
							'wtAddMatrix': 'wtAddMatrix',
							'quatToEuler': 'quatToEuler',
							'blendColors': 'blend',
							'clamp': 'clamp',
							'closetPointOnMesh': 'clsPntOnMesh',
							'closetPointOnSurface': 'clsPntOnSurf',
							'nearestPointOnCurve': 'clsPntOnCrv',
							'pointOnCurveInfo': 'pntOnCrvInfo',
							'pointOnSurfaceInfo': 'pntOnSurfInfo',
							'choice': 'choice',
							'angleBetween': 'angleBtw',

							# rig component
							'rigComponent': 'rigComponent',
							'rigLocal': 'rigLocal',
							'controlsGrp': 'controlsGrp',
							'jointsGrp': 'jointsGrp',
							'nodesLocal': 'nodesLocal',
							'rigWorld': 'rigWorld',
							'nodesHide': 'nodesHide',
							'nodesShow': 'nodesShow',
							'subComponents': 'subComponents',
						},

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
						},

				'resolution': {
								'high': 'high',
								'middle': 'mid',
								'low': 'low',
								'proxy': 'proxy',
								'simulation': 'sim'
							},

				}

dNameConvensionInverse = {}
for sKey in dNameConvension:
	dInverse = {sKey: {v: k for k, v in dNameConvension[sKey].iteritems()}}
	dNameConvensionInverse.update(dInverse)