nameDict = {
				'type': {	
							#transform
							'group': 'grp',
							'null': 'null',
							'locator': 'loc',
							'follicle': 'fol',
							'xtran': 'xtr',
							
							#geometry
							'mesh': 'mesh',
							'surface': 'surf',
							'curve': 'crv',
							'curveLine': 'crvLine',

							#rigging
							'joint': 'jnt',
							'bindJoint': 'bind',
							'blueprintJoint': 'bpJnt',
							'reverseJoint': 'rvsJnt',
							'blueprintCurve': 'bpCrv',
							'blueprintSurface': 'bpSurf',
							'blueprintMesh': 'bpMesh',
							'ikHandle': 'ikHnd',
							'pointConstraint': 'poc',
							'orientConstraint': 'onc',
							'parentConstraint': 'pac',
							'scaleConstraint': 'sac',
							'aimConstraint': 'amc',

							#deformer
							'skinCluster': 'skin',
							'blendshape': 'bs',
							'cluster': 'cls',
							'clusterHandle': 'clsHnd',
							'lattice': 'lat',
							'latticeBase': 'latBase',
							'deltaMesh': 'delMush',
							'wrap': 'wrp',
							'wire': 'wire',
							'wireBase': 'wireBase',
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
							'deformationRig': 'deformationRig',
							'animationRig': 'animationRig',
							'geometryGroup': 'geometryGrp',
							'skeletonGroup': 'skeletonGrp',
							'componentsGroup': 'componentsGrp',
							'rigNodesGroup': 'rigNodesGrp',
							'rigComponent': 'rigComponent',
							'rigLocal': 'rigLocal',
							'controlsGroup': 'controlsGrp',
							'jointsGroup': 'jointsGrp',
							'nodesLocalGroup': 'nodesLocalGrp',
							'rigWorld': 'rigWorld',
							'nodesHideGroup': 'nodesHideGrp',
							'nodesShowGrroup': 'nodesShowGrp',
							'subComponents': 'subComponents',
						},

				'side': {
							'left': 'l',
							'right': 'r',
							'middle': 'm',
						},

				'resolution': {
								'high': 'high',
								'middle': 'mid',
								'low': 'low',
								'proxy': 'proxy',
								'simulation': 'sim'
							},

				}

nameInverseDict = {}
for key in nameDict:
	inverseDict = {key: {v: k for k, v in nameDict[key].iteritems()}}
	nameInverseDict.update(inverseDict)