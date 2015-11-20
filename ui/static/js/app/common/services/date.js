(function(){
    var app = angular.module('proctor');
    app.service('DateTimeService', function($rootScope, $interval){
        var ticker = null;
        var self = this;

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
            console.log(app.language.current);
            ticker = $interval(function(){
                self.value = localDate(app.language.current);
            }, 1000);
        };

        this.stop_timer = function(){
            $interval.cancel(ticker);
            ticker = null;
        };

        $rootScope.$watch(function(){
            return app.language.current;
        }, function(){
            console.log(restarting timer);
            if (ticker) {
                self.stop_timer();
                self.start_timer();
            }
        }, true);
    });
})();
