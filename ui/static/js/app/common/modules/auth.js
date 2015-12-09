'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', 'permissions', function($cookies, permissions){
        var token = '';
        var username = $cookies.get('authenticated_user');
        var restrictions = null;

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined){
                token = c;
                $cookies.put('authenticated_token', undefined);
                restrictions =  permissions.get();
            }
        };

        this.get_token = function(){
            return token;
        };

        this.get_proctor = function(){
            return username;
        };

        this.is_proctor = function(){
            restrictions.then(function(data){
                console.log(data);
                return data.role == 'proctor';
            });
        };
    }]);

    module.factory('permissions', function($rootScope, $http){
        var get = function(){
            return $http({
                url: $rootScope.apiConf.apiServer + '/permission/',
                method: 'GET'
            });
        };

        return {
            get: get
        };
    });
})();