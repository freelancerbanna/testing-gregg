var ICMO = ICMO || {};
ICMO.models = ICMO.models || {};
ICMO.wsURL = null;
ICMO.wsHeartbeat = null;
ICMO.core = (function () {
    var _context_menu_appended = false,
        _flattenObject = function (ob) {
            /* https://gist.github.com/gdibble/9e0f34f0bb8a9cf2be43 */
            var toReturn = {};
            var flatObject;
            for (var i in ob) {
                if (!ob.hasOwnProperty(i)) {
                    continue;
                }
                if ((typeof ob[i]) === 'object') {
                    flatObject = _flattenObject(ob[i]);
                    for (var x in flatObject) {
                        if (!flatObject.hasOwnProperty(x)) {
                            continue;
                        }
                        toReturn[i + (!!isNaN(x) ? '__' + x : '')] = flatObject[x];
                    }
                } else {
                    toReturn[i] = ob[i];
                }
            }
            return toReturn;
        },

        _unflattenObject = function (ob) {
            var toReturn = {};
            var keys;
            for (var i in ob) {
                if (!ob.hasOwnProperty(i)) {
                    continue;
                }
                if (i.indexOf('__') > -1) {
                    keys = i.split('__');
                    $.extend(true, toReturn, _nest(ob[i], keys));
                    _nest(ob[i], keys, toReturn);
                } else {
                    toReturn[i] = ob[i];
                }
            }
            return toReturn;
        },

        _nest = function (value, keys) {
            if (keys.length === 0) {
                return value;
            }
            var d = {};
            d[keys.shift()] = _nest(value, keys);
            return d;
        },
        centerNotification = function (e) {
            if (!$("." + e.sender._guid)[1]) {
                var element = e.element.parent(),
                    eWidth = element.width(),
                    eHeight = element.height(),
                    wWidth = $(window).width(),
                    wHeight = $(window).height(),
                    newTop, newLeft;

                newLeft = Math.floor(wWidth / 2 - eWidth / 2);
                newTop = Math.floor(wHeight / 2 - eHeight / 2);

                e.element.parent().css({top: newTop, left: newLeft});
            }
        };

    return {
        getDataSourceByURL: function (dataURL, model) {
            return new kendo.data.DataSource({
                autoSync: false,
                transport: ICMO.core.getTransportByURL(dataURL),
                schema: ICMO.core.getSchema(model)
            });
        },
        getTransport: function ($el, userDataField, userIdField) {
            var dataField = userDataField || 'api-url',
                dataURL = $el.data(dataField),
                userIdField = userIdField || $el.data('id-field') || 'slug';
            return ICMO.core.getTransportByURL(dataURL, userIdField, $el.attr('data-read-filter'));
        },
        getTransportByURL: function (userDataURL, userIdField, dataReadFilter) {
            var idField = userIdField || 'slug',
                dataReadFilter = dataReadFilter || false,
                dataURL=userDataURL.trim();
            return {
                push: function (options) {
                    //Listen to the "message" event fired when the server pushes data
                    $(document).on('wsmessage+' + dataURL, function (e, data) {
                        var result = JSON.parse(data),
                            objects = [];
                        if (!$.isArray(result)) {
                            objects.push(_flattenObject(result));
                        } else {
                            $.each(result, function (idx, elem) {
                                objects.push(_flattenObject(elem))
                            });
                        }
                        console.log('receiving');
                        console.log(objects);
                        $.each(objects, function (idx, obj) {
                            //Check what the push type is and invoke the corresponding callback.
                            if (obj.kendo_action == "push-update") {
                                console.log("Applying push update");
                                options.pushUpdate(obj);
                            } else if (obj.kendo_action == "push-destroy") {
                                console.log("Applying push delete");
                                options.pushDestroy(obj);
                            } else if (obj.kendo_action == "push-create") {
                                console.log("Applying push create");
                                options.pushCreate(obj);
                            }
                        });
                    });
                },
                create: {
                    url: function () {
                        return dataURL;
                    },
                    type: 'POST',
                    dataType: "json",
                    contentType: 'application/json'
                },
                read: {
                    url: function () {
                        var url = dataURL;
                        if (dataReadFilter) {
                            url += '?' + dataReadFilter;
                        }
                        return url;
                    },
                    type: "GET",
                    dataType: "json",
                    contentType: 'application/json'
                },
                update: {
                    url: function (options) {
                        return dataURL + options[idField] + "/";
                    },
                    dataType: "json",
                    type: 'PATCH',
                    contentType: 'application/json'
                },
                destroy: {
                    url: function (options) {
                        return dataURL + options[idField] + "/";
                    },
                    dataType: "json",
                    type: 'DELETE',
                    contentType: 'application/json'
                },
                parameterMap: function (options) {
                    return kendo.stringify(_unflattenObject(options));
                }
            }
        },
        getSchema: function (model) {
            return {
                model: model,
                parse: function (data) {
                    /* Flatten objects to simplify life with the grid */
                    var res = [];
                    if (!$.isArray(data)) {
                        return _flattenObject(data);
                    }
                    $.each(data, function (idx, elem) {
                        res.push(_flattenObject(elem))
                    });
                    return res;
                }
            }
        },
        showCenteredNotification: function (message) {
            var notificationWidget = $("#notification").kendoNotification({show: centerNotification}).data("kendoNotification");
            notificationWidget.show(message);
        },
        showNotification: function ($target, message) {
            var $notificationEl = $('#notification'),
                notificationWidget = $notificationEl.kendoNotification({
                    position: {
                        pinned: true,
                        left: $target.position().left + 30,
                        top: $target.position().top
                    }
                }).data("kendoNotification");
            notificationWidget.show(message);
        },
        refreshCharts: function (e) {
            var $el;
            if ($(e.target).hasClass('collapse')) {
                $el = $(e.target).closest('.tab-pane');
            } else {
                $el = $("#" + e.target.href.split("#")[1]);
            }
            $el.find('[data-role="chart"]').each(function (idx, item) {
                $(item).data('kendoChart').refresh();
            });
            $el.find('[data-role="radialgauge"]').each(function (idx, item) {
                $(item).data('kendoRadialGauge').redraw();
            });
        },
        refreshSplitters: function (e) {
            var $el;
            if ($(e.target).hasClass('collapse')) {
                $el = $(e.target).closest('.tab-pane');
            } else {
                $el = $("#" + e.target.href.split("#")[1]);
            }
            $el.find('[data-role="splitter"]').each(function (idx, item) {
                $(item).data('kendoSplitter').resize();
            });
        },
        value_types: [
            'plan', 'actual', 'variance'
        ],
        period_types: {
            months: ['jan', 'feb', 'mar', 'apr', 'may',
                'jun', 'jul', 'aug', 'sep', 'oct',
                'nov', 'dec'],
            quarters: ['q1', 'q2', 'q3', 'q4'],
            years: ['fiscal_year']
        },
        fiscal_months: ['jan', 'feb', 'mar', 'apr', 'may',
            'jun', 'jul', 'aug', 'sep', 'oct',
            'nov', 'dec'],
        fiscal_year_start: 1,
        monthNames: ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'],
        getCurrentMonthName: function () {
            var d = new Date();
            return ICMO.core.period_types['months'][d.getMonth()];
        },
        getPeriods: function (periodType, startMonth, endMonth) {
            var startMonthIndex = startMonth ? ICMO.core.fiscal_months.indexOf(startMonth) : 0,
                endMonthIndex = endMonth ? ICMO.core.fiscal_months.indexOf(endMonth) : 11;
            if (periodType == 'months') {
                return ICMO.core.fiscal_months.slice(startMonthIndex, endMonthIndex + 1);
            }
            return ICMO.core.period_types[periodType];
        },
        getFirstMonth: function (firstMonth) {
            return firstMonth ? firstMonth : ICMO.core.fiscal_months[0];
        },
        getLastMonth: function (lastMonth) {
            return lastMonth ? lastMonth : ICMO.core.fiscal_months[11];
        },
        setApiPeriodRange: function ($el, startMonth, endMonth) {
            $el.data('api-url', $el.data('api-url') + '&period_range=' + startMonth + '-' + endMonth);
        },
        hasChangePermission: false,
        toTitle: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
        createWebsocket: function (dataURL, endpoint) {
            //dataURL is just used as a unique id to ensure the transport
            //receives the correct message
            ICMO.core.ws4redis = WS4Redis({
                uri: ICMO.wsURL + endpoint + '?subscribe-broadcast&echo',
                receive_message: receiveMessage,
                heartbeat_msg: ICMO.wsHeartbeat
            });
            function receiveMessage(msg) {
                $(document).trigger('wsmessage+' + dataURL, msg);
            }
        },
        alertErrorAndRefresh: function () {
            bootbox.alert("There has been an error processing your request.  " +
                "Our support staff has been notified.  The page will now reload. " +
                " Please try your request again.",
                function () {
                    location.reload();
                }
            );
        }
    }
}());


