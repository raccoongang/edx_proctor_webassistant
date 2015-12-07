(function(){
    angular.module('proctor').controller('ArchCtrl', function($scope, NgTableParams, DateTimeService, events, courses_data){
        $scope.events = events.data;
        $scope.searchFilter = '';

        $scope.tableParams = new NgTableParams({
            page: 1,
            count: 10
        }, {
            data: $scope.events
        });

        $scope.$watch('searchFilter', function(){
            $scope.tableParams.reload();
        });

        var get_event_data = function(){

            // Adds `course_name` and `exam_name` to every event
            if (courses_data.data.results !== undefined && courses_data.data.results.length){
                angular.forEach($scope.events, function(val, key){
                    val.start_date = DateTimeService.get_localized_date_from_string(val.start_date);
                    val.end_date = DateTimeService.get_localized_date_from_string(val.end_date);
                    var course = courses_data.data.results.filter({id: val.course_id});
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