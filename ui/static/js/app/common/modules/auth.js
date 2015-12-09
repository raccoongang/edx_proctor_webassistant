'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', '$q', 'permissions', function($cookies, $q, permissions){
        var token = '';
        var username = $cookies.get('authenticated_user');
        var restrictions = null;

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined){
                token = c;
                $cookies.put('authenticated_token', undefined);
                return true;
            }
            return false;
        };

        this.get_token = function(){
            return token;
        };

        this.get_proctor = function(){
            return username;
        };

        this.is_proctor = function(){
            var deferred = $q.defer();
            if (token){
                permissions.get().then(function(data){
                    restrictions = data.data;
                    deferred.resolve(restrictions.role == 'proctor');
                }, function(){
                    deferred.resolve(false);
                });
            }
            return deferred.promise;
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