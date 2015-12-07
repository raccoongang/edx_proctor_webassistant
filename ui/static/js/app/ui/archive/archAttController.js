(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, sessions){
        $scope.sessions = sessions.data.results;
        $scope.searchFilter = '';
        $scope.exam_name = $scope.sessions[0].examName;
    });
})();