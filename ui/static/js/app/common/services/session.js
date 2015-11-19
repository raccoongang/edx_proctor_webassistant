(function(){
    angular.module('sessionEvents', [])
        .service('TestSession', function($rootScope, $http){
            var Session = null;

            this.registerSession = function(){
                $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'POST'
                }).then(function(data){
                    console.log(data);
                });
            };

            this.endSession = function(){

            };

            this.getSession = function(){
                return angular.copy(Session);
            };
        });
})();
