'use strict';

/**
 *
 * Main module of the application.
 */
(function () {
    var app = angular.module('proctor', [
        'ngRoute',
        'ngCookies',
        'ngAnimate',
        'ngSanitize',
        'ngTable',
        'ui.bootstrap',
        'websocket',
        'pascalprecht.translate'
    ]);
    app.config(function ($routeProvider,
                         $controllerProvider,
                         $locationProvider,
                         $compileProvider,
                         $filterProvider,
                         $provide,
                         $httpProvider,
                         $translateProvider,
                         $translateLocalStorageProvider
    ) {
        app.controller = $controllerProvider.register;
        app.directive = $compileProvider.directive;
        app.routeProvider = $routeProvider;
        app.filter = $filterProvider.register;
        app.service = $provide.service;
        app.factory = $provide.factory;

        app.path = window.app.rootPath;

        delete $httpProvider.defaults.headers.common['X-Requested-With'];

        // I18N
        $translateProvider.useStaticFilesLoader({
            prefix: app.path + 'i18n/',
            suffix: '.json'
        });
        $translateProvider.preferredLanguage('en');
        $translateProvider.useSanitizeValueStrategy('sanitize');
        $translateProvider.useLocalStorage();

        $provide.decorator('uibModalBackdropDirective', function($delegate) {
            $delegate[0].templateUrl = app.path + 'ui/partials/modal/backdrop.html';
            return $delegate;
        });
        $provide.decorator('uibModalWindowDirective', function($delegate) {
            $delegate[0].templateUrl = app.path + 'ui/partials/modal/window.html';
            return $delegate;
        });

        $routeProvider
            .when('/', {
                templateUrl: app.path + 'ui/home/view.html',
                controller: 'MainCtrl',
                resolve: {
                    deps: function(resolver){
                        return resolver.load_deps([
                            app.path + 'ui/home/hmController.js',
                            app.path + 'ui/home/hmDirectives.js',
                            app.path + 'common/services/backend_api.js'
                        ]);
                    }
                }
            })
            .otherwise({
                redirectTo: '/'
            });
    });

    app.run(['$rootScope', '$location', function ($rootScope, $location) {
        var domain;
        var match = $location.absUrl().match(/(?:https?:\/\/)?(?:www\.)?(.*?)\//);
        if (match !== null)
            domain = match[1];
        var api_port = '', socket_port = '';
        $rootScope.apiConf = {
            domain: domain,
            ioServer: domain + (socket_port?':' + socket_port:''),
            apiServer: 'http://' + domain + (api_port?':' + api_port:'') + '/api'
        };
    }]);

    app.factory('resolver', function ($rootScope, $q, $timeout) {
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

    // MAIN CONTROLLER
    app.controller('MainController', ['$scope', '$translate', function($scope, $translate){
        $scope.supported_languages = ['en', 'ru'];

        var lng_is_supported = function(val){
            return $scope.supported_languages.indexOf(val) >= 0?true:false;
        };

        $scope.changeLanguage = function (langKey) {
            if (lng_is_supported(langKey)) {
                $translate.use(langKey);
            }
        };

        $scope.logout = function(){
            window.location = window.app.logoutUrl;
        };
        //
        //$scope.get_lng_img = function(lng){
        //    if (lng_is_supported(lng)){
        //
        //    }
        //};
    }]);

    app.directive('header', [function(){
        return {
            restrict: 'E',
            templateUrl: app.path + 'ui/partials/header.html',
            link: function(scope, e, attr) {}
        };
    }]);

    app.filter('trusted', ['$sce', function($sce) {
        var div = document.createElement('div');
        return function(text) {
            div.innerHTML = text;
            return $sce.trustAsHtml(div.textContent);
        };
    }]);

})();
