'use strict';

(function () {
    angular.module('proctor').controller(
        'MainCtrl', ['$scope', '$interval', 'WS', 'Api', 'NgTableParams', '$uibModal', 'TestSession',
            function ($scope, $interval, WS, Api, NgTableParams, $uibModal, TestSession) {

                var session = TestSession.getSession();

                $scope.ws_data = [];
                $scope.test_center = session.testing_center;
                $scope.course_name = session.course_name;
                $scope.exam_name = session.exam_name;

                $scope.websocket_callback = function (msg) {
                    if (msg && msg['examCode']) {
                        $scope.ws_data.push(angular.copy(msg));
                        $scope.$apply();
                    }
                };

                WS.init(session.hash_key, $scope.websocket_callback, true);

                var update_status = function (idx, status) {
                    var obj = $.grep($scope.ws_data, function(e){
                        return e.hash == idx;
                    });
                    if (obj.length > 0) {
                        obj[0]['status'] = status;
                    }
                };

                $scope.accept_exam_attempt = function (code) {
                    Api.accept_exam_attempt(code)
                        .success(function (data) {
                            update_status(data['hash'], data['status']);
                            if (data['status'] == 'OK') {
                                $interval(function () {
                                    Api.get_exam_status(code)
                                        .success(function (data) {
                                            update_status(data['hash'], data['status']);
                                        })
                                }, 1500);
                            }
                        })
                        .error(function (data) {

                        });
                };

                $scope.send_review = function (code) {
                    Api.send_review(code).success(function(){
                        var idx = 0;
                        while ($scope.ws_data[idx].examCode !== code) {
                            idx++;
                        }
                        $scope.ws_data.splice(idx, 1);
                    });
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
                    data: $scope.ws_data
                });

                $scope.$watch('ws_data', function(newValue, oldValue) {
                    if (newValue!=oldValue){
                        $scope.tableParams.reload();
                    }
                }, true);
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