ICMO.models.IcmoUser = kendo.data.Model.define({
    fields: {
        id: {
            from: "email",
            type: "string",
            editable: false
        },
        email: {
            type: "string",
            editable: false
        },
        employer: {
            type: "string",
            editable: false
        },
        first_name: {
            type: "string",
            editable: false
        },
        full_name: {
            editable: false,
            type: "string"
        },
        last_name: {
            type: "string",
            editable: false
        }
    },
    id: "id",
    idField: "id"
});


ICMO.models.Period = kendo.data.Model.define({
    fields: {
        average_sale_actual: {
            type: "string",
            editable: false
        },
        average_sale_plan: {
            type: "string",
            editable: false
        },
        average_sale_variance: {
            type: "string",
            editable: false
        },
        budget_actual: {
            type: "string",
            editable: false
        },
        budget_actual__amount: {
            type: "number",
            editable: false
        },
        budget_plan: {
            type: "string",
            editable: false
        },
        budget_plan__amount: {
            type: "number",
            editable: false
        },
        budget_variance: {
            type: "string",
            editable: false
        },
        budget_variance__amount: {
            type: "number",
            editable: false
        },
        campaign: {
            type: "string",
            editable: false
        },
        campaign_name: {
            type: "string",
            editable: false
        },
        company: {
            type: "string",
            editable: false
        },
        contacts_actual: {
            type: "number",
            editable: false
        },
        contacts_plan: {
            type: "number",
            editable: false
        },
        contacts_variance: {
            type: "number",
            editable: false
        },
        cost_per_mql_actual: {
            type: "string",
            editable: false
        },
        cost_per_mql_actual__amount: {
            type: "number",
            editable: false
        },
        cost_per_mql_plan: {
            type: "string",
            editable: false
        },
        cost_per_mql_plan__amount: {
            type: "number",
            editable: false
        },
        cost_per_mql_variance: {
            type: "string",
            editable: false
        },
        cost_per_mql_variance__amount: {
            type: "number",
            editable: false
        },
        cost_per_sql_actual: {
            type: "string",
            editable: false
        },
        cost_per_sql_actual__amount: {
            type: "string",
            editable: false
        },
        cost_per_sql_plan: {
            type: "string",
            editable: false
        },
        cost_per_sql_plan__amount: {
            type: "string",
            editable: false
        },
        cost_per_sql_variance: {
            type: "string",
            editable: false
        },
        cost_per_sql_variance__amount: {
            type: "string",
            editable: false
        },
        custom_budget_line_item: {
            type: "string",
            editable: false
        },
        custom_budget_line_item_name: {
            type: "string",
            editable: false
        },
        mql_actual: {
            type: "number",
            editable: false
        },
        mql_plan: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_actual: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_plan: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_variance: {
            type: "number",
            editable: false
        },
        mql_variance: {
            type: "number",
            editable: false
        },
        order:{
            type:"number",
            editable:false
        },
        period: {
            type: "string",
            editable: false
        },
        period_type: {
            type: "string",
            editable: false
        },
        program: {
            type: "string",
            editable: false
        },
        resolution: {
            type: "string",
            editable: false
        },
        revenue_plan: {
            type: "string",
            editable: false
        },
        roi_actual: {
            type: "number",
            editable: false
        },
        roi_plan: {
            type: "number",
            editable: false
        },
        roi_variance: {
            type: "number",
            editable: false
        },
        sales_actual: {
            type: "number",
            editable: false
        },
        sales_plan: {
            type: "number",
            editable: false
        },
        sales_variance: {
            type: "number",
            editable: false
        },

        segment: {
            type: "string",
            editable: false
        },
        sql_actual: {
            type: "number",
            editable: false
        },
        sql_plan: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_actual: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_plan: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_variance: {
            type: "number",
            editable: false
        },
        sql_variance: {
            type: "number",
            editable: false
        },
        sales_revenue_actual: {
            type: "string",
            editable: false
        },
        sales_revenue_actual__amount: {
            type: "number",
            editable: false
        },
        sales_revenue_plan: {
            type: "string",
            editable: false
        },
        sales_revenue_variance: {
            type: "string",
            editable: false
        },
        touches_actual: {
            type: "number",
            editable: false
        },
        touches_per_contact_actual: {
            type: "number",
            editable: false
        },
        touches_per_contact_plan: {
            type: "number",
            editable: false
        },
        touches_per_contact_variance: {
            type: "number",
            editable: false
        },
        touches_plan: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_actual: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_plan: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_variance: {
            type: "number",
            editable: false
        },
        touches_variance: {
            type: "number",
            editable: false
        }
    },
    idField: "id",
    id: "id"

});


