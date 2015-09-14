var app = angular.module('bigbinf_webApp', ['ngRoute']);

app.config(function($routeProvider) {
	$routeProvider
	.when('/', {
		templateUrl: 'static/html/submitjob.html',
		controller: 'CsubmitJob'
	})
	.when('/about',{
		templateUrl: 'static/html/about.html',
	})
}); 

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

app.controller('CsubmitJob', ['$scope', 'fileUpload', function ($scope, fileUpload){
	
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