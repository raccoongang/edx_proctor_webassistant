'use strict';

(function(){
    angular.module('proctor').service('Api', ['$rootScope', '$http', function($rootScope, $http){
        var get_url = function(call){
            return '' + $rootScope.apiConf.apiServer + '/' + call + '/';
        };

        this.accept_exam_attempt = function(code){
            return $http({
                'url':  get_url('start_exam') + code,
                'method': 'GET'
            });
        };

        this.get_exam_status = function(code){
            return $http({
                'url':  get_url('poll_status') + code,
                'method': 'GET'
            });
        };

        this.send_review = function(code){
            return $http({
                'url':  get_url('review'),
                'method': 'POST',
                data: JSON.stringify({attempt_code: code})
            });
        };
    }]);
})();