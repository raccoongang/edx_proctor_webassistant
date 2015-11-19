(function(){
    angular.module('sessionEvents', [])
        .service('TestSession', function(){
            var Session = null;

            this.registerSession = function(){

            };

            this.endSession = function(){

            };

            this.getSession = function(){
                return angular.copy(Session);
            };
        });
})();
