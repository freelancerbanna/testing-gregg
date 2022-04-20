var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};

ICMO.apps.performance = {
    renderCellTemplate: function (model, time_period) {
        var template = kendo.template($('#campaignSummaryValueTemplate').html());
        var values = ICMO.apps.performance.getCampaignValuesByTimePeriod(model, time_period);
        return template(values);
    },
    renderFooterTemplate: function (model, time_period) {
        var template = kendo.template($('#campaignSummaryFooterTemplate').html());
        var values = ICMO.apps.performance.getCampaignValuesByTimePeriod(model, time_period, true);
        return template(values);
    },
    getCampaignValuesByTimePeriod: function (model, time_period, sum) {
        var data_fields = ['mql', 'sql', 'sales', 'sales_revenue'],
            currency_fields = ['sales_revenue'],
            currency_subfields = ['amount', 'currency', 'localized', 'localized_whole_number'],
            output = {},
            modelField,
            sum = sum || false,
            suffix = "";
        if (model['jan_mql_actual'] !== undefined) {
            suffix = "_actual";
        }
        for (var x = 0; x < data_fields.length; x++) {
            modelField = time_period + "_" + data_fields[x] + suffix;
            if (currency_fields.indexOf(data_fields[x]) > -1) {
                for (var y = 0; y < currency_subfields.length; y++) {
                    output[data_fields[x] + "__" + currency_subfields[y]] = ICMO.apps.performance.getSumOrValue(model[modelField + "__" + currency_subfields[y]], sum);
                }
            } else {
                output[data_fields[x]] = ICMO.apps.performance.getSumOrValue(model[modelField], sum);
            }
        }
        return output;
    },
    getSumOrValue: function (obj, sum) {
        if (sum && obj && obj.sum !== undefined) {
            return kendo.toString(obj.sum, 'n0');
        } else {
            return obj;
        }
    },
    generateAggregators: function (suffix) {
        var output = [],
            suffix = suffix || "";
        $.each(ICMO.core.period_types, function (idx, period_type) {
            $.each(period_type, function (idx, period) {
                output.push({
                    field: period + '_cost' + suffix + '__amount',
                    aggregate: 'sum'
                });
                output.push({field: period + '_mql' + suffix, aggregate: 'sum'});
                output.push({field: period + '_sql' + suffix, aggregate: 'sum'});
                output.push({field: period + '_sales' + suffix, aggregate: 'sum'});
                output.push({
                    field: period + '_sales_revenue' + suffix + '__amount',
                    aggregate: 'sum'
                });
            })
        });
        return output;
    }
};

