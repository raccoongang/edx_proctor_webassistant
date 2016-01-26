(function(){
    angular.module('proctor')
        .service('wsData', function($route, TestSession, DateTimeService, Polling) {

            var self = this;

            this.attempts = [];

            var updateStatus = function (idx, status) {
                var obj = self.attempts.filterBy({hash: idx});
                if (obj.length > 0) {
                    if (obj[0].review_sent !== true)
                        obj[0]['status'] = status;
                }
            };

            var addAttempt = function (attempt) {
                if (!attempt.hasOwnProperty('comments')) {
                    attempt.comments = [];
                };
                self.attempts.push(angular.copy(attempt));
            };

            var recievedComments = function (msg) {
                var item = self.attempts.filterBy({hash: msg.hash});
                item = item.length ? item[0] : null;
                if (item) {
                    var comment = item.comments.filterBy({timestamp: msg.comments.timestamp});
                    if (!comment.length) {
                        item.comments.push(msg.comments);
                    }
                }
            };

            var pollStatus = function (msg) {
                var item = self.attempts.filterBy({hash: msg.hash});
                item = item.length ? item[0] : null;
                if (msg.status == 'started' && item && item.status == 'ready_to_start') {
                    // variable to display in view
                    item.started_at = DateTimeService.get_now_time();
                }
                updateStatus(msg['hash'], msg['status']);
                if (['verified', 'error', 'rejected'].in_array(msg['status'])) {
                    Polling.stop(hash);
                }
            };

            var endSession = function () {
                TestSession.flush();
                $route.reload();
            };

            this.websocket_callback = function(msg) {
                if (msg) {
                    if (msg.examCode) {
                        addAttempt(msg);
                        return;
                    }
                    if (msg['hash'] && msg.hasOwnProperty('comments')) {
                        recievedComments(msg);
                        return;
                    }
                    if (msg['hash'] && msg['status']) {
                        pollStatus(msg);
                        return;
                    }
                    if (msg.hasOwnProperty('end_session')) {
                        endSession();
                    }
                }
            };

            this.clear = function () {
                this.attempts = [];
            }
        });
})();
