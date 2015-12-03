'use strict';

(function(){
    angular.module('proctor.api', []).service('Api', ['$rootScope', '$http', 'Auth', 'TestSession',
        function($rootScope, $http, Auth, TestSession){
        var get_url = function(call){
            return '' + $rootScope.apiConf.apiServer + '/' + call + '/';
        };

        var generic_api_call = function(params){
            params.headers !== undefined?
                params.headers.Authorization = "Token " + Auth.get_token():
                params.headers = {Authorization: "Token " + Auth.get_token()};
            return $http(params);
        };

        this.accept_exam_attempt = function(code){
            return generic_api_call({
                'url':  get_url('start_exam') + code,
                'method': 'GET'
            });
        };

        this.stop_exam_attempt = function(attempt, user_id){
            return generic_api_call({
                'url':  get_url('stop_exam') + attempt,
                'method': 'PUT',
                'data': JSON.stringify({action: 'submit', user_id: user_id})
            });
        };

        this.stop_all_exam_attempts = function(attempts){
            angular.forEach(attempts, function(val, key){
                val.action = 'submit';
            });
            return generic_api_call({
                'url':  get_url('stop_exams'),
                'method': 'PUT',
                'data': JSON.stringify({attempts: attempts})
            });
        };

        this.get_exams_status = function(list){
            return generic_api_call({
                'url':  get_url('poll_status'),
                'method': 'POST',
                'data': JSON.stringify({list: list})
            });
        };

        this.send_review = function(payload){
            return generic_api_call({
                'url':  get_url('review'),
                'method': 'POST',
                data: JSON.stringify(payload)
            });
        };

        this.get_session_data = function(){
            return generic_api_call({
                'url':  get_url('proctored_exams'),
                'method': 'GET'
            });
        };

        this.restore_session = function(){
            if (window.sessionStorage['proctoring'] !== undefined){
                var session = TestSession.getSession();
                if (session) {
                    return generic_api_call({
                        'url':  get_url('exam_register'),
                        'method': 'GET',
                        'params': {session: session.hash_key}
                    });
                }
            }
        };

        this.start_all_exams = function(list){
            return generic_api_call({
                'url':  get_url('bulk_start_exam'),
                'method': 'POST',
                'data': JSON.stringify({list: list})
            });
        };
    }]);
})();
