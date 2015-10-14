'use strict';

(function () {
    angular.module('proctor').controller('MainCtrl', ['$scope', 'WS', 'Api', function ($scope, WS, Api) {

        $scope.ws_data = {};

        WS.init('attempts');

        $scope.$watch(function () {
            return WS.get_msg();
        }, function (val) {
            if (val) {
                var idx = val['hash'];
                $scope.ws_data[idx] = val;
                $scope.ws_data[idx]['status'] = '';
            }
        });

        $scope.accept_exam_attempt = function (code) {
            Api.accept_exam_attempt(code)
                .success(function (data) {
                    $scope.ws_data[data['hash']]['status'] = data['status'];
                })
                .error(function (data) {

                });
        };
    }]);
})();