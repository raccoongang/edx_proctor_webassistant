(function(){
    angular.module('proctor').controller('ArchCtrl', function($scope, events, courses_data){
        $scope.events = events.data;

        $scope.tableParams = new NgTableParams({
            page: 1,
            count: 10
        }, {
            data: $scope.events
        });

        var get_event_data = function(){

            // Adds `course_name` and `exam_name` to every event
            if (courses_data.data.results !== undefined && courses_data.data.results.length){
                angular.forEach($scope.events, function(val, key){
                    var course = courses_data.results.filter({id: val.course_id});
                    if (course.length){
                        val.course_name = course[0].name;
                        var exam = course[0].proctored_exams.filter({id: val.course_event_id});
                        if (exam.length){
                            val.exam_name = exam[0].exam_name;
                        }
                    }
                });
            }
        };

        get_event_data();
    });
})();