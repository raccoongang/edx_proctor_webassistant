'use strict';

/**
 *
 * Main module of the application.
 */
(function () {
    var app = angular.module('proctor', []);
    app.config(function ($routeProvider, $controllerProvider, $compileProvider, $filterProvider, $provide, $httpProvider) {
        app.controllerProvider = $controllerProvider;
        app.compileProvider = $compileProvider;
        app.routeProvider = $routeProvider;
        app.filterProvider = $filterProvider;
        app.provide = $provide;

        delete $httpProvider.defaults.headers.common['X-Requested-With'];

        $routeProvider
            .when('/', {
                templateUrl: 'home/view.html',
                controller: 'MainCtrl',
                resolve: {
                    deps: function(resolver){
                        return resolver.load_deps('home/hmController.js');
                    }
                }
            })
            .otherwise({
                redirectTo: '/'
            });
    });

    app.run(function ($rootScope, $location) {
        var domain;
        var match = $location.absUrl().match(/(?:https?:\/\/)?(?:www\.)?(.*?)\//);
        if (match !== null)
            domain = match[1];
        var apiPort = 8000;
        $rootScope.apiConf = {
            domain: domain,
            ioServer: domain + ':' + apiPort,
            apiServer: 'http://' + domain + ':' + apiPort + '/api'
        };

        $rootScope.errors = null;
        $rootScope.msg = null;
    });

    angular.module('proctor').factory('resolver', function ($rootScope, $q, $timeout) {
        return {
            load_deps: function (dependencies, callback) {
                var deferred = $q.defer();
                $script(dependencies, function () {
                    $timeout(function () {
                        $rootScope.$apply(function () {
                            deferred.resolve();
                            if (callback !== undefined)
                                callback();
                        });
                    });
                });
                return deferred.promise;
            }
        };
    });


})();
