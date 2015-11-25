(function(){
    var app = angular.module('proctor.date', []);
    app.service('DateTimeService', function($rootScope, $interval){
        var ticker = null;
        var self = this;

        String.prototype.toHHMMSS = function () {
            var sec_num = parseInt(this, 10); // don't forget the second param
            var hours   = Math.floor(sec_num / 3600);
            var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
            var seconds = sec_num - (hours * 3600) - (minutes * 60);

            if (hours   < 10) {hours   = "0"+hours;}
            if (minutes < 10) {minutes = "0"+minutes;}
            if (seconds < 10) {seconds = "0"+seconds;}
            var time    = hours+':'+minutes+':'+seconds;
            return time;
        }

        this.value = null;

        var date_options = {
            year: 'numeric', month: 'long',  day: 'numeric',
            weekday: 'long', hour: 'numeric', minute: 'numeric', second: 'numeric'
        };

        var localDate = function(loc){
            var d = new Date();
            return d.toLocaleString(loc, date_options);
        };

        this.start_timer = function(){
            ticker = $interval(function(){
                self.value = localDate(app.language.current);
            }, 1000);
        };

        this.stop_timer = function(){
            $interval.cancel(ticker);
            ticker = null;
        };

        this.get_now_diff_from_string = function(date_str){
            var diff = parseInt((Date.now() - Date.parse(date_str))/1000);
            return ("" + diff).toHHMMSS();
        };

        $rootScope.$watch(function(){
            return app.language.current;
        }, function(){
            if (ticker) {
                self.stop_timer();
                self.start_timer();
            }
        }, true);
    });
})();
