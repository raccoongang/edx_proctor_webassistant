(function(){
    angular.module('proctor').controller('SessionCtrl', function($scope, data){
        $scope.courses = [];
        $scope.exams = [];
        $scope.session = {};
        if (data.data.results !== undefined && data.data.results.length) {
            var c_list = [];
            angular.forEach(data.data.results, function (val, key) {
                c_list.push({name: val.name, id: val.id});
            });
            $scope.courses = c_list;
        }

        $scope.$watch('session.course', function(val, old){
            if (data.data.results !== undefined && data.data.results.length) {
                var e_list = $.grep(data.data.results, function(e){
                    return e.id == val;
                });
                if (e_list.length){
                    $scope.exams = e_list[0].proctored_exams;
                }
            }
        });

        $scope.start_session = function(){

        };
    });
})();