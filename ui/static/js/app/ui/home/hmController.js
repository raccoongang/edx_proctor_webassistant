'use strict';

(function () {
    angular.module('proctor').controller(
        'MainCtrl', ['$scope', '$interval', 'WS', 'Api', 'NgTableParams', '$uibModal',
            function ($scope, $interval, WS, Api, NgTableParams, $uibModal) {

        $scope.ws_data = {};

        $scope.websocket_callback = function(msg){
            console.log("ws_callback", msg, msg['examCode'], msg && msg['examCode']);
            if (msg && msg['examCode']) {
                var idx = msg['hash'];
                $scope.ws_data[idx] = angular.copy(msg);
                $scope.ws_data[idx]['status'] = '';
                $scope.$apply();
            }
        };

        WS.init('attempts', $scope.websocket_callback, true);

        var update_status = function(idx, status){
            $scope.ws_data[idx]['status'] = status;
        };

        $scope.accept_exam_attempt = function (code) {
            Api.accept_exam_attempt(code)
                .success(function (data) {
                    update_status(data['hash'], data['status']);
                    if (data['status'] == 'OK') {
                        $interval(function(){
                            Api.get_exam_status(code)
                                .success(function(data){
                                    update_status(data['hash'], data['status']);
                                })
                        }, 1500);
                    }
                })
                .error(function (data) {

                });
        };

        $scope.send_review = function(code){
            Api.send_review(code);
        };

        $scope.add_review = function () {

            var modalInstance = $uibModal.open({
                animation: true,
                templateUrl: 'reviewContent.html',
                controller: 'ReviewCtrl',
                size: 'lg',
                resolve: {}
            });

            modalInstance.result.then(function (data) {
                console.log(data);
            }, function () {
                console.log('Modal dismissed at: ' + new Date());
            });
        };

        $scope.tableParams = new NgTableParams({
            page: 1,
            count: 10
        }, {
            data: function () {
                var data = [];
                angular.forEach($scope.ws_data, function(value, key){
                    data.push(value);
                });
                return data;
            }()
        });
    }]);

    angular.module('proctor').controller('ReviewCtrl', function ($scope, $uibModalInstance) {
        $scope.ok = function () {
            $uibModalInstance.close({});
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
    });
})();