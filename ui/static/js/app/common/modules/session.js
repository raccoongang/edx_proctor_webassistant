(function(){
    angular.module('proctor.session', ['proctor.i18n'])
        .service('TestSession', function($rootScope, $http, Auth, i18n, DateTimeService){
            var Session = null;

            this.registerSession = function(testing_center, course_id, exam_id, course_name, exam_name){
                return $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'POST',
                    headers: {Authorization: "Token " + Auth.get_token()},
                    data: JSON.stringify({
                        testing_center: testing_center,
                        course_id: course_id,
                        course_event_id: exam_id,
                        course_name: course_name,
                        exam_name: exam_name
                    })
                }).then(function(data){
                    Session = data.data;
                    if (course_name !== undefined && exam_name !== undefined) {
                        Session.course_name = course_name;
                        Session.exam_name = exam_name;
                    }
                    window.sessionStorage['proctoring'] = JSON.stringify(Session);
                }, function(data){
                    alert(i18n.translate('SESSION_ERROR_1'));
                });
            };

            this.endSession = function(comment){
                if (Session){
                    return $http({
                        url: $rootScope.apiConf.apiServer + '/event_session/' + Session.id + '/',
                        method: 'PATCH',
                        headers: {Authorization: "Token " + Auth.get_token()},
                        data: JSON.stringify({
                            status: 'archived',
                            comment: comment
                        })
                    }).then(function(){
                        Session = null;
                    }, function(){
                        alert(i18n.translate('SESSION_ERROR_2'));
                    });
                }
            };

            this.fetchSession = function(hash_key){
                return $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'GET',
                    headers: {Authorization: "Token " + Auth.get_token()},
                    params: {'session': hash_key}
                }).then(function(data){
                    Session = data.data.length == 1 ? data.data[0]: null;
                    if (Session){
                        window.sessionStorage['proctoring'] = JSON.stringify(Session);
                    }
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

            this.getSessionDuration = function(){
                if (Session){
                    return DateTimeService.get_now_diff_from_string(Session.start_date);
                }
            };

            this.flush = function(){
                Session = null;
                delete window.sessionStorage['proctoring'];
            };

            this.is_owner = function() {
                if (Session && Session.hasOwnProperty('owner_username')) {
                    return Auth.get_proctor() == Session['owner_username'];
                }
            };
        });
})();
