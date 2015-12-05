(function(){
    angular.module('proctor').controller('ArchCtrl', function($scope, events){
        $scope.events = events.data;
    });
})();