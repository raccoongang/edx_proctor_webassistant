(function(){
    angular.module('sessionEvents', [])
        .service('TestSession', function($rootScope, $http, Auth){
            var Session = null;

            this.registerSession = function(testing_center, course_id, exam_id, course_name, exam_name){
                return $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'POST',
                    headers: {Authorization: "Token " + Auth.get_token()},
                    data: JSON.stringify({
                        testing_center: testing_center,
                        course_id: course_id,
                        course_event_id: exam_id
                    })
                }).then(function(data){
                    Session = data.data;
                    if (course_name !== undefined && exam_name !== undefined) {
                        Session.course_name = course_name;
                        Session.exam_name = exam_name;
                    }
                    window.sessionStorage['proctoring'] = Session;
                }, function(data){
                    alert("Failed to create/join session");
                });
            };

            this.endSession = function(){

            };

            this.getSession = function(){
                return angular.copy(Session);
            };
        });
})();
