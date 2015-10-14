'use strict';

(function () {
    angular.module('proctor').controller('MainCtrl', ['$scope', 'WS', function ($scope, WS) {
        $scope.ws_msg = function (obj) {

        };

        WS.init();
    }]);
})();