'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', 'permissions', function($cookies, permissions){
        var token = '';
        var username = $cookies.get('authenticated_user');
        var restrictions = [];

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined){
                token = c;
                $cookies.put('authenticated_token', undefined);
                permissions.get().then(function(data){
                    restrictions = data.data;
                });
            }
        };

        this.get_token = function(){
            return token;
        };

        this.get_proctor = function(){
            return username;
        };

        this.is_proctor = function(){
            console.log(restrictions.role, restrictions.role == 'proctor');
            return restrictions.role == 'proctor';
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