'use strict';

(function(){
    angular.module('proctor').service('Api', ['$rootScope', '$http', function($http, $rootScope){
        var url = function(call){
            return $rootScope.apiConf.apiServer + '/' + call + '/';
        };

        this.accept_exam_attempt = function(code){
            return $http({
                url:  url('start_exam') + code,
                method: 'GET'
            });
        };
    }]);
})();