'use strict';

(function(){
    angular.module('proctorApi', []).service('Api', ['$rootScope', '$http', 'Auth', function($rootScope, $http, Auth){
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
    }]);
})();
