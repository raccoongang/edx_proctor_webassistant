(function(){
    angular.module('proctor.session', [])
        .service('TestSession', function($rootScope, $http, Auth, i18n){
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
                    alert(i18n.translate('SESSION_ERROR_1'));
                });
            };

            this.endSession = function(){
                return $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'PUT',
                    headers: {Authorization: "Token " + Auth.get_token()},
                    data: JSON.stringify({
                        status: 'finished'
                    })
                }).then(function(){
                    Session = null;
                }, function(){
                    alert(i18n.translate('SESSION_ERROR_2'));
                });
            };

            this.getSession = function(){
                return angular.copy(Session);
            };

            this.setSession = function(obj){
                if (!Session){
                    Session = obj;
                }
            };
        });
})();
