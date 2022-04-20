var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.dashboards = {};
ICMO.apps.dashboards.premade = {};

ICMO.apps.dashboards.periodChart = (function () {
    var defaults = {
            dataSource: {
                autoSync: false,
                sort: {
                    field: "order",
                    dir: "asc"
                }
            },
            title: {text: null},
            legend: {
                visible: false
            },
            seriesDefaults: {
                type: "line",
                overlay: {
                    gradient: null
                }
            },
            series: [],
            categoryAxis: {
                crosshair: {
                    visible: true
                }
            },
            valueAxis: {
                labels: {
                    format: "c0"
                }
            },
            tooltip: {
                visible: true,
                shared: true,
                format: "N0",
                template: "#= category#<br/>#=value #"
            },
            theme: "metro"
        };
    return {
        create: function ($el, title, series, period_type, userChartType, dataSource) {
            var chartType = userChartType || 'line',
                settings = $.extend({}, defaults);
            if (dataSource != undefined) {
                settings.dataSource = dataSource;
            } else {
                settings.dataSource.transport = ICMO.core.getTransport($el, null);
            }
            settings.dataSource.schema = ICMO.core.getSchema(ICMO.models.Period);

            settings.seriesDefaults.type = chartType;
            settings.series = series;
            settings.title.text = title;
            return ICMO.charts.periodOverTimeChart($el, settings, period_type, settings.dataSource);
        }
    }

}());


ICMO.apps.dashboards.localDataChart = (function () {
    var defaults = {
        title: {
            text: "Lead Generation Programs vs Custom Budget Line Items"
        },
        legend: {
            visible: true,
            position: 'bottom'
        },
        seriesDefaults: {
            type: null
        },
        series: null,
        valueAxis: {
            line: {
                visible: false
            },
            minorGridLines: {
                visible: true
            },
            labels: {
                rotation: "auto"
            }
        },
        categoryAxis: {
            categories: null,
            majorGridLines: {
                visible: false
            }
        },
        tooltip: {
            visible: true,
            template: "#= series.name #: #= value #"
        },
        theme: "metro"
    };

    return {
        create: function ($el, title, series, categories, userChartType) {
            var chartType = userChartType || 'line',
                settings = $.extend({}, defaults);

            settings.title.text = title;
            settings.seriesDefaults.type = chartType;
            settings.series = series;
            settings.categoryAxis.categories = categories;

            $el.kendoChart(settings);
            $el.data('kendoChart');
        }
    }

}());

ICMO.apps.dashboards.premade = {

    budgetPlannedVsActualByMonth: function ($el) {
        ICMO.apps.dashboards.periodChart.create(
            $el,
            "Budget Planned vs Actual by Month",
            [{
                field: "budget_plan__amount",
                name: "Budget Planned"
            }, {
                field: "budget_actual__amount",
                name: "Budget Actual"
            }],
            'months'
        );
    },
    ROIMonthlyChart: function ($el) {
        ICMO.apps.dashboards.periodChart.create(
            $el,
            "ROI Planned vs Actual by Month",
            [{
                field: "roi_plan",
                name: "ROI Planned"
            }, {
                field: "roi_actual",
                name: "ROI Actual"
            }],
            'months'
        );
    },
    salesPlannedVsActualByMonth: function ($el) {
        ICMO.apps.dashboards.periodChart.create(
            $el,
            "Sales Planned vs Actual by Month",
            [{
                field: "sales_plan",
                name: "Sales Planned"
            }, {
                field: "sales_actual",
                name: "Sales Actual"
            }],
            'months'
        );
    },
    programVsCustomBudgetChart: function ($el, series_planned, series_actual) {
        ICMO.apps.dashboards.localDataChart.create(
            $el,
            "Budget Breakdown: Programs vs Other Items",
            [
                {name: "Budget Planned", data: series_planned},
                {name: "Budget Actual", data: series_actual}
            ],
            ["Programs", "Other Items"],
            "bar"
        );
    },
    budgetTotalChart: function ($el, budget_plan_amount, budget_actual_amount) {
        ICMO.apps.dashboards.localDataChart.create(
            $el,
            "Annual Total Budget: Plan vs Actual",
            [
                {name: "Budget Planned", data: [budget_plan_amount]},
                {name: "Budget Actual", data: [budget_actual_amount]}
            ],
            [],
            "column"
        );
    }
};


ICMO.apps.dashboards.summaryGrid = function ($el, userSettings, finishedCallback, userStartMonth, userEndMonth) {
    var itemTypes = ['plan', 'actual', 'variance'],
        defaults = {
            periodType: 'months',
            startMonth: ICMO.core.getFirstMonth(userStartMonth),
            endMonth: ICMO.core.getLastMonth(userEndMonth),
            nameField: {field: null, title: null, width: 300},
            field: null,
            fieldAggregate: 'sum',
            fieldValueSuffix: '', /* __amount, __currency, etc */
            fieldAggregateSuffix: '', /* __amount, __currency, etc */
            finishedCallback: null
        },
        settings = $.extend({}, defaults, userSettings),
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

    ICMO.core.setApiPeriodRange($el, settings.startMonth, settings.endMonth);
    ICMO.grid.create($el, ICMO.models.HorizontalPeriod, getDefaults(), getAggregates(), []);
    var grid = $el.data('kendoGrid');
    grid.bind('dataBound', function () {
        if (finishedCallback) {
            finishedCallback();
        }
    });
    return grid;
};

ICMO.apps.dashboards.growthChart = function ($el, values, categories, color) {
    var defaults = {
            legend: {
                visible: false
            },
            title: {visible: false},
            valueAxis: {
                visible: false,
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: false
                }
            },
            categoryAxis: {
                categories: categories,
                visible: false,
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: false
                },
                line: {
                    visible: false
                }
            },
            series: [{
                data: [],
                labels: {
                    visible: true,
                    position: "center",
                    format: "{0:n0}%",
                    color: "#666666"
                },
                color: color
            }],
            seriesDefaults: {
                type: "column",
                overlay: {
                    gradient: null
                },
                gap: .1
            },
            tooltip: {
                visible: true,
                template: "#= category #"
            },
            chartArea: {
                height: 100
            },
            theme: 'metro'
        },
        settings = $.extend({}, defaults),
        isCurrency = isCurrency || false;
    if (isCurrency) {
        settings.valueAxis.labels.format = "{0:c0}";
    }
    settings.series[0].data = values;
    $el.kendoChart(settings);
    return $el.data('kendoChart');
};


ICMO.apps.dashboards.growthGage = function ($el, target, previous, actual) {
    var defaults = {
            pointer: [{
                value: actual,
                color: "#62cdef",
                cap: {size: 0.15}
            }],
            scale: {
                max: target * 1.5,

                labels: {
                    format: "${0:n1}M",
                    position: 'outside'
                },
                ranges: [
                    {
                        from: 0,
                        to: previous,
                        color: "#c2282c"
                    },
                    {
                        from: previous,
                        to: target,
                        color: "#ff8f00"
                    },
                    {
                        from: target,
                        to: target * 1.5,
                        color: "#c6d741"
                    }
                ]
            },
            chartArea: {
                height: 100
            },
            theme: 'metro'
        },
        settings = $.extend({}, defaults);
    $el.kendoRadialGauge(settings);
    return $el.data('kendoChart');
};