(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, $filter, DateTimeService, sessions){
        $scope.sessions = angular.copy(sessions.data.results);
        $scope.search = {filter: ''};
        $scope.exam_name = $scope.sessions.length?$scope.sessions[0].examName:'';

        $scope.get_diff_time = function(d1, d2){
            return DateTimeService.get_diff_from_string(d1, d2);
        };
    });
})();