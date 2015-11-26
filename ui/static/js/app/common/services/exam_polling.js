(function(){
    var app = angular.module('proctor');

    app.service('Polling', polling);

    function polling($interval, Api){
        var self = this;
        var attempts = [];
        var timer = null;

        var get_status = function(){
            // statuses will be updated through websocket channel
            return Api.get_exams_status(attempts);
        };

        this.stop = function(key){
            var idx = attempts.indexOf(key);
            if (idx >= 0){
                attempts.splice(idx, 1);
            }
        };

        this.stop_all = function(){
            $interval.cancel(timer);
        };

        this.start = function(){
            timer = $interval(function(){
                get_status();
            }, 2000);
        };

        this.add_item = function(key){
            if (attempts.length == 0){
                self.start();
            }
            attempts.push(key);
        };
    }

    polling.$inject = ['$interval', 'Api'];
})();