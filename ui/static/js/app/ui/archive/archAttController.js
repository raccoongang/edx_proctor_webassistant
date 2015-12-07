(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, $filter, sessions){
        $scope.sessions = angular.copy(sessions.data.results);
        $scope.searchFilter = '';
        $scope.exam_name = $scope.sessions[0].examName;
    });
})();