'use strict';

(function () {
    angular.module('proctor').controller('MainCtrl', ['$scope', 'WS', 'Api', function ($scope, WS, Api) {

        $scope.ws_data = {};

        $scope.websocket_callback = function(msg){
            if (msg) {
                var idx = msg['hash'];
                $scope.ws_data[idx] = msg;
                $scope.ws_data[idx]['status'] = '';
                $scope.$apply();
            }
        };

        WS.init('attempts', $scope.websocket_callback);

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