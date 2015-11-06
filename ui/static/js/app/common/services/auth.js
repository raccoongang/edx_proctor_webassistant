'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', function($cookies){
        var token = '';

        this.authenticate = function(){
            console.log($cookies);
            if ($cookies.authenticated_token !== undefined){
                token = $cookies.authenticated_token;
                $cookies.remove('authenticated_token');
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
    }]);
})();