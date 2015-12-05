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
            console.log(typeof translated, translated);
            div.innerHTML = translated;
            var ret = $sce.trustAsHtml(div.textContent).toString();
            language_cache[text] = ret;
            return ret == translated?translated:ret;
        };

        this.clear_cache = function(){
            language_cache = {};
        };
    });
})();