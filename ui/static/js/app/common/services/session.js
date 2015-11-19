(function(){
    angular.module('sessionEvents', [])
        .service('TestSession', function($rootScope, $http, Auth){
            var Session = null;

            this.registerSession = function(){
                $http({
                    url: $rootScope.apiConf.apiServer + '/event_session/',
                    method: 'POST',
                    headers: {Authorization: "Token " + Auth.get_token()}
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
