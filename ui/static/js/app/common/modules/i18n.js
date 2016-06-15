(function(){
    var module = angular.module('proctor.i18n', [
        'pascalprecht.translate',
        'ngSanitize'
    ]);

    module.service('i18n', function($sce, translateFilter){
        var language_cache = {};
        var div = document.createElement('div');

        this.translate = function(text) {
            if (language_cache[text] !== undefined) {
                return language_cache[text];
            }
            var translated = translateFilter(text);
            div.innerHTML = translated;
            var ret = $sce.trustAsHtml(div.textContent).toString();
            var res = ret == translated?translated:ret;
            res.replace(/_\*/g, '<b>').replace(/\*_/g, '</b>').replace(/_n_/g, '</br>');
            language_cache[text] = res;
            return res;
        };

        this.clear_cache = function(){
            language_cache = {};
        };
    });
})();