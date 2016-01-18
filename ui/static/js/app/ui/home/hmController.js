'use strict';

(function () {
    angular.module('proctor').controller(
        'MainCtrl', ['$scope', '$interval', '$location',
            '$q', '$route', 'WS', 'Api', 'Auth', 'i18n',
            'NgTableParams', '$uibModal',
            'TestSession', 'wsData', 'Polling',
            'DateTimeService', 'students',
            function ($scope, $interval, $location, $q, $route, WS, Api, Auth, i18n,
                      NgTableParams, $uibModal, TestSession, wsData, Polling, DateTimeService, students) {

                var session = TestSession.getSession();

                if (session) {
                    $interval(function () {
                        $scope.session_duration = TestSession.getSessionDuration();
                    }, 1000);
                }

                $scope.ws_data = [];

                // Update table with students attempts on next new attempt
                $scope.$watch(
                    function() {
                        return wsData.attempts;
                    },
                    function(new_val) {
                        $scope.ws_data = angular.copy(new_val);
                        $scope.tableParams.reload();
                    },
                    true
                );

                // get student exams from session
                if (students !== undefined) {
                    angular.forEach(students.data, function (attempt) {
                        // restore attempt comments
                        Api.get_comments(attempt.examCode).then(function (data) {
                            var started_at = '', comments = data.data.results;
                            attempt.comments = [];
                            angular.forEach(comments, function (comment) {
                                var item = {
                                    comment: comment.comment,
                                    timestamp: comment.event_start,
                                    status: comment.event_status
                                };
                                attempt.comments.push(item);
                            });

                            if (attempt.actual_start_date) {
                                started_at = DateTimeService.get_localized_time_from_string(attempt.actual_start_date);
                            };

                            attempt.started_at = started_at;
                            attempt.status = attempt.attempt_status;
                            wsData.attempts.push(attempt);
                            Polling.add_item(attempt.examCode); // first item starts cyclic update
                        });
                    });
                }

                $scope.test_center = session.testing_center;
                $scope.course_name = session.course_name;
                $scope.exam_name = session.exam_name;
                $scope.exam_link = window.location.href + "session/" + session.hash_key;

                $scope.exams = {
                    checked: [],
                    ended: []
                };

                $scope.tableParams = new NgTableParams({
                    page: 1,
                    count: 10
                }, {
                    data: wsData.attempts
                });

                $scope.is_owner = function () {
                    return TestSession.is_owner();
                };

                var attempt_end = function (hash) {
                    Polling.stop(hash);
                };

                // Start websocket connection
                WS.init(session.hash_key, wsData.websocket_callback, true);

                $scope.accept_exam_attempt = function (exam) {
                    if (exam.accepted) {
                        Api.accept_exam_attempt(exam.examCode)
                            .success(function (data) {
                                if (data['status'] == 'OK') {
                                    Polling.add_item(exam.examCode);
                                }
                            });
                    }
                };

                $scope.stop_exam_attempt = function (exam) {
                    if (confirm(i18n.translate('STOP_ATTEMPT')) === true) {
                        Api.stop_exam_attempt(exam.examCode, exam.orgExtra.userID).then(function (data) {
                            if (data.data.status = 'submitted') {
                                $scope.add_review(exam, 'personal', $scope.attempt_review_callback);
                            }
                        }, function () {
                            alert(i18n.translate('STOP_EXAM_FAILED'));
                        });
                    }
                };

                $scope.add_review = function (exam, type, callback) {
                    var deferred = $q.defer();

                    if (exam.comments == undefined) {
                        exam.comments = [];
                    }

                    exam['review_type'] = type;

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
                        if (callback !== undefined)
                            callback(exam, data);
                        deferred.resolve(data);
                    }, function () {
                        deferred.reject();
                    });

                    return deferred.promise;
                };

                // When proctor adds any comment for single student's exam attempt
                $scope.attempt_review_callback = function (attempt, data) {
                    attempt.comments.push(data);
                    Api.save_comment(attempt.examCode,
                        {
                            "comments": data.comment,
                            "duration": 1,
                            "eventFinish": data.timestamp,
                            "eventStart": data.timestamp,
                            "eventStatus": data.status
                        }
                    );
                };

                $scope.send_review = function (exam, status) {
                    if (exam.status == 'submitted' && exam.review_sent !== true) {
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
                        angular.forEach(exam.comments, function (val, key) {
                            payload.desktopComments.push(
                                {
                                    "comments": val.comment,
                                    "duration": 1,
                                    "eventFinish": val.timestamp,
                                    "eventStart": val.timestamp,
                                    "eventStatus": val.status
                                }
                            );
                        });
                        Api.send_review(payload).success(function () {
                            var idx = 0;
                            while ($scope.ws_data[idx].examCode !== exam.examCode) {
                                idx++;
                            }
                            if (status == 'Clean')
                                wsData.attempts[idx].status = 'verified';
                            else if (status == 'Suspicious')
                                wsData.attempts[idx].status = 'rejected';
                            exam.review_sent = true;
                            attempt_end(exam.hash);
                        }).error(function () {
                            alert(i18n.translate('REVIEW_SEND_FAILED') + " " + exam.examCode);
                        });
                    }
                };

                $scope.check_all_attempts = function () {
                    var list = [];
                    angular.forEach($scope.ws_data, function (val) {
                        if (!list.in_array(val.examCode)) {
                            list.push(val.examCode);
                        }
                    });
                    $scope.exams.checked = angular.copy(list);
                };

                $scope.uncheck_all_attempts = function () {
                    $scope.exams.checked = [];
                };

                var there_are_not_reviewed_attempts = function () {
                    var list = [];
                    angular.forEach($scope.ws_data, function (val) {
                        if (!['verified', 'rejected', 'error', 'timed_out'].in_array(val.status)) {
                            list.push(val.hash);
                        }
                    });
                    return list.length > 0;
                };

                $scope.end_session = function () {
                    if (!there_are_not_reviewed_attempts()) {
                        $scope.add_review({}, 'session').then(function (data) {
                            TestSession.endSession(data.comment).then(function () {
                                delete window.sessionStorage['proctoring'];
                                Polling.stop_all();
                                wsData.clear();
                                $location.path('/session');
                            }, function () {
                            });
                        }, function () {
                            alert(i18n.translate('EVENT_COMMENT_ERROR'));
                        });
                    }
                    else {
                        alert(i18n.translate('NOT_REVIEWED_SESSIONS'));
                    }
                };

                var get_not_started_attempts = function () {
                    var list = [];
                    angular.forEach($scope.ws_data, function (val, key) {
                        if (val.status == undefined || !val.status || val.status == 'created') {
                            if ($scope.exams.checked.in_array(val.examCode)) {
                                list.push(val.examCode);
                            }
                        }
                    });
                    return list;
                };

                $scope.start_all_attempts = function () {
                    if (confirm(i18n.translate('APPROVE_ALL_STUDENTS')) === true) {
                        Api.start_all_exams(get_not_started_attempts()).then(function () {
                            angular.forEach($scope.exams.checked, function (val, key) {
                                Polling.add_item(val);
                            });
                        });
                    }
                };

                var get_items_to_stop = function () {
                    var list = [];
                    angular.forEach($scope.exams.checked, function (val, key) {
                        var item = $scope.ws_data.filterBy({examCode: val});
                        if (item.length) {
                            if (!['verified', 'rejected', 'submitted'].in_array(item[0].status)) {
                                list.push({user_id: item[0].orgExtra.userID, attempt_code: val});
                            }
                        }
                    });
                    return list;
                };

                $scope.end_all_attempts = function () {
                    if (confirm(i18n.translate('STOP_ALL_ATTEMPTS')) === true) {
                        var list = get_items_to_stop();
                        if (list.length){
                            Api.stop_all_exam_attempts(list).then(function () {
                                $scope.add_review({}, 'common').then(function (data) {
                                    data.status = i18n.translate('COMMENT').toString();
                                    angular.forEach(list, function (val, key) {
                                        var res = $scope.ws_data.filterBy({examCode: val.attempt_code})[0];
                                        if (res.comments == undefined) {
                                            res.comments = [];
                                        }
                                        res.comments.push(data);
                                        Api.save_comment(val.attempt_code,
                                            {
                                                "comments": data.comment,
                                                "duration": 1,
                                                "eventFinish": data.timestamp,
                                                "eventStart": data.timestamp,
                                                "eventStatus": data.status
                                            }
                                        );
                                    });
                                });
                            }, function () {
                                alert(i18n.translate('STOP_EXAMS_FAILED'));
                            });
                        }
                    }
                };

                $scope.accept_student = function (exam) {
                    exam.accepted = true;
                };

                $scope.show_comments = function (exam) {
                    if (exam.comments.length) {
                        var deferred = $q.defer();

                        var modalInstance = $uibModal.open({
                            animation: true,
                            templateUrl: 'comments.html',
                            controller: 'CommentCtrl',
                            size: 'lg',
                            resolve: {
                                exam: exam
                            }
                        });

                        modalInstance.result.then(function () {
                            deferred.resolve();
                        });

                        return deferred.promise;
                    }
                };
            }]);

    angular.module('proctor').controller('ReviewCtrl', function ($scope, $uibModalInstance, TestSession, DateTimeService, i18n, exam) {
        $scope.exam = exam;
        var session = TestSession.getSession();
        $scope.exam.course_name = session.course_name;
        $scope.exam.exam_name = session.exam_name;
        $scope.available_statuses = [];
        if (exam.review_type == 'common') {
            $scope.available_statuses = [
                i18n.translate('COMMENT')
            ];
        }
        else if (exam.review_type == 'personal') {
            $scope.available_statuses = [
                i18n.translate('COMMENT').toString(),
                i18n.translate('SUSPICIOUS').toString()
            ];
        }
        $scope.comment = {
            status: $scope.available_statuses.length ? $scope.available_statuses[0] : '',
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

        $scope.i18n = function (text) {
            return i18n.translate(text);
        };

        $scope.get_date = function () {
            return DateTimeService.get_now_date();
        };

        $scope.get_time = function () {
            return DateTimeService.get_now_time();
        };
    });

    angular.module('proctor').controller('CommentCtrl', function ($scope, $uibModalInstance, DateTimeService, i18n, exam) {
        $scope.comments = exam.comments;

        $scope.ok = function () {
            $uibModalInstance.close();
        };

        $scope.i18n = function (text) {
            return i18n.translate(text);
        };

        $scope.get_date = function (timestamp) {
            return DateTimeService.get_localized_date_from_timestamp(timestamp);
        };
    });
})();
