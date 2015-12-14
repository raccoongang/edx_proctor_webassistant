'use strict';
(function(){
    var app = angular.module('proctor');

    app.filter('hasaccess', function(){
        return function(arr, bool) {
            var ret = [];
            angular.forEach(arr, function(val){
                console.log(val.has_access, val.has_access == bool);
                ret.push(val.has_access == bool);
            });
            return ret;
        };
    });
})();
