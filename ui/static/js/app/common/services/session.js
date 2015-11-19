(function(){
    angular.module('sessionEvents', [])
        .service('TestSession', function($rootScope, $http, Auth){
            var Session = null;

            this.registerSession = function(testing_center, course_id, exam_id){
                $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'POST',
                    headers: {Authorization: "Token " + Auth.get_token()},
                    data: JSON.stringify({
                        testing_center: testing_center,
                        course_id: course_id,
                        course_event_id: exam_id
                    })
                }).then(function(data){
                    console.log(data);
                });
            };

            this.endSession = function(){

            };

            this.getSession = function(){
                return angular.copy(Session);
            };
        });
})();
