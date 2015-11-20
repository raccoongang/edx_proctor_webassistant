(function(){
    angular.module('proctor').controller('SessionCtrl', function($scope, $location, data, TestSession){
        $scope.courses = [];
        $scope.exams = [];
        $scope.session = {};
        if (data.data.results !== undefined && data.data.results.length) {
            var c_list = [];
            angular.forEach(data.data.results, function (val, key) {
                c_list.push({name: val.name, id: val.id});
            });
            $scope.courses = c_list;
            $scope.session.course = c_list[0].id;
        }

        $scope.$watch('session.course', function(val, old){
            if (data.data.results !== undefined && data.data.results.length) {
                var e_list = $.grep(data.data.results, function(e){
                    return e.id == val;
                });
                if (e_list.length){
                    $scope.exams = e_list[0].proctored_exams;
                    if ($scope.exams.length) {
                        $scope.session.exam = e_list[0].proctored_exams[0].id;
                    }
                }
            }
        });

        $scope.start_session = function(){
            TestSession.registerSession(
                $scope.session.testing_centre,
                $scope.session.course,
                $scope.session.exam
            )
                .then(function(){
                    $location.path('/');
                }, function(){

                });
        };

    });
})();