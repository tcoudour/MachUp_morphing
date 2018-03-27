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
			"uuid": "4F2366E5-421E-4835-B821-496607250C1A",
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
			"uuid": "4B455352-8288-4B69-8583-D6A4592ECB2B",
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
			"uuid": "91573F54-0679-4044-B2EE-AF7A30F10FD0",
			"type": "WingGeometry",
			"is_main": true,
			"side": "both",
			"span": 2,
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
		},
		{
			"uuid": "E1086D73-CB0F-410E-847D-401457FC896C",
			"type": "WingGeometry",
			"is_main": true,
			"side": "both",
			"span": 2,
			"sweep": 0,
			"dihedral": 5,
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
				"y": -2,
				"z": 0
			},
			"right_start": {
				"x": 0,
				"y": 2,
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
					"aileron": 1,
					"flap": 0
				}
			},
			"same_as_root": true
		}],
	"materials": [
		{
			"uuid": "92DAB3B0-8358-4517-AB77-7B8B184EBA65",
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
			"uuid": "D08FB849-9999-4394-90B7-756E06FAEFA4",
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
			"uuid": "FF9D5DC6-B905-448F-846A-23ABF99A9692",
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
		},
		{
			"uuid": "9BB9808E-E2B9-4506-B32A-E0A877689B98",
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
		"uuid": "67584B62-9587-47B3-B738-B0BF6277B5F7",
		"type": "Origin",
		"name": "TwoWings",
		"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
		"children": [
			{
				"uuid": "87D36476-9E91-441C-9189-AF3925B79893",
				"type": "Mesh",
				"name": "Center of Gravity",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "4F2366E5-421E-4835-B821-496607250C1A",
				"material": "92DAB3B0-8358-4517-AB77-7B8B184EBA65"
			},
			{
				"uuid": "3737A868-A134-4596-AA94-E0ECDC32E77D",
				"type": "Mesh",
				"name": "Aerodynamic Center",
				"visible": false,
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "4B455352-8288-4B69-8583-D6A4592ECB2B",
				"material": "D08FB849-9999-4394-90B7-756E06FAEFA4"
			},
			{
				"uuid": "684CD04D-583D-41A6-9EF6-5571FE66008D",
				"type": "PointLight",
				"name": "PointLight",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,10,10,-20,1],
				"color": 16777215,
				"intensity": 1,
				"distance": 0,
				"decay": 1
			},
			{
				"uuid": "4227189A-1554-4E48-A455-6CDF6D8A977F",
				"type": "Mesh",
				"name": "Wing_1",
				"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
				"geometry": "91573F54-0679-4044-B2EE-AF7A30F10FD0",
				"material": "FF9D5DC6-B905-448F-846A-23ABF99A9692",
				"children": [
					{
						"uuid": "1AC429E0-C8B7-46DA-9B70-83A2399157D6",
						"type": "Mesh",
						"name": "Wing_2",
						"matrix": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
						"geometry": "E1086D73-CB0F-410E-847D-401457FC896C",
						"material": "9BB9808E-E2B9-4506-B32A-E0A877689B98"
					}]
			}],
		"background": 11184810
	}
}