ICMO.apps.performance.dataEntry = (function () {
    var initializedTabs = [],
        bindGridtools = function (grid, $el, $gridTools) {
            /*
             $gridTools.find('.grid-expand').bind('click', function (e) {
             var grid = $el.data('kendoTreeList');
             $.each(grid.dataSource.data(), function (idx, data) {
             grid.expand($el.find("tr[data-uid=" + data.uid + "]"));
             })
             });
             $gridTools.find('.grid-collapse').bind('click', function (e) {
             var grid = $el.data('kendoTreeList');
             $.each(grid.dataSource.data(), function (idx, data) {
             grid.collapse($el.find("tr[data-uid=" + data.uid + "]"));
             })
             });
             */
            $gridTools.find('.grid-prev-month').bind('click', function (e) {
                var selector = $gridTools.find('select');
                if ($(e.target).closest('button').hasClass('disabled')) {
                    return;
                }
                selector[0].selectedIndex -= 1;
                selector.change();
            });
            $gridTools.find('.grid-next-month').bind('click', function (e) {
                var selector = $gridTools.find('select');
                if ($(e.target).closest('button').hasClass('disabled')) {
                    return;
                }
                selector[0].selectedIndex += 1;
                selector.change();
            });
            $gridTools.find('.grid-month').on('change', function (e) {
                var selector = $gridTools.find('select'),
                    selected_month = selector.val();
                if (selector[0].selectedIndex === 0) {
                    $gridTools.find('.grid-prev-month').addClass('disabled');
                } else if (selector[0].selectedIndex === selector[0].options.length - 1) {
                    $gridTools.find('.grid-next-month').addClass('disabled');
                } else {
                    $gridTools.find('.grid-prev-month').removeClass('disabled');
                    $gridTools.find('.grid-next-month').removeClass('disabled');
                }
                $.each(grid.columns, function (idx, column) {
                    if (_.contains(['name', ''], column.field) !== true && column.field.indexOf(selected_month) != 0) {
                        grid.hideColumn(column.field);
                    } else {
                        grid.showColumn(column.field);
                    }
                });
            });
            $gridTools.find('.grid-today').bind('click', function (e) {
                var selector = $gridTools.find('select');
                selector.val(ICMO.core.getCurrentMonthName()).change();
            });
        },
        treeListDefaults = {
            dataSource: {
                autoSync: false,
                sort: {field: 'order', dir: 'asc'},
                filter: {
                    logic: "or",
                    filters: [
                        {
                            field: 'item_type',
                            operator: 'eq',
                            value: 'category'
                        }, {
                            field: 'item_type',
                            operator: 'eq',
                            value: 'program'
                        }
                    ]
                }
            },
            editable: false,
            selectable: true,
            resizable: true,
            columns: [
                {field: 'slug', hidden: true},
                {field: 'order', hidden: true},
                {field: 'parent_slug', hidden: true},
                {
                    field: 'name',
                    title: 'Program Selector',
                    template: function (model) {
                        return kendo.template($('#budgetNameTemplate').html())(model)
                    }
                }
            ]
        },
        getCampaignGridDefaults = function () {
            /* renders all the columns for the twelve months, hiding other months than the current */

            var column,
                data_fields = ['mql', 'sql', 'sales', 'sales_revenue__amount'],
                currentMonthName = ICMO.core.getCurrentMonthName(),
                titles = {
                    mql: "MQLs",
                    sql: "SQLs",
                    sales: "Sales",
                    sales_revenue__amount: "Revenue"
                },
                columns = [
                    {field: 'slug', hidden: true},
                    {field: 'name', title: 'Name', width: 150}
                ];

            $.each(ICMO.core.period_types['months'], function (idx, period) {
                $.each(data_fields, function (idx, field) {
                    column = {
                        title: titles[field],
                        field: period + "_" + field,
                        footerTemplate: "<b>#: sum #</b>"
                    };
                    if (period != currentMonthName) {
                        column.hidden = true;
                    }
                    if (field == 'sales_revenue__amount') {
                        column.template = "#: " + period + "_sales_revenue__localized_whole_number#";
                    } else {
                        column.format = "{0:n0}";
                    }
                    columns.push(column);
                });
            });

            columns.push({
                field: '', title: 'Actions',
                template: function (model) {
                    return kendo.template($('#rowTools').html())(model)
                },
                width: 75
            });
            return {columns: columns}
        },
        setActiveProgram = function ($el, programSlug) {
            $el.data('program-slug', programSlug);
            $el.data('api-url', $el.data('root-api-url') + programSlug + '/campaigns/');
            if (!$el.data('kendoGrid')) {
                initializeCampaignGrid($el);
                $el.closest('[data-role="splitter"]').each(function (idx, item) {
                    $(item).data('kendoSplitter').resize();
                });
            }
            var dataSource = $el.data('kendoGrid').dataSource;
            dataSource.transport.options.read.url = $el.data('api-url');
            dataSource.transport.options.create.url = $el.data('api-url');
            dataSource.transport.options.update.url = function (options) {
                return $el.data('api-url') + options.slug + "/";
            };
            dataSource.transport.options.destroy.url = function (options) {
                return $el.data('api-url') + options.slug + "/";
            };
            dataSource.read();
            $('#container-' + $el.attr('id')).show();
            $('#select-a-program-' + $el.attr('id')).hide();
        },
        clearActiveProgram = function ($el) {
            $el.data('program-slug', '');
            $('#container-' + $el.attr('id')).hide();
            $('#select-a-program-' + $el.attr('id')).show();
        },
        getCampaignGridByTree$El = function ($treeEl) {
            return $('#' + $treeEl.attr('id').replace('treelist', 'grid'));
        },
        resizeSplitters = function ($el) {
            var $splitter = $el.closest('.k-splitter');
            $el.closest('.k-splitter').height(Math.max($splitter.find('.left-pane').height(), $splitter.find('.right-pane').height()));
        },
        initializeCampaignGrid = function ($el) {
            ICMO.grid.create($el, ICMO.models.Campaign, getCampaignGridDefaults(), ICMO.apps.performance.generateAggregators(), null);
            var grid = $el.data('kendoGrid');
            var $gridTools = $('#' + $el.attr('data-tools'));
            bindGridtools(grid, $el, $gridTools);
            grid.bind("dataBound", function () {
                resizeSplitters($el);
            });
            return grid;
        };
    return {
        createTreeList: function ($el, userOptions, userAggregators) {
            var aggregators = userAggregators || [],
                settings = $.extend({}, treeListDefaults, userOptions || {});

            settings.dataSource.transport = ICMO.core.getTransport($el);
            settings.dataSource.aggregate = aggregators;
            settings.dataSource.schema = ICMO.core.getSchema(ICMO.models.BudgetLineItem);

            $el.kendoTreeList(settings);

            var grid = $el.data('kendoTreeList');
            var $gridTools = $('.' + $el.attr('data-tools'));

            /* once the grid has loaded run all the bindings */
            ICMO.grid.bindTools(grid, $el, $gridTools);

            grid.bind("dataBound", function () {
                $.each($el.find('tbody tr'), function (idx, row) {
                    var dataItem = $el.data('kendoTreeList').dataItem(row);
                    $(row).attr('data-item-type', dataItem.item_type);
                    $(row).click(function (e) {
                        var dataItem = $el.data('kendoTreeList').dataItem(this);
                        if (dataItem.item_type == 'program') {
                            setActiveProgram(getCampaignGridByTree$El($el), dataItem.program);
                        } else {
                            clearActiveProgram(getCampaignGridByTree$El($el));
                        }
                    });
                });
                $('.k-i-collapse').on('mouseup', function(){
                    resizeSplitters($el);
                });
                $('.k-i-expand').on('mouseup', function(){
                    resizeSplitters($el);
                });
            });
        },
        createCampaignGrid: function ($el) {
            $("#" + $el.attr('id') + "-splitter").kendoSplitter({
                panes: [
                    {size: "20%", collapsible: true},
                    {collapsible: false}
                ]
            });
            clearActiveProgram($el);
        },
        initTabs: function (api_url) {
            $('.nav-tabs .segment-tab-link a').click(function (e) {
                var segmentSlug = $(e.target).attr('href').replace('#tab_', '');
                if (initializedTabs.indexOf(segmentSlug) === -1) {
                    ICMO.apps.performance.dataEntry.createTreeList($('#treelist-' + segmentSlug));
                    ICMO.apps.performance.dataEntry.createCampaignGrid($('#grid-' + segmentSlug));
                    var dataSource = ICMO.core.getDataSourceByURL(api_url + segmentSlug + '/periods/?resolution=program&period=year', ICMO.models.Period);
                    ICMO.apps.performance.summary.createMQLChart($('#radar-segment-' + segmentSlug + '-mql'), dataSource, 'mql_actual', 'program');
                    ICMO.apps.performance.summary.createSQLChart($('#radar-segment-' + segmentSlug + '-sql'), dataSource, 'sql_actual', 'program');
                    ICMO.apps.performance.summary.createSalesChart($('#radar-segment-' + segmentSlug + '-sales'), dataSource, 'sales_actual', 'program');
                    initializedTabs.push(segmentSlug);
                }
            });
        }
    }
}());


