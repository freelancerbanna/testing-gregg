var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.charts = {};
ICMO.charts.premade = {};

ICMO.charts.periodChart = function ($el, userSettings, dataSource) {
    var defaults = {
            dataSource: {
                autoSync: false
            },
            title: {text: null},
            legend: {
                position: "top"
            },
            seriesDefaults: {
                overlay: {
                    gradient: null
                }
            },
            series: [],

            theme: "metro"
        },
        settings = $.extend({}, defaults, userSettings);
    if (dataSource != undefined) {
        settings.dataSource = dataSource;
    } else {
        settings.dataSource.transport = ICMO.core.getTransport($el, null);
        settings.dataSource.sort = {
            field: "order",
            dir: "asc"
        }
    }
    settings.dataSource.schema = ICMO.core.getSchema(ICMO.models.Period);
    $el.kendoChart(settings);
    return $el.data('kendoChart');
};

ICMO.charts.periodOverTimeChart = function ($el, userSettings, periodType, dataSource, userStartMonth, userEndMonth) {
    var defaults = {
            dataSource: {
                sort: {
                    field: "order",
                    dir: "asc"
                }
            },
            categoryAxis: {}
        },
        settings = $.extend({}, defaults, userSettings),
        startMonth = ICMO.core.getFirstMonth(userStartMonth),
        endMonth = ICMO.core.getLastMonth(userEndMonth);

    settings.categoryAxis.categories = ICMO.core.getPeriods(periodType, startMonth, endMonth);
    ICMO.core.setApiPeriodRange($el, settings.startMonth, settings.endMonth);
    return ICMO.charts.periodChart($el, settings, dataSource)
};


ICMO.charts.periodRadarChart = function ($el, title, series, dataSource, userSettings) {
    var defaults = {
            legend: {
                visible: false
            },
            title: {
                text: null
            },
            valueAxis: {
                visible: false
            },
            seriesDefaults: {
                type: "radarColumn",
                overlay: {
                    gradient: null
                }
            },
            tooltip: {
                visible: true,
                shared: true,
                format: "N0"
            }
        },
        settings = $.extend({}, defaults, userSettings);
    settings.series = series;
    settings.title.text = title;
    return ICMO.charts.periodChart($el, settings, dataSource)
};


ICMO.charts.bulletChart = function ($el, actual, plan, isCurrency, userSettings) {
    var defaults = {
            legend: {
                visible: false
            },
            chartArea: {
                margin: {
                    left: 0
                }
            },
            valueAxis: {
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: true
                },
                labels: {
                    format: "{0:n0}"
                }
            },
            series: [{
                data: []
            }],
            seriesDefaults: {
                type: "bullet",
                overlay: {
                    gradient: null
                }
            },
            tooltip: {
                visible: true,
                template: "Target: #= value.target # <br /> Actual: #= value.current #"
            },
            theme: 'metro'
        },
        settings = $.extend({}, defaults, userSettings);
    settings.series[0].data.push([actual, plan]);
    if (isCurrency) {
        settings.valueAxis.labels.format = "{0:c0}";
    }
    $el.kendoChart(settings);
    return $el.data('kendoChart');
};

ICMO.charts.periodVerticalBulletChart = function ($el, title, currentField, targetField, periodType, dataSource, userSettings) {
    var defaults = {
            legend: {
                visible: false
            },
            title: {
                text: null
            },
            chartArea: {
                margin: {
                    left: 0
                }
            },
            valueAxis: [{
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: true
                },
                labels: {
                    format: "{0:n0}"
                }
            }],
            series: [],
            seriesDefaults: {
                type: "verticalBullet",
                overlay: {
                    gradient: null
                },
                target: {
                    color: "#aaaaaa"
                }
            },
            categoryAxis: {
                majorGridLines: {
                    visible: false
                }
            },
            tooltip: {
                visible: true,
                template: "Target: #= value.target # <br /> Actual: #= value.current #"
            }
        },
        settings = $.extend({}, defaults, userSettings);
    settings.title.text = title;
    settings.series.push({currentField: currentField, targetField: targetField});

    if (currentField.indexOf('amount') >= 0) {
        settings.valueAxis[0].labels.format = "{0:c0}";
    }
    return ICMO.charts.periodOverTimeChart($el, settings, periodType, dataSource)
};


ICMO.charts.verticalBulletChart = function ($el, title, data, isCurrency) {
    var defaults = {
            legend: {
                visible: false
            },
            title: {
                text: null
            },
            dataSource: {
                data: null
            },
            chartArea: {
                margin: {
                    left: 0
                }
            },
            valueAxis: [{
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: true
                },
                labels: {
                    format: "{0:n0}"
                }
            }],
            series: [{
                type: "verticalBullet",
                
                currentField: "current",
                targetField: "target"
            }],
            seriesDefaults: {
                type: "verticalBullet",
                overlay: {
                    gradient: null
                },
                target: {
                    color: "#aaaaaa"
                },
                currentField: "current",
                targetField: "target"
            },
            categoryAxis: {
                majorGridLines: {
                    visible: false
                },
                field: 'category'
            },
            theme: "metro",
            tooltip: {
                visible: true,
                template: "Target: #= value.target # <br /> Actual: #= value.current #"
            }
        },
        settings = $.extend({}, defaults);
    settings.title.text = title;
    settings.dataSource.data = data;
    settings.categoryAxis.categories = ICMO.core.getPeriods('months', 'jan', 'dec');
    if (isCurrency) {
        settings.valueAxis[0].labels.format = "{0:c0}";
    }
    $el.kendoChart(settings);
    return $el.data('kendoChart');
};

ICMO.charts.simpleColumnChart = function ($el, title, values, categories, tooltipTemplate, userSettings) {
    var defaults = {
            legend: {
                visible: false
            },
            title: {text: title},
            valueAxis: {
                majorGridLines: {
                    visible: false
                },
                minorTicks: {
                    visible: false
                },
                labels: {
                    format: "{0:n0}"
                }
            },
            categoryAxis: {
                categories: categories,
                line: {
                    visible: false
                }
            },
            series: [{
                data: [],
                labels: {
                    visible: true,
                    position: "center",
                    format: "{0:n0}"
                }
            }],
            seriesDefaults: {
                type: "column",
                overlay: {
                    gradient: null
                }
            },
            tooltip: {
                visible: true,
                template: "#= value #"
            },
            theme: 'metro'
        },
        settings = $.extend({}, defaults, userSettings),
        isCurrency = isCurrency || false;
    if (isCurrency) {
        settings.valueAxis.labels.format = "{0:c0}";
    }
    settings.series[0].data = values;
    $el.kendoChart(settings);
    return $el.data('kendoChart');
};