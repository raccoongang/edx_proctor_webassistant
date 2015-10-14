(function () {
    angular.module('websocket', []).service('WS', ['$rootScope', function ($rootScope) {
        var ws, ws_msg, self = this;

        this.get_msg = function () {
            return ws_msg;
        };
        this.init = function (subcribe, callback) {
            if (["function", "object"].indexOf(typeof window.WebSocket) >= 0)
                ws = new WebSocket(
                    'ws://' +
                    $rootScope.apiConf.ioServer +
                    '/ws/' +
                    subcribe +
                    '?subscribe-broadcast&echo'
                );
            else {
                ws = {};
            }
            ws.onopen = function () {
                console.log("Websocket connected");
            };
            ws.onmessage = function (e) {
                try {
                    console.log(e.data);
                }
                catch (err) {
                    console.log(e.data);
                }
            };
            ws.onerror = function(e){
                console.log(e);
            };
            ws.onclose = function (e) {
                console.log("Websocket connection closed");
            };
            $rootScope.$on('$locationChangeStart', function (event, next, current) {
                ws.close();
            });
        };
    }]);
})();