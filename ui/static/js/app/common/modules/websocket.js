(function () {
    angular.module('websocket', []).factory('WS', ['$rootScope', function ($rootScope) {
        var ws, ws_params = {}, ws_msg = null;

        var init = function (subcribe, callback, reconnect) {
            ws_params.channel = subcribe;
            ws_params.callback = callback;
            if (["function", "object"].indexOf(typeof window.WebSocket) >= 0){
                var protocol = 'ws://';
                if("https:" == document.location.protocol){
                    protocol = 'wss://';
                }
                ws = new WebSocket(
                    protocol +
                    $rootScope.apiConf.ioServer +
                    '/ws/' +
                    subcribe +
                    '?subscribe-broadcast&echo'
                );
            }
            else {
                ws = {};
            }
            ws.onopen = function () {
                console.log("Websocket connected");
            };
            ws.onmessage = function (e) {
                try {
                    ws_msg = JSON.parse(e.data);

                    callback(ws_msg);
                }
                catch (err) { }
            };
            ws.onerror = function (e) {
                console.log(e);
            };
            ws.onclose = function (e) {
                console.log("Websocket connection closed");
                if (reconnect !== undefined && reconnect === true) {
                    init(subcribe, callback, reconnect);
                }
            };
            $rootScope.$on('$locationChangeStart', function (event, next, current) {
                init(ws_params.channel, ws_params.callback, false);
                ws.close();
            });
        };

        return {
            init: init
        };
    }]);
})();