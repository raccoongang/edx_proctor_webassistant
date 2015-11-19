(function(){
    angular.module('proctor').controller('SessionCtrl', function($scope, data){
        $scope.courses = {};
        $scope.exams = {};

        console.log(data);

        $scope.start_session = function(){

        };
    });
})();