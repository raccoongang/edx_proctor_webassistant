'use strict';
(function(){
    var app = angular.module('proctor');
    app.directive('reviewModal', [function(){
        return {
            restrict: 'E',
            templateUrl: app.path + 'ui/partials/add_review.html',
            link: function(scope, e, attr) {}
        };
    }]);
})();
