'use strict';

(function () {
    angular.module('proctor').controller(
        'MainCtrl', ['$scope',
                     '$interval',
                     '$location',
                     'WS',
                     'Api',
                     'i18n',
                     'NgTableParams',
                     '$uibModal',
                     'TestSession',
                     'students',
            function ($scope, $interval, $location, WS, Api, i18n, NgTableParams, $uibModal, TestSession, students) {

                var session = TestSession.getSession();

                $scope.ws_data = [];

                // get student exams from session
                if (students !== undefined){
                    angular.forEach(students.data, function(val, key){
                        $scope.ws_data.push(val);
                    });
                }

                $scope.test_center = session.testing_center;
                $scope.course_name = session.course_name;
                $scope.exam_name = session.exam_name;
                $scope.exams = {
                    checked: []
                };

                $scope.websocket_callback = function (msg) {
                    if (msg){
                        if (msg['examCode']) {
                            $scope.ws_data.push(angular.copy(msg));
                            $scope.$apply();
                            return;
                        }
                        if (msg['hash'] && msg['status']){
                            update_status(msg['hash'], msg['status']);
                        }
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

                $scope.accept_exam_attempt = function (exam) {
                    if (exam.accepted){
                        Api.accept_exam_attempt(exam.examCode)
                            .success(function (data) {
                                if (data['status'] == 'OK') {
                                    $interval(function () {
                                        Api.get_exam_status(exam.examCode);
                                    }, 1500);
                                }
                            });
                    }
                };

                $scope.send_review = function (code, status) {
                    Api.send_review(code, status).success(function(){
                        var idx = 0;
                        while ($scope.ws_data[idx].examCode !== code) {
                            idx++;
                        }
                        $scope.ws_data[idx].status = 'finished';
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

                $scope.check_all_student_sessions = function() {
                    var list = [];
                    angular.forEach($scope.ws_data, function(val, key){
                        list.push(val.examCode);
                    });
                    $scope.exams.checked = angular.copy(list);
                };

                $scope.uncheck_all_student_sessions = function() {
                    $scope.exams.checked = [];
                };

                $scope.end_session = function(){
                    TestSession.endSession().then(function(){
                        delete window.sessionStorage['proctoring'];
                        $location.path('/session');
                    }, function(){});
                };

                $scope.start_all_exams = function(){
                    if (confirm(i18n.translate('APPROVE_ALL_STUDENTS')) === true){
                        Api.start_all_exams($scope.exams.checked);
                    }
                };

                $scope.accept_student = function(exam){
                    exam.accepted = true;
                };
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
