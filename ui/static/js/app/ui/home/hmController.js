'use strict';

(function () {
    angular.module('proctor').controller(
        'MainCtrl', ['$scope',
                     '$interval',
                     '$location',
                     'WS',
                     'Api',
                     'Auth',
                     'i18n',
                     'NgTableParams',
                     '$uibModal',
                     'TestSession',
                     'Polling',
                     'students',
            function ($scope, $interval, $location, WS, Api, Auth, i18n,
                      NgTableParams, $uibModal, TestSession, Polling, students) {

                var session = TestSession.getSession();

                if (session){
                    $interval(function(){
                        $scope.session_duration = TestSession.getSessionDuration();
                    }, 1000);
                }

                $scope.ws_data = [];

                // get student exams from session
                if (students !== undefined){
                    angular.forEach(students.data, function(val, key){
                        val.status = val.attempt_status;
                        $scope.ws_data.push(val);
                        if (['ready_to_start', 'started', 'ready_to_submit', 'submitted'].in_array(val.status)) {
                            Polling.add_item(val.hash); // first item starts cyclic update
                        }
                    });
                }

                $scope.test_center = session.testing_center;
                $scope.course_name = session.course_name;
                $scope.exam_name = session.exam_name;
                $scope.exams = {
                    checked: [],
                    ended: []
                };

                $scope.tableParams = new NgTableParams({
                    page: 1,
                    count: 10
                }, {
                    data: $scope.ws_data
                });

                var attempt_end = function(hash){
                    Polling.stop(hash);
                };

                var update_status = function (idx, status) {
                    var obj = $.grep($scope.ws_data, function(e){
                        return e.hash == idx;
                    });
                    if (obj.length > 0) {
                        obj[0]['status'] = status;
                    }
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
                            if (['verified', 'error', 'rejected'].in_array(msg['status'])) {
                                attempt_end();
                            }
                        }
                    }
                };

                WS.init(session.hash_key, $scope.websocket_callback, true);

                $scope.accept_exam_attempt = function (exam) {
                    if (exam.accepted){
                        Api.accept_exam_attempt(exam.examCode)
                            .success(function (data) {
                                if (data['status'] == 'OK') {
                                    Polling.add_item(data['hash']);
                                }
                            });
                    }
                };

                $scope.add_review = function (exam) {

                    if (exam.comments == undefined) {
                        exam.comments = [];
                    }

                    var modalInstance = $uibModal.open({
                        animation: true,
                        templateUrl: 'reviewContent.html',
                        controller: 'ReviewCtrl',
                        size: 'lg',
                        resolve: {
                            exam: exam
                        }
                    });

                    modalInstance.result.then(function (data) {
                        exam.comments.push(data);
                    }, function () { });
                };

                $scope.send_review = function (exam, status) {
                    var payload = {
                        "examMetaData": {
                            "examCode": exam.examCode,
                            "reviewedExam": true,
                            "proctor_username": Auth.get_proctor()
                        },
                        "reviewStatus": status,
                        "videoReviewLink": "",
                        "desktopComments": []
                    };
                    angular.forEach(exam.comments, function(val, key){
                        payload.desktopComments.push(
                            {
                                "comments": val.comment,
                                "duration": 88,
                                "eventFinish": 88,
                                "eventStart": 12,
                                "eventStatus": val.status
                            }
                        );
                    });
                    Api.send_review(payload).success(function(){
                        var idx = 0;
                        while ($scope.ws_data[idx].examCode !== exam.examCode) {
                            idx++;
                        }
                        $scope.ws_data[idx].status = 'finished';
                    }).error(function(){
                        alert(i18n.translate('REVIEW_SEND_FAILED') + " " + exam.examCode);
                    });
                };

                $scope.$watch('ws_data', function(newValue, oldValue) {
                    if (newValue!=oldValue){
                        $scope.tableParams.reload();
                    }
                }, true);

                $scope.check_all_student_sessions = function() {
                    var list = [];
                    angular.forEach($scope.ws_data, function(val, key){
                        if (val.status == undefined || !val.status){
                            list.push(val.examCode);
                        }
                    });
                    $scope.exams.checked = angular.copy(list);
                };

                $scope.uncheck_all_student_sessions = function() {
                    $scope.exams.checked = [];
                };

                $scope.end_session = function(){
                    TestSession.endSession().then(function(){
                        delete window.sessionStorage['proctoring'];
                        Polling.stop_all();
                        $location.path('/session');
                    }, function(){});
                };

                $scope.start_all_exams = function(){
                    if (confirm(i18n.translate('APPROVE_ALL_STUDENTS')) === true){
                        Api.start_all_exams($scope.exams.checked).then(function(){
                            angular.forEach($scope.exams.checked, function(val, key){
                                Polling.add_item(val);
                            });
                        });
                    }
                };

                $scope.end_all_exams = function(){};

                $scope.accept_student = function(exam){
                    exam.accepted = true;
                };
            }]);

    angular.module('proctor').controller('ReviewCtrl', function ($scope, $uibModalInstance, TestSession, DateTimeService, i18n, exam) {
        $scope.exam = exam;
        var session = TestSession.getSession();
        $scope.exam.course_name = session.course_name;
        $scope.exam.exam_name = session.exam_name;
        $scope.available_statuses = [i18n.translate('SUSPICIOUS')];
        $scope.comment = {
            status: $scope.available_statuses[0],
            message: ""
        };

        $scope.ok = function () {
            var ret = {
                timestamp: new Date(),
                comment: $scope.comment.message,
                status: $scope.comment.status
            };
            ret.timestamp = ret.timestamp.getTime();
            $uibModalInstance.close(ret);
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };

        $scope.i18n = function(text){
            return i18n.translate(text);
        };

        $scope.get_date = function(){
            return DateTimeService.get_now_date();
        };
    });
})();
