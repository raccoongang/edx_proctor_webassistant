(function(){
    angular.module('proctor').controller('ProfileCtrl', function($scope){
        $scope.data = [
            {'name': "John", 'age': 25},
            {'name': "Hanna", 'age': 5},
            {'name': "Dick", 'age': 23},
            {'name': "Carlos", 'age': 12}
        ];
    });
})();