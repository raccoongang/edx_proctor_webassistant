Array.prototype.in_array = function (val){
    return this.indexOf(val) >= 0;
};

Array.prototype._filter = function(params){
    return $.grep(this, function(e){
        var is = true;
        angular.forEach(params, function(val, key){
            is = is && e[key] == val;
        });
        return is;
    });
};

