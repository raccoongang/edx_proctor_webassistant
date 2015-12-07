(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, $filter, sessions){
        $scope.sessions = angular.copy(sessions.data.results);
        $scope.search = {filter: ''};
        $scope.exam_name = $scope.sessions.length?$scope.sessions[0].examName:'';

        $scope.$watch('search.filter', function(val){
            $scope.sessions = $filter('filter')($scope.sessions, val);
        });
    });
})();