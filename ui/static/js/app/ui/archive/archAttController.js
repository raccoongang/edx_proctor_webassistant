(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, $filter, sessions){
        $scope.sessions = angular.copy(sessions.data.results);
        $scope.search = {filter: ''};

        console.log($scope.sessions);
    });
})();