ICMO.apps.performance.summary = (function () {
    var defaults = {
        columns: [
            {
                title: 'Segment',
                field: 'segment_name',
                width: 300,
                template: function (model) {
                    model.name = model.segment_name;
                    return kendo.template($('#campaignSummaryNameTemplate').html())(model)
                },
                footerTemplate: "<div width='100%' class='text-right'>MQLs<br>SQLs<br>Sales<br>Revenue</div>",
            },
            {
                title: 'Jan',
                field: 'jan_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'jan');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'jan');
                }
            },
            {
                title: 'Feb',
                field: 'feb_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'feb');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'feb');
                }
            },
            {
                title: 'Mar',
                field: 'mar_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'mar');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'mar');
                }
            },
            {
                title: 'Apr',
                field: 'apr_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'apr');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'apr');
                }
            },
            {
                title: 'May',
                field: 'may_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'may');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'may');
                }
            },
            {
                title: 'Jun',
                field: 'jun_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'jun');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'jun');
                }
            },
            {
                title: 'Jul',
                field: 'jul_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'jul');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'jul');
                }
            },
            {
                title: 'Aug',
                field: 'aug_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'aug');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'aug');
                }
            },
            {
                title: 'Sep',
                field: 'sep_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'sep');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'sep');
                }
            },
            {
                title: 'Oct',
                field: 'oct_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'oct');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'oct');
                }
            },
            {
                title: 'Nov',
                field: 'nov_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'nov');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'nov');
                }
            },
            {
                title: 'Dec',
                field: 'dec_mql',
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'dec');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'dec');
                }
            },
            {
                title: 'Q1 Summary',
                field: 'q1_mql',
                hidden: true,
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'q1');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'q1');
                }
            },
            {
                title: 'Q2 Summary',
                field: 'q2_mql',
                hidden: true,
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'q2');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'q2');
                }
            },
            {
                title: 'Q3 Summary',
                field: 'q3_mql',
                hidden: true,
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'q3');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'q3');
                }
            },
            {
                title: 'Q4 Summary',
                field: 'q4_mql',
                hidden: true,
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'q4');
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'q4');
                }
            },
            {
                title: 'Fiscal Year Summary',
                field: 'fiscal_year_mql',
                hidden: true,
                template: function (model) {
                    return ICMO.apps.performance.renderCellTemplate(model, 'fiscal_year');
                },
                attributes: {
                    style: "border-left: 1px solid rgb(219,219,219) !important;border-right: 1px solid rgb(219,219,219) !important;"
                },
                footerTemplate: function (model) {
                    return ICMO.apps.performance.renderFooterTemplate(model, 'year');
                }
            }
        ]
    };
    return {
        create: function ($el) {
            var aggregators = ICMO.apps.performance.generateAggregators('_actual');
            ICMO.grid.create($el, ICMO.models.HorizontalPeriod, defaults, aggregators, []);
            return $el.data('kendoGrid');
        },
        createMQLChart: function ($el, datasource, userField, userCategory) {
            var field = userField || "year_mql_actual",
                category = userCategory || "segment_name";
            ICMO.charts.periodRadarChart(
                $el,
                "MQL Performance",
                [{
                    field: field,
                    categoryField: category
                }],
                datasource
            );
        },
        createSQLChart: function ($el, datasource, userField, userCategory) {
            var field = userField || "year_sql_actual",
                category = userCategory || "segment_name";
            ICMO.charts.periodRadarChart(
                $el,
                "SQL Performance",
                [{field: field, categoryField: category}],
                datasource
            );
        },
        createSalesChart: function ($el, datasource, userField, userCategory) {
            var field = userField || "year_sales_actual",
                category = userCategory || "segment_name";
            ICMO.charts.periodRadarChart(
                $el,
                "Sales Performance",
                [{field: field, categoryField: category}],
                datasource
            );
        }
    }
}());


