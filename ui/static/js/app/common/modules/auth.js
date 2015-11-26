'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', function($cookies){
        var token = '';
        var username = $cookies.get('authenticated_user');

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined){
                token = c;
                $cookies.put('authenticated_token', undefined);
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
})();