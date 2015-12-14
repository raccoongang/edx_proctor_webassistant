'use strict';
(function(){
    var app = angular.module('proctor');

    app.filter('hasaccess', function(){
        return function(arr) {
            var ret = [];
            angular.forEach(arr, function(val, key){
                console.log(val.has_access, val.has_access === true);
                ret.push(val.has_access === true);
            });
            return ret;
        };
    });
})();
