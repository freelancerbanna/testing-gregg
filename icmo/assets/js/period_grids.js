var ICMO = ICMO || {};
ICMO.periods = ICMO.apps.periods || {};


ICMO.periods.horizontalPeriodGrid = (function () {
    var settings = {},
        itemTypes = ['plan', 'actual', 'variance'],

        getValuesByTimePeriod = function (model, period, aggregate) {
            var value,
                is_aggregate = aggregate || false,
                output = {};
            $.each(itemTypes, function (idx, itemType) {
                value = model[getModelFieldName(period, itemType, is_aggregate)];
                if (is_aggregate) {
                    value = value[settings.fieldAggregate]
                }
                output[itemType] = value;
            });
            return output;
        },
        getModelFieldName = function (period, itemType, aggregate) {
            var is_aggregate = aggregate || false,
                fieldName = period + "_" + settings.field + "_" + itemType;
            if (is_aggregate) {
                fieldName += settings.fieldAggregateSuffix;
            } else {
                fieldName += settings.fieldValueSuffix;
            }
            return fieldName;
        },
        renderValueTemplate = function (model, period) {
            var template = kendo.template($('#summaryValueTemplate').html());
            return template(getValuesByTimePeriod(model, period));
        },
        renderFooterTemplate = function (model, period) {
            var template = kendo.template($('#summaryFooterTemplate').html());
            return template(getValuesByTimePeriod(model, period, true));
        },
        getDefaults = function () {
            var defaults = {
                columns: [
                    {
                        field: settings.nameField.field,
                        title: settings.nameField.title,
                        width: settings.nameField.width,
                        template: function (model) {
                            model.name = model[settings.nameField.field];
                            return kendo.template($('#summaryNameTemplate').html())(model)
                        },
                        footerTemplate: "<div width='100%' class='text-right'>Plan<br>Actual<br>Variance</div>",
                    }
                ]
            };
            $.each(ICMO.core.getPeriods(settings.periodType, settings.startMonth, settings.endMonth), function (idx, period) {
                var fieldName;
                if (settings.field.indexOf('__') > -1) {
                    fieldName = period + "_" + settings.field.split('__')[0] + "_actual" + "__" + settings.field.split('__')[1];
                } else {

                    fieldName = period + "_" + settings.field + "_actual";
                }

                defaults.columns.push({
                    field: fieldName,
                    title: period.charAt(0).toUpperCase() + period.slice(1),
                    template: function (model) {
                        return renderValueTemplate(model, period);
                    },
                    footerTemplate: function (model) {
                        return renderFooterTemplate(model, period);
                    }
                });
            });
            return defaults;
        },
        getAggregates = function () {
            var aggregates = [];
            $.each(ICMO.core.period_types[settings.periodType], function (idx, period) {
                $.each(itemTypes, function (idx, itemType) {
                    aggregates.push({
                        field: getModelFieldName(period, itemType, true),
                        aggregate: settings.fieldAggregate
                    });
                });
            });
            return aggregates;
        };

    return {
        create: function ($el, userSettings, finishedCallback, userStartMonth, userEndMonth) {
            var defaults = {
                periodType: 'months',
                startMonth: ICMO.core.getFirstMonth(userStartMonth),
                endMonth: ICMO.core.getLastMonth(userEndMonth),
                nameField: {field: null, title: null, width: 300},
                field: null,
                fieldAggregate: 'sum',
                fieldValueSuffix: '', /* __amount, __currency, etc */
                fieldAggregateSuffix: '', /* __amount, __currency, etc */
                finishedCallback: null
            };
            settings = $.extend({}, defaults, userSettings);
            ICMO.core.setApiPeriodRange($el, settings.startMonth, settings.endMonth);
            ICMO.grid.create($el, ICMO.models.HorizontalPeriod, getDefaults(), getAggregates(), []);
            var grid = $el.data('kendoGrid');
            grid.bind('dataBound', function () {
                if (finishedCallback) {
                    finishedCallback();
                }
            });
            return grid;
        }
    }
}());


