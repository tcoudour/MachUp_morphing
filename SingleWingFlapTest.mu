{
	"MachUp": {
		"version": 4
	},
	"metadata": {
		"version": 4.4,
		"type": "Object",
		"generator": "Object3D.toJSON"
	},
	"geometries": [
		{
			"uuid": "DA927E8F-C628-49F5-9F38-ADFB7637B41C",
			"type": "SphereBufferGeometry",
			"radius": 0.1,
			"widthSegments": 32,
			"heightSegments": 16,
			"phiStart": 0,
			"phiLength": 6.283185307179586,
			"thetaStart": 0,
			"thetaLength": 3.141592653589793
		},
		{
			"uuid": "EDF85348-56DC-4BB4-BDD6-E382A98B9072",
			"type": "SphereBufferGeometry",
			"radius": 0.1,
			"widthSegments": 32,
			"heightSegments": 16,
			"phiStart": 0,
			"phiLength": 6.283185307179586,
			"thetaStart": 0,
			"thetaLength": 3.141592653589793
		},
		{
			"uuid": "F3F65A70-6971-4D2D-8BA9-891B32D6CF29",
			"type": "WingGeometry",
			"is_main": true,
			"side": "both",
			"span": 4,
			"sweep": 0,
			"dihedral": 0,
			"mount": 0,
			"washout": 0,
			"root_chord": 1,
			"tip_chord": 1,
			"root_airfoil": {
				"NACA 2412": {
					"properties": {
						"type": "linear",
						"alpha_L0": -0.036899751,
						"CL_alpha": 6.283185307,
						"Cm_L0": -0.0527,
						"Cm_alpha": -0.08,
						"CD0": 0.0055,
						"CD0_L": -0.0045,
						"CD0_L2": 0.01,
						"CL_max": 1.4
					}
				}
			},
			"tip_airfoil": {
				"NACA 2412": {
					"properties": {
						"type": "linear",
						"alpha_L0": -0.036899751,
						"CL_alpha": 6.283185307,
						"Cm_L0": -0.0527,
						"Cm_alpha": -0.08,
						"CD0": 0.0055,
						"CD0_L": -0.0045,
						"CD0_L2": 0.01,
						"CL_max": 1.4
					}
				}
			},
			"nSeg": 40,
			"nAFseg": 50,
			"left_start": {
				"x": 0,
				"y": 0,
				"z": 0
			},
			"right_start": {
				"x": 0,
				"y": 0,
				"z": 0
			},
			"dy": 0,
			"control": {
				"has_control_surface": true,
				"span_root": 0,
				"span_tip": 1,
				"chord_root": 0.2,
				"chord_tip": 0.2,
				"is_sealed": 1,
				"mix": {
					"elevator": 0,
					"rudder": 0,
					"aileron": 0,
					"flap": 1
				}
			},
			"same_as_root": true
		}],
	"materials": [
		{
			"uuid": "D4767800-B84F-40FB-8916-83EF993B7ACB",
			"type": "MeshStandardMaterial",
			"color": 16711680,
			"roughness": 0.5,
			"metalness": 0.5,
			"emissive": 16711680,
			"side": 2,
			"depthFunc": 3,
			"depthTest": true,
			"depthWrite": true,
			"skinning": false,
			"morphTargets": false
		},
		{
			"uuid": "FCA18F50-F3EE-4FF1-9DA0-E71C988B80B6",
			"type": "MeshStandardMaterial",
			"color": 6684927,
			"roughness": 0.5,
			"metalness": 0.5,
			"emissive": 6684927,
			"side": 2,
			"depthFunc": 3,
			"depthTest": true,
			"depthWrite": true,
			"skinning": false,
			"morphTargets": false
		},
		{
			"uuid": "FEF7B928-318F-4F83-82A6-5AE4243820F6",
			"type": "MeshPhongMaterial",
			"color": 16777215,
			"emissive": 0,
			"specular": 1118481,
			"shininess": 30,
			"side": 2,
			"depthFunc": 3,
			"depthTest": true,
			"depthWrite": true,
			"skinning": false,
			"morphTargets": false
		}],
	"object": {
		"uuid": "1CD1B54C-5BCD-48C4-AFBD-F995BF20D389",
		"type": "Origin",
		"name": "SingleWingFlapTest",
		"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
		"children": [
			{
				"uuid": "065487A6-EAFA-41F9-9D80-134FC763A1B9",
				"type": "Mesh",
				"name": "Center of Gravity",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "DA927E8F-C628-49F5-9F38-ADFB7637B41C",
				"material": "D4767800-B84F-40FB-8916-83EF993B7ACB"
			},
			{
				"uuid": "B08FD978-66F3-4D52-BD6E-D5DE4E76F312",
				"type": "Mesh",
				"name": "Aerodynamic Center",
				"visible": false,
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "EDF85348-56DC-4BB4-BDD6-E382A98B9072",
				"material": "FCA18F50-F3EE-4FF1-9DA0-E71C988B80B6"
			},
			{
				"uuid": "A5C6DDF4-DFA6-4C8A-B97A-ADF592968891",
				"type": "PointLight",
				"name": "PointLight",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,10,10,-20,1],
				"color": 16777215,
				"intensity": 1,
				"distance": 0,
				"decay": 1
			},
			{
				"uuid": "3C0F96C0-08E5-4C28-962E-C55E9BBF8990",
				"type": "Mesh",
				"name": "Wing_1",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "F3F65A70-6971-4D2D-8BA9-891B32D6CF29",
				"material": "FEF7B928-318F-4F83-82A6-5AE4243820F6"
			}],
		"background": 11184810
	}
}