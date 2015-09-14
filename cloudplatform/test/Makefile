default:
	docker build -t bigbinf/testjob .
remotebuild:
	curl  -X POST --header "Content-Type: application/json" --data-binary @testjob.tar.gz http://localhost:4444/build?t=10.0.0.47:5000/bigbinf/testjob