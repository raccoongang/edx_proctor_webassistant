'use strict';
(function(){
    var app = angular.module('proctor');
    app.filter('hasaccess', function(){
        return function(arr) {
            var ret = [];
            angular.forEach(arr, function(val, key){
                ret.push(val.has_access === true);
            });
            return ret;
        };
    });
})();
