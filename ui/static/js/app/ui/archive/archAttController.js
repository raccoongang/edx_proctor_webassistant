(function(){
    angular.module('proctor').controller('ArchAttCtrl', function($scope, sessions){
        $scope.sessions = sessions.data;
    });
})();