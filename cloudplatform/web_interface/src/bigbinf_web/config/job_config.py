pod = {
"apiVersion": "v1",
"kind": "Pod",
"metadata": {
	"name":"",
	"labels":{
		"app": "batch-job"
	}
},
"spec":{
	"containers":[
		{
			"name": "",
			"image": "",
			"volumeMounts":[
				{
					"name": "rawdata",
					"mountPath":""
				},
				{
					"name": "results",
					"mountPath": ""
				}
			]
			

		}
 	],
	"RestartPolicy": "Never",
	"volumes": [
		{
			"name": "rawdata",
			"hostPath":{
				"path": ""
			}
		},
		{
			"name": "results",
			"hostPath": {
				"path": ""
			}
		}
	]

 }
}