'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', '$q', '$http', 'permissions', function($cookies, $q, $http, permissions){
        var token = '';
        var username = $cookies.get('authenticated_user');
        var restrictions = null;

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined && c){
                token = c;
                $cookies.put('authenticated_token', undefined);
                return true;
            }
            return false;
        };

        this.get_token = function(){
            if (token)
                return token;
            else
                return $cookies.get('authenticated_token');
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

        this.get_profile = function(){
            if (token){
                $http({
                    url: "https://sso.test.npoed.ru/api/me"
                });
            }
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