ICMO.periods.periodGrid = (function () {
    var defaults = {
            dataSource: {pageSize: 100},
            pageable: false,
            editable: false,
            sortable: {mode:'multiple'},
            reorderable: true,
            resizable: true,
        },
        getColumns = function (fields, groupFields, mode) {
            var columns = [],
                column,
                isCurrencyField,
                isItemField,
                field;
            for (var i = 0; i < fields.length; i++) {
                field = fields[i];
                if (!ICMO.periods.columns[field]) {
                    console.log("Columns:  Couldn't find field " + field);
                    continue;
                }
                isCurrencyField = ICMO.periods.currencyFields.indexOf(field) > -1;
                isItemField = ICMO.periods.itemFields.indexOf(field) > -1;
                if (isItemField) {
                    column = $.extend({}, ICMO.periods.columns[field]);
                    if (groupFields && groupFields.indexOf(field) > -1) {
                        column.hidden = true;
                    }
                    columns.push(column);
                } else if (mode == 'consolidated') {
                    column = $.extend({}, ICMO.periods.columns[field]);
                    if (isCurrencyField) {
                        column.field += '_actual__amount';
                        column.template = "#:" + field + "_actual__localized_whole_number# / #:" + field + "_plan__localized_whole_number#";
                    } else {
                        column.field += "_actual";
                        column.template = "#:" + field + "_actual# / #:" + field + "_plan#";
                    }
                    columns.push(column);
                } else if (ICMO.periods.variants.indexOf(mode) > -1) {
                    var variant = mode;
                    column = $.extend({}, ICMO.periods.columns[field]);
                    if (isCurrencyField) {
                        column.field += '_' + variant + '__amount';
                        column.template = "#:" + field + "_" + variant + "__localized_whole_number#"
                    } else {
                        column.field += "_" + variant;
                    }
                    columns.push(column);

                } else {
                    for (var x = 0; x < ICMO.periods.variants.length; x++) {
                        column = $.extend({}, ICMO.periods.columns[field]);
                        column.field += "_" + ICMO.periods.variants[x];
                        column.title += " " + ICMO.core.toTitle(ICMO.periods.variants[x]);
                        if (isCurrencyField) {
                            column.field += '__amount';
                            column.template = "#:" + field + "_" + ICMO.periods.variants[x] + "__localized_whole_number#"
                        }
                        columns.push(column);
                    }
                }
            }
            return columns;
        },
        getAggregates = function (fields) {
            var aggregates = [],
                aggregate = {},
                isCurrencyField;
            for (var i = 0; i < fields.length; i++) {
                if (ICMO.periods.itemFields.indexOf(fields[i]) > -1) {
                    continue;
                }
                if (!ICMO.periods.aggregates[fields[i]]) {
                    console.log("Aggregates: Couldn't find field " + fields[i]);
                    continue;
                }
                isCurrencyField = ICMO.periods.currencyFields.indexOf(fields[i]) > -1;
                for (var x = 0; x < ICMO.periods.variants.length; x++) {
                    aggregate = {
                        field: fields[i] + "_" + ICMO.periods.variants[x],
                        aggregate: ICMO.periods.aggregates[fields[i]]
                    };
                    if (isCurrencyField) {
                        aggregate.field += '__amount';
                    }
                    aggregates.push(aggregate);
                }
            }
            return aggregates;
        },
        getGroups = function (groupFields, fields) {
            var groups = [];
            for (var i = 0; i < groupFields.length; i++) {
                groups.push({
                    field: ICMO.periods.columns[groupFields[i]].field,
                    aggregates: getAggregates(fields)
                })
            }
            return groups;
        };

    return {
        create: function ($el, fields, groupFields, consolidate) {
            var settings = $.extend({}, defaults);

            settings.columns = getColumns(fields, groupFields, consolidate);
            if (groupFields) {
                settings.dataSource.group = getGroups(groupFields, fields);
            }
            ICMO.grid.create($el, ICMO.models.Period, settings, getAggregates(fields), []);
            return $el.data('kendoGrid');
        }
    }
}());

ICMO.periods.aggregates = {
    budget: 'sum',
    sales_revenue: 'sum',
    contacts: 'sum',
    touches: 'sum',
    mql: 'sum',
    sql: 'sum',
    sales: 'sum',
    touches_per_contact: 'average',
    average_sale: 'average',
    touches_to_mql_conversion: 'average',
    mql_to_sql_conversion: 'average',
    sql_to_sale_conversion: 'average',
    cost_per_mql: 'average',
    cost_per_sql: 'average',
    roi: 'average'
};
ICMO.periods.currencyFields = [
    'budget', 'sales_revenue', 'cost_per_mql', 'cost_per_sql', 'average_sale'
];
ICMO.periods.itemFields = [
    'revenue_plan', 'segment', 'program', 'custom_budget_line_item', 'campaign'
];
ICMO.periods.variants = [
    'plan', 'actual', 'variance'
];
ICMO.periods.columns = {
    'revenue_plan': {
        field: 'revenue_plan_name',
        title: "Revenue Plan",
        template: "<b>#: revenue_plan_name #</b>",
        width: 130,
        attributes: {
            style: "border-right: 1px solid rgb(219,219,219) !important;"
        }
    },
    'segment': {
        field: 'segment_name',
        title: "Segment",
        template: "<b>#: segment_name #</b>",
        width: 130,
        attributes: {
            style: "border-right: 1px solid rgb(219,219,219) !important;"
        }
    },
    'program': {
        field: 'program_name',
        title: "Program",
        template: "<b>#: program_name #</b>",
        width: 130,
        attributes: {
            style: "border-right: 1px solid rgb(219,219,219) !important;"
        }
    },
    'custom_budget_line_item': {
        field: 'custom_budget_line_item_name',
        title: "Budget Line Item",
        template: "<b>#: custom_budget_line_item_name #</b>",
        width: 130,
        attributes: {
            style: "border-right: 1px solid rgb(219,219,219) !important;"
        }
    },
    'campaign': {
        field: 'campaign_name',
        title: "Campaign",
        template: "<b>#: campaign_name #</b>",
        width: 130,
        attributes: {
            style: "border-right: 1px solid rgb(219,219,219) !important;"
        }
    },
    touches_per_contact: {
        field: 'touches_per_contact',
        title: 'Touches Per Contact',
        format: '{0: # }',
        footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #</span>',
    },
    touches_to_mql_conversion: {
        field: 'touches_to_mql_conversion',
        title: 'Touches to MQL Conversion',
        format: "{0: #.#'%' }",
        footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
    },
    mql_to_sql_conversion: {
        field: 'mql_to_sql_conversion',
        title: 'MQL to SQL Conversion',
        format: "{0: #.#'%' }",
        footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>'
    },
    sql_to_sale_conversion: {
        field: 'sql_to_sale_conversion',
        title: 'SQL to Sale Conversion',
        format: "{0: #.#'%' }",
        footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
    },
    cost_per_mql: {
        field: 'cost_per_mql',
        title: 'Cost Per MQL',
        //footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">$#= kendo.toString(average, "n0") #</span>',
    },
    cost_per_sql: {
        field: 'cost_per_sql',
        title: 'Cost Per SQL',
        //footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">$#= kendo.toString(average, "n0") #</span>',
    },
    contacts: {
        field: 'contacts',
        title: 'Contacts',
        format: '{0: #,##}',
        footerTemplate: '<span title="Sum" data-placement="left" data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>'
    },

    touches: {
        field: 'touches',
        title: 'Touches',
        format: '{0: #,##}',
        footerTemplate: '<span title="Sum" data-placement="left" data-toggle="tooltip">#= kendo.toString(sum, "n0")#</span>'
    },
    mql: {
        field: 'mql',
        title: 'MQLs',
        format: '{0: #,##}',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0")#</span>'
    },
    sql: {
        field: 'sql',
        title: 'SQLs',
        format: '{0: #,##}',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>'
    },
    sales: {
        field: 'sales',
        title: 'Sales',
        format: '{0: #,##}',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>',
    },
    sales_revenue: {
        field: 'sales_revenue',
        title: 'Sales Revenue',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">$#= kendo.toString(sum, "n0") #</span>'
    },
    average_sale: {
        field: 'average_sale',
        title: 'Average Sale',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">$#= kendo.toString(average, "n0") #</span>'
    },
    budget: {
        field: 'budget',
        title: 'Program Budget',
        footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">$#= kendo.toString(sum, "n0") #</span>'
    },
    roi: {
        field: 'roi',
        title: 'ROI',
        footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
    }
};