var app = angular.module('bigbinf_webApp', ['ngRoute', 'ngFileUpload']);

app.config(function($routeProvider) {
	$routeProvider
	.when('/', {
		templateUrl: 'static/html/main.html',
		controller: 'CsubmitJob'
	})
	.when('/about',{
		templateUrl: 'static/html/about.html',
	})
	.when('/regions',{
		templateUrl: 'static/html/regions.html',
		controller: 'Cregions'
	})
	
}); 


app.factory('Region', function ($http){
	var region = 'default';

	return {
		region: region
	};
})

app.controller('Ctitle', function ($scope, $http){
	$http.get('region')
		.success(function(data){
			console.log(data);
			$scope.region = data.region;
		});
});

app.controller('CsubmitJobFancy', ['$scope', 'Upload', '$timeout', function ($scope, Upload, $timeout) {
    $scope.uploadFile = function(file) {
    	console.log(file.name);
    Upload.upload({
      url: '/submitjob',
      data: {file: file, resultspath: $scope.resultspath, datapath: $scope.datapath},
    })
    .then(function (response) {
        file.result = response.data;
    }, function (err) {
    	console.log('error uploading');
      if (err.status > 0)
        $scope.errorMsg = err.status + ': ' + err.data;
    }, function (evt) {
      file.progress = parseInt(100.0 * evt.loaded / evt.total);
    });
    }
}]);

app.directive('fileModel', ['$parse', function ($parse) {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			element.bind('change', function(){
				$parse(attrs.fileModel)
				.assign(scope, element[0].files[0]);
				scope.$apply();
			});
		}
	};
}]);

app.service('fileUpload', ['$http', function ($http) {
	this.uploadFileToUrl = function(file, uploadUrl){
		var fd = new FormData();
		fd.append('file', file);
		$http.post(uploadUrl, fd,
		{
			transformRequest: angular.identity,
			// manually settings content type to multipart/form-data
			// fails due to the boundary parameter not being filled.
			headers:{'Content-Type': undefined}
		})
		.success(function(d){
			console.log('file upload successful', d);
		})
		.error(function(e){
			console.log('failed to upload', e)
		});

	}
}]);

app.controller('CsubmitJob', ['$scope', 'fileUpload', function($scope, fileUpload){
	
	$scope.fileChanged = function(element){
		$scope.jobfile = element.files[0];
		$scope.$apply();
	}

	$scope.submitJobForm = function(){
		var file = $scope.jobfile;
		var submitjobAPI = '/submitjob';
		fileUpload.uploadFileToUrl(file, submitjobAPI);
	};
}]);



app.controller('CjobQueue', function($scope, $http, $timeout){
	var requestJobQueue = function(){
		$http.get('queue')
		.success(function(data){
			$scope.queue = data;
		});
	};


	var pollQueue = function(){
		requestJobQueue();

		$timeout(function(){
			console.log('polled job queue');
			pollQueue();
		}, 5000);
	};

	$scope.deleteJob = function(jobname){
		$http.delete('deletejob', {params:{jobname:jobname}})
		.success(function(data){
			requestJobQueue();
		});
	}

	$scope.getResults = function(jobname){
		$http.get('results', {params:{jobname:jobname}})
		.success(function(data){
			console.log(data);
		});
	}




	requestJobQueue();
	pollQueue();



});


app.controller('Cregions', function($scope, $http){
	$http.get('regions')
	.success(function(data){
		$scope.regions = data.clouds;
	});
});
