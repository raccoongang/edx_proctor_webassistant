(function(){
    var app = angular.module('proctor.date', ['pascalprecht.translate']);
    app.service('DateTimeService', function($rootScope, $interval){
        var ticker = null;
        var self = this;
        var default_lng = 'ru';

        String.prototype.toHHMMSS = function () {
            var sec_num = parseInt(this, 10); // don't forget the second param
            var hours   = Math.floor(sec_num / 3600);
            var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
            var seconds = sec_num - (hours * 3600) - (minutes * 60);

            if (hours   < 10) {hours   = "0"+hours;}
            if (minutes < 10) {minutes = "0"+minutes;}
            if (seconds < 10) {seconds = "0"+seconds;}
            return hours+':'+minutes+':'+seconds;
        };

        this.value = null;

        var datetime_options = {
            year: 'numeric', month: 'long',  day: 'numeric',
            weekday: 'long', hour: 'numeric', minute: 'numeric', second: 'numeric'
        };

        var short_datetime_options = {
            year: 'numeric', month: 'long',  day: 'numeric',
            hour: 'numeric', minute: 'numeric', second: 'numeric'
        };

        var time_options = {
            hour: 'numeric', minute: 'numeric', second: 'numeric'
        };

        var localDate = function(loc, options){
            var d = new Date();
            return d.toLocaleString(loc, (options !== undefined?options:datetime_options));
        };

        this.start_timer = function(){
            ticker = $interval(function(){
                var l = window.localStorage['NG_TRANSLATE_LANG_KEY'];
                self.value = localDate(l !== undefined?l:default_lng);
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

        this.get_diff_from_string = function(date_str1, date_str2){
            var diff = null;
            var d1 = Date.parse(date_str1)/1000;
            var d2 = Date.parse(date_str2)/1000;
            if (date_str1 && date_str2){
                if (d1 > d2){
                    diff = parseInt(d1 - d2);
                }
                else{
                    diff = parseInt(d2 - d1);
                }
                return ("" + diff).toHHMMSS();
            }
            else{
                return '';
            }
        };

        this.get_now_date = function(){
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth()+1; //January is 0!
            var yyyy = today.getFullYear();

            if(dd<10) {
                dd='0'+dd
            }

            if(mm<10) {
                mm='0'+mm
            }

            return dd+'.'+mm+'.'+yyyy;
        };

        this.get_now_time = function(){
            // Returns localized time based on `time_options`
            // Example: 3:45:07 PM
            return localDate(window.localStorage['NG_TRANSLATE_LANG_KEY'], time_options);
        };

        this.get_now_timestamp = function(){
            var d = new Date();
            return d.getTime();
        };

        this.get_localized_time_from_string = function(string){
            var date = new Date(Date.parse(string));
            return date.toLocaleString(
                window.localStorage['NG_TRANSLATE_LANG_KEY'],
                time_options
            );
        };

        this.get_localized_date_from_string = function(string){
            var date = new Date(Date.parse(string));
            return date.toLocaleString(
                window.localStorage['NG_TRANSLATE_LANG_KEY'],
                short_datetime_options
            );
        };

        this.get_localized_date_from_timestamp = function(timestamp){
            var date = new Date(timestamp);
            return date.toLocaleString(
                window.localStorage['NG_TRANSLATE_LANG_KEY'],
                short_datetime_options
            );
        };

        $rootScope.$watch(function(){
            if (window.localStorage['NG_TRANSLATE_LANG_KEY'] !== undefined){
                return window.localStorage['NG_TRANSLATE_LANG_KEY'];
            }
            else
                return default_lng;
        }, function(){
            if (ticker) {
                self.stop_timer();
                self.start_timer();
            }
        }, true);
    });

    app.filter('date_localize', function(DateTimeService) {
        return function(input) {
            return input?DateTimeService.get_localized_date_from_string(input):'';
        };
    });

    app.filter('date_localize_timestamp', function(DateTimeService) {
        return function(input) {
            return input?DateTimeService.get_localized_date_from_timestamp(input):'';
        };
    });
})();