ICMO.models.HorizontalPeriod = kendo.data.Model.define({
    fields: {
        average_sale_actual: {
            type: "string",
            editable: false
        },
        average_sale_plan: {
            type: "string",
            editable: false
        },
        average_sale_variance: {
            type: "string",
            editable: false
        },
        budget_actual: {
            type: "string",
            editable: false
        },
        budget_actual__amount: {
            type: "number",
            editable: false
        },
        budget_plan: {
            type: "string",
            editable: false
        },
        budget_plan__amount: {
            type: "number",
            editable: false
        },
        budget_variance: {
            type: "string",
            editable: false
        },
        budget_variance__amount: {
            type: "number",
            editable: false
        },
        campaign: {
            type: "string",
            editable: false
        },
        company: {
            type: "string",
            editable: false
        },
        contacts_actual: {
            type: "number",
            editable: false
        },
        contacts_plan: {
            type: "number",
            editable: false
        },
        contacts_variance: {
            type: "number",
            editable: false
        },
        cost_per_mql_actual: {
            type: "string",
            editable: false
        },
        cost_per_mql_plan: {
            type: "string",
            editable: false
        },
        cost_per_mql_variance: {
            type: "string",
            editable: false
        },
        cost_per_sql_actual: {
            type: "string",
            editable: false
        },
        cost_per_sql_plan: {
            type: "string",
            editable: false
        },
        cost_per_sql_variance: {
            type: "string",
            editable: false
        },
        custom_budget_line_item: {
            type: "string",
            editable: false
        },
        mql_actual: {
            type: "number",
            editable: false
        },
        mql_plan: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_actual: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_plan: {
            type: "number",
            editable: false
        },
        mql_to_sql_conversion_variance: {
            type: "number",
            editable: false
        },
        mql_variance: {
            type: "number",
            editable: false
        },
        period: {
            type: "string",
            editable: false
        },
        period_type: {
            type: "string",
            editable: false
        },
        program: {
            type: "string",
            editable: false
        },
        resolution: {
            type: "string",
            editable: false
        },
        revenue_plan: {
            type: "string",
            editable: false
        },
        roi_actual: {
            type: "number",
            editable: false
        },
        roi_plan: {
            type: "number",
            editable: false
        },
        roi_variance: {
            type: "number",
            editable: false
        },
        sales_actual: {
            type: "number",
            editable: false
        },
        sales_plan: {
            type: "number",
            editable: false
        },
        sales_variance: {
            type: "number",
            editable: false
        },
        segment: {
            type: "string",
            editable: false
        },
        segment_name: {
            type: "string",
            editable: false
        },
        sql_actual: {
            type: "number",
            editable: false
        },
        sql_plan: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_actual: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_plan: {
            type: "number",
            editable: false
        },
        sql_to_sale_conversion_variance: {
            type: "number",
            editable: false
        },
        sql_variance: {
            type: "number",
            editable: false
        },
        sales_revenue_actual: {
            type: "string",
            editable: false
        },
        sales_revenue_plan: {
            type: "string",
            editable: false
        },
        sales_revenue_variance: {
            type: "string",
            editable: false
        },
        touches_actual: {
            type: "number",
            editable: false
        },
        touches_per_contact_actual: {
            type: "number",
            editable: false
        },
        touches_per_contact_plan: {
            type: "number",
            editable: false
        },
        touches_per_contact_variance: {
            type: "number",
            editable: false
        },
        touches_plan: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_actual: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_plan: {
            type: "number",
            editable: false
        },
        touches_to_mql_conversion_variance: {
            type: "number",
            editable: false
        },
        touches_variance: {
            type: "number",
            editable: false
        }
    },
    idField: "id",
    id: "id"

});

$(function () {
    /* disable backspace */
    $(document).on("keydown", function (e) {
        var code = e.keyCode || e.which;
        if (code === 8 && !$(e.target).is("input, textarea")) {
            e.preventDefault();
        }
    });
}());
