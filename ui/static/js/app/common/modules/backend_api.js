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

        this.restore_session = function(session_hash){
            var hash_key = null;
            if (session_hash !== undefined) {
                hash_key = session_hash;
            }
            else {
                if (window.sessionStorage['proctoring'] !== undefined) {
                    var session = TestSession.getSession();
                    if (session) {
                        hash_key = session.hash_key;
                    }
                }
            }
            return generic_api_call({
                'url': get_url('exam_register'),
                'method': 'GET',
                'params': {session: hash_key}
            });
        };

        this.start_all_exams = function(list){
            return generic_api_call({
                'url':  get_url('bulk_start_exam'),
                'method': 'POST',
                'data': JSON.stringify({list: list})
            });
        };

        this.get_archived_events = function(){
            return generic_api_call({
                'url': get_url('archived_event_session'),
                'method': 'GET'
            });
        };

        this.get_archived_sessions = function(event_hash){
            return generic_api_call({
                'url': get_url('archived_exam'),
                'method': 'GET',
                'params': {event_hash: event_hash}
            });
        };

        this.save_comment = function(code, comment){
            return generic_api_call({
                'url': get_url('comment'),
                'method': 'POST',
                'data': JSON.stringify({
                    comment: comment,
                    examCode: code
                })
            });
        };

        this.get_comments = function(attempt_code){
            return generic_api_call({
                'url': get_url('comment'),
                'method': 'GET',
                'params': {exam_code: attempt_code}
            });
        };
    }]);
})();
