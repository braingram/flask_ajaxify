var Ajaxify = function() {
    this.url = '/ajaxify';  // default url
    this.datum = {};  // last received datum
    this.request = {};  // last sent request
    this.send = function (options) {
        /*
         *  options is an object that should contain
         *
         *  at least (required):
         *
         *      - func or attr (string)
         *          function or attribute to fetch
         *
         *      - callback (function)
         *          callback to be called when ajax request returns
         *          will be called with arguments
         *
         *              - status (int)
         *                  0 = no error, otherwise error
         *                  1 = python error
         *                  2 = javascript error during ajax send
         *              - result (string, json encoded)
         *                  result of function or attribute call
         *              - error (string)
         *                  error message
         *
         *  and optionally (optional):
         *
         *      - args (string, json list)
         *          arguments to pass to the function
         *
         *      - kwargs (string, json object)
         *          keyword arguments to pass to the function
         *
         *      - url (string)
         *          ajax url
         *
         *  If options.url is not provided, this.url will be used instead
         *  if this.url is also undefined, an exception will be thrown
         */
        this.request = $.extend({}, options);  // store last request
        if (options.callback === undefined) {
            throw "Callback was undefind";
        };
        callback = options.callback;
        try {
            // using foo = options.foo || default; will give
            // default on 0 or false, etc. which is 'ok' here
            func = options.func || '';
            attr = options.attr || '';
            args = options.args || '[]';
            kwargs = options.kwargs || '{}';
            if (!options.url) {
                if (!this.url) {
                    throw 'url was undefined';
                } else {
                    url = this.url;
                };
            } else {
                url = options.url;
            };

            if ((func != '') & (attr != '')) {
                throw 'either func[' + func + '] and attr[' + attr + '] must be empty';
            };
            if ((func == '') & (attr == '')) {
                throw 'neither func nor attr was provided';
            };
            // test if args and kwargs are valid json
            args = $.parseJSON(args);
            kwargs = $.parseJSON(kwargs);
            if (func == '') {
                data = {
                    attr: attr,
                };
            } else {
                data = {
                    func: func,
                    args: $.toJSON(args),
                    kwargs: $.toJSON(kwargs),
                };
            };
            $.getJSON(url, data, function(data) {
                    this.datum = data;  // store last datum
                    callback(data.status, data.result, data.error);
                    });
        } catch (error) {
            callback(2, '', 'JS: ' + error.message);
        };
    };
    return this;
}();