ICMO.models.Campaign = (function () {
    var schema = {
            fields: {
                company: {
                    type: "string",
                    editable: false
                },
                created: {
                    type: "date",
                    editable: false
                },
                modified: {
                    type: "date",
                    editable: false
                },
                modified_by: {
                    type: "string",
                    editable: false
                },
                modified_by_name: {
                    type: "string",
                    editable: false
                },
                name: {
                    required: true,
                    type: "string",
                    validation: {
                        required: true
                    }
                },
                program: {
                    type: "string",
                    editable: false
                },
                revenue_plan: {
                    type: "string",
                    editable: false
                },
                segment: {
                    type: "string",
                    editable: false
                },
                slug: {
                    type: "string",
                    editable: false
                },
                source: {
                    type: "string"
                }
            },
            idField: "slug",
            id: "slug"
        },
        fieldTemplates = {
            average_sale: {
                type: "string",
                editable: false
            },
            cost_per_mql: {
                type: "string",
                editable: false
            },
            cost_per_sql: {
                type: "string",
                editable: false
            },
            mql: {type: "number"},
            mql_to_sql_conversion: {
                type: "number",
                editable: false
            },
            sales: {
                type: "number"
            },
            sql: {
                type: "number"
            },
            sales_revenue: {type: 'string'},
            sales_revenue__amount: {type: 'number', defaultValue: 0},
            sales_revenue__localized_whole_number: {type: 'string'},
            sales_revenue__localized: {type: 'string'}
        };

    $.each(ICMO.core.period_types['months'], function (idx, period) {
        $.each(fieldTemplates, function (fieldName, fieldOptions) {
            schema.fields[period + "_" + fieldName] = fieldOptions;
        });
    });
    return kendo.data.Model.define(schema);
})();
