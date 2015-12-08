'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', 'permissions', function($cookies, permissions){
        var token = '';
        var username = $cookies.get('authenticated_user');

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined){
                token = c;
                $cookies.put('authenticated_token', undefined);
                permissions.get().then(function(data){
                    console.log(data);
                });
            }
            //else {
            //    var cookies = $cookies.getAll();
            //    angular.forEach(cookies, function (v, k) {
            //        $cookies.remove(k);
            //    });
            //    window.location = window.app.loginUrl;
            //}
        };

        this.get_token = function(){
            return token;
        };

        this.get_proctor = function(){
            return username;
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