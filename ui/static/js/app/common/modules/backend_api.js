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

        this.stop_exam_attempt = function(code){
            return generic_api_call({
                'url':  get_url('stop_exam') + code,
                'method': 'PUT',
                'data': JSON.stringify({})
            });
        };

        this.get_exam_status = function(code){
            return generic_api_call({
                'url':  get_url('poll_status') + code,
                'method': 'GET'
            });
        };

        this.send_review = function(code, status){
            return generic_api_call({
                'url':  get_url('review'),
                'method': 'POST',
                data: JSON.stringify({attempt_code: code}),
                params: {status: status}
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
                return generic_api_call({
                    'url':  get_url('exam_register'),
                    'method': 'GET',
                    params: {session: session?session.hash_key:''}
                });
            }
        };

        this.start_all_exams = function(list){
            return generic_api_call({
                'url':  get_url('bulk_start_exam'),
                'method': 'POST',
                'data': JSON.stringify(list)
            });
        };
    }]);
})();
