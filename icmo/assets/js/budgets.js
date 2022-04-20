var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.budgets = {};

ICMO.apps.budgets = (function () {
    return {
        getBudgetValuesByTimePeriod: function (model, time_period, sum) {
            var item_types = ['plan', 'actual', 'variance'],
                currency_fields = ['amount', 'currency', 'localized', 'localized_whole_number'],
                output = {},
                sum = sum || false,
                suffix;

            if (model['jan_budget_actual__amount'] !== undefined) {
                suffix = "_budget";
            } else {
                suffix = "";
            }
            for (var x = 0; x < item_types.length; x++) {
                for (var y = 0; y < currency_fields.length; y++) {
                    var field = item_types[x] + "__" + currency_fields[y];
                    var obj = model[time_period + suffix + "_" + field];
                    if (sum && obj && obj.sum !== undefined) {
                        output[field] = "$" + kendo.toString(obj.sum, 'n0');
                    } else {
                        output[field] = obj;
                    }
                }
            }
            return output;
        },
        renderBudgetValueTemplate: function (model, time_period) {
            var template = kendo.template($('#budgetValueTemplate').html());
            var values = ICMO.apps.budgets.getBudgetValuesByTimePeriod(model, time_period);
            values['item_type'] = model.item_type;
            return template(values);
        },
        renderBudgetFooterTemplate: function (model, time_period) {
            var template = kendo.template($('#budgetSummaryFooterTemplate').html());
            var values = ICMO.apps.budgets.getBudgetValuesByTimePeriod(model, time_period, true);
            values['item_type'] = 'program';
            return template(values);
        }
    }
}());

ICMO.apps.budgets.budgetTrees = (function () {
    var initializedTabs = [],
        renderBudgetEditor = function (container, options) {
            var plan_field = options.field.replace('actual', 'plan');
            var variance_field = options.field.replace('actual', 'variance');
            // create an input element
            var template = kendo.template($('#budgetEditorTemplate').html());
            var input = $(template({
                plan_field: plan_field,
                variance_field: variance_field,
                actual_field: options.field,
                plan_value: options.model[plan_field],
                variance_value: options.model[variance_field],
                actual_value: options.model[options.field],
                item_type: options.model.item_type,
                automatic_distribution: options.model.automatic_distribution
            }));
            // set its name to the field to which the column is bound ('name' in this case)
            // append it to the container
            input.appendTo(container);
        },
        renderBudgetNameEditor = function (container, options) {
            // create an input element
            var input = $('<input/>');
            input.attr('name', options.field);
            if (options.model.item_type === 'program') {
                input.attr('disabled', 'disabled');
                input.attr('title', 'Rename the program to rename this budget item.');
            }
            input.appendTo(container);
        },

        bindBudgetGridTools = function (grid, $el, $gridTools) {
            $gridTools.find('.grid-toggle-detail').bind('click', function () {
                $el.find('.budget_plan').toggle();
                $el.find('.budget_cell .subrow').toggle();
                $el.find('.budget_variance').toggle();
                $el.find('.budget_value_cell_spacer').toggle();
            });
            $gridTools.find('.grid-change-view').bind('change', function (e) {
                grid.cancelRow();
                grid.trigger('cancel');
                var view = $(e.target).val();
                if (view === 'month') {
                    toggleColumns(grid, quarter_columns, month_columns);
                } else if (view === 'quarter') {
                    toggleColumns(grid, month_columns, quarter_columns);
                }
            });
            $gridTools.find('.grid-add-category').bind('click', function () {
                grid.one('edit', function (e) {
                    e.model.item_type = 'category';
                });
                grid.addRow();
            });
            $gridTools.find('.grid-add-custom').bind('click', function () {
                grid.one('edit', function (e) {
                    e.model.item_type = 'custom';
                });
                grid.addRow();
            });
        },
        toggleColumns = function (grid, hide_column_names, show_column_names) {
            $.each(hide_column_names, function (idx, name) {
                grid.hideColumn(name);
            });
            $.each(show_column_names, function (idx, name) {
                grid.showColumn(name);
            });
        },
        month_columns = [
            'jan_actual__amount', 'feb_actual__amount', 'mar_actual__amount',
            'apr_actual__amount', 'may_actual__amount', 'jun_actual__amount',
            'jul_actual__amount', 'aug_actual__amount', 'sep_actual__amount',
            'oct_actual__amount', 'nov_actual__amount', 'dec_actual__amount',
            'fiscal_year_actual__amount'
        ],
        quarter_columns = [
            'q1_actual__amount', 'q2_actual__amount', 'q3_actual__amount', 'q4_actual__amount', 'fiscal_year_actual__amount'
        ],
        generateColumnNames = function () {
            var columns = [
                {
                    field: 'name',
                    title: 'Name',
                    template: function (model) {
                        return kendo.template($('#budgetNameTemplate').html())(model)
                    },
                    editor: renderBudgetNameEditor,
                    /*footerTemplate: "<div width='100%' class='text-right'>Plan<br>Actual<br>Variance</div>",*/
                    width: 300
                }
            ];
            $.each(ICMO.core.fiscal_months, function (idx, month) {
                columns.push({
                    field: month + '_actual__amount',
                    title: ICMO.core.toTitle(month),
                    editor: renderBudgetEditor,
                    template: function (model) {
                        return ICMO.apps.budgets.renderBudgetValueTemplate(model, month);
                    }
                });
            });
            $.each(ICMO.core.period_types['quarters'], function (idx, period) {
                columns.push({
                    field: period + '_actual__amount',
                    title: ICMO.core.toTitle(period) + ' Summary',
                    hidden: true,
                    template: function (model) {
                        return ICMO.apps.budgets.renderBudgetValueTemplate(model, period);
                    }
                });
            });
            columns.push({
                field: 'fiscal_year_actual__amount',
                title: 'Fiscal Year Summary',
                template: function (model) {
                    return ICMO.apps.budgets.renderBudgetValueTemplate(model, 'fiscal_year');
                },
                attributes: {
                    style: "border-left: 1px solid rgb(219,219,219) !important;border-right: 1px solid rgb(219,219,219) !important;"
                }
            });
            columns.push({
                field: '', title: 'Actions',
                template: function (model) {
                    return kendo.template($('#rowTools').html())(model)
                }
            });
            return columns;
        },
        generateAggregates = function () {
            var output = [];
            $.each(ICMO.core.period_types['months'], function (idx, month) {
                $.each(ICMO.core.value_types, function (idx, value_type) {
                    output.push({
                        field: month + '_' + value_type + '__amount', aggregate: 'sum'
                    });
                });
            });
            return output;
        },
        gridSettings = {
            columns: generateColumnNames()
        },
        aggregates = generateAggregates(),
        sumPlan = function (item) {
            var total = 0;
            for (var i = 0; i < ICMO.core.fiscal_months.length; i++) {
                total += item[ICMO.core.fiscal_months[i] + "_plan__amount"];
            }
            return total;
        },
        bindGridDefaults = function ($el, grid) {
            $el.on('blur', 'tr.k-grid-edit-row input', function (e) {
            })
        },
        bindProgramPlanBudgetSave = function ($el, grid) {
            grid.dataSource.bind("change", function (e) {
                if (e.action === "itemchange" && e.field.indexOf('plan') == 4) {
                    var item = e.items[0];
                    if (item.item_type == 'program') {
                        var total = sumPlan(item),
                            $fiscalYearPlan = $el.find("tr[data-uid=" + item.uid + "]").find('td:nth-last-of-type(2)').find('.budget_plan');
                        grid.icmo_dirty_uid = item.uid;
                        if (total != item.fiscal_year_plan__amount) {
                            $fiscalYearPlan.addClass('text-red');
                        } else {
                            $fiscalYearPlan.removeClass('text-red');
                        }
                    }
                }
            });
            $el.bind('preSave', function (e, item) {
                if (item.item_type == 'program' && !item.automatic_distribution) {
                    var total = sumPlan(item);
                    if (total != item.fiscal_year_plan__amount) {
                        bootbox.alert("The sum of all budget months must equal the " +
                            "planned fiscal year total. You are off by " +
                            (total - item.fiscal_year_plan__amount));
                        e.preventDefault();
                    }
                }
            })
        },
        dndTest = function (grid, moved_item, destination_item) {
            if (!moved_item.is_moveable) {
                return {
                    allowed: false,
                    msg: "This item is managed in the program mix and cannot be moved"
                }
            }
            if (moved_item.item_type != 'custom' && destination_item && destination_item.item_type == 'category' && destination_item.program) {
                return {allowed: false, msg: "Only custom budget items may be added to a Channel."}
            }
            return {allowed: true, msg: null}
        },
        moveOutTest = function (item) {
            return item.is_moveable;
        },
        deleteTest = function (item) {
            return item.item_type != 'program' && !item.program;
        },
        enableAutomaticDistribution = function ($el) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoTreeList'),
                dataItem = grid.dataItem($targetRow);
            dataItem.set('automatic_distribution', true);
            grid.dataSource.sync();
        },
        disableAutomaticDistribution = function ($el) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoTreeList'),
                dataItem = grid.dataItem($targetRow);
            dataItem.set('automatic_distribution', false);
            grid.dataSource.sync();
        };

    return {
        create: function ($el) {
            var contextMenuOptions = [
                {
                    label: 'Enable Automatic Distribution',
                    action: 'enable-automatic-distribution',
                    callback: enableAutomaticDistribution,
                    visible: function ($el) {
                        var item = ICMO.grid.contextMenu.get$TargetRowDataItem($el);
                        return item.item_type == 'program' && !item.automatic_distribution;

                    }
                },
                {
                    label: 'Disable Automatic Distribution',
                    action: 'disable-automatic-distribution',
                    callback: disableAutomaticDistribution,
                    visible: function ($el) {
                        var item = ICMO.grid.contextMenu.get$TargetRowDataItem($el);
                        return item.item_type == 'program' && item.automatic_distribution;

                    }
                },
                'edit'
            ];
            var grid = ICMO.tree.create($el, ICMO.models.BudgetLineItem, gridSettings, {
                    aggregates: aggregates,
                    dndTestFunc: dndTest,
                    moveOutTestFunc: moveOutTest,
                    deleteTestFunc: deleteTest,
                    contextMenuOptions: contextMenuOptions
                }),
                $gridTools = $('#' + $el.data('tools'));
            bindBudgetGridTools(grid, $el, $gridTools);
            bindProgramPlanBudgetSave($el, grid);
            bindGridDefaults($el, grid);
            return grid;
        },
        createPieChartDataSource: function ($el) {
            var data = $el.data('kendoTreeList').dataSource.data();
            var output = [];
            for (var i = 0; i < data.length; i++) {
                if (data[i].item_type === 'category') {
                    output.push({
                        fiscal_year_plan__amount: data[i].fiscal_year_plan__amount,
                        fiscal_year_actual__amount: data[i].fiscal_year_actual__amount,
                        name: data[i].name
                    });
                }
            }
            return new kendo.data.DataSource({
                data: output
            });
        },
        initTabs: function () {
            $('.nav-tabs .segment-tab-link a').click(function (e) {
                var segmentSlug = $(e.target).attr('href').replace('#tab_', '');
                if (initializedTabs.indexOf(segmentSlug) === -1) {
                    var segmentTreeList = ICMO.apps.budgets.budgetTrees.create($('#treelist-segment-'+segmentSlug));
                    segmentTreeList.bind("dataBound", function () {
                        var pieDataSource = ICMO.apps.budgets.budgetTrees.createPieChartDataSource($('#treelist-segment-'+segmentSlug));
                        ICMO.apps.budgets.summaryGrid.createActualPieChart($('#pie-segment-'+segmentSlug+'-actual'), pieDataSource, "fiscal_year_actual__amount", "name");
                        ICMO.apps.budgets.summaryGrid.createPlanPieChart($('#pie-segment-'+segmentSlug+'-plan'), pieDataSource, "fiscal_year_plan__amount", "name");
                    });
                    initializedTabs.push(segmentSlug);
                }
            });
        }
    }
}());


ICMO.apps.budgets.summaryGrid = (function () {
    var defaults = (function () {
            var defaults = {
                columns: [
                    {
                        field: 'segment_name',
                        title: 'Segment',
                        width: 300,
                        template: function (model) {
                            model.item_type = 'summary';
                            model.name = model.segment_name;
                            return kendo.template($('#budgetNameTemplate').html())(model)
                        },
                        footerTemplate: "<div style='width:100%' class='text-right'>Plan<br>Actual<br>Variance</div>"
                    }
                ],
                editable: false
            };
            $.each(ICMO.core.fiscal_months, function (idx, month) {
                defaults.columns.push({
                    field: month + '_budget_actual__amount',
                    title: ICMO.core.toTitle(month),
                    template: function (model) {
                        return ICMO.apps.budgets.renderBudgetValueTemplate(model, month);
                    },
                    footerTemplate: function (model) {
                        return ICMO.apps.budgets.renderBudgetFooterTemplate(model, month);
                    }
                });
            });
            return defaults;
        }()),
        aggregates = (function () {
            var output = [];
            $.each(ICMO.core.period_types['months'], function (idx, month) {
                $.each(ICMO.core.value_types, function (idx, value_type) {
                    output.push({
                        field: month + '_budget_' + value_type + '__amount', aggregate: 'sum'
                    });
                });
            });
            return output;
        }());
    return {
        create: function ($el) {
            ICMO.grid.create($el, ICMO.models.HorizontalPeriod, defaults, aggregates, []);
            var grid = $el.data('kendoGrid');
            grid.bind('dataBound', function () {
            });
            return grid;
        },
        createPlanPieChart: function ($el, datasource, userField, userCategory) {
            var field = userField || "year_budget_plan__amount",
                category = userCategory || "segment_name";
            ICMO.apps.dashboards.periodChart.create(
                $el,
                "Planned Fiscal Year Budget",
                [{

                    field: field,
                    categoryField: category
                }],
                'months',
                'pie',
                datasource
            );
        },
        createActualPieChart: function ($el, datasource, userField, userCategory) {
            var field = userField || "year_budget_actual__amount",
                category = userCategory || "segment_name";
            ICMO.apps.dashboards.periodChart.create(
                $el,
                "Actual Fiscal Year Budget",
                [{

                    field: field,
                    categoryField: category
                }],
                'months',
                'pie',
                datasource
            );
        }
    }
}());


ICMO.models.BudgetLineItem = (function () {
    var schema = {
            fields: {
                created: {type: "date", editable: false},
                modified: {type: "date", editable: false},
                modified_by: {type: "string", editable: false},

                program: {type: "string"},
                weight: {type: "number", defaultValue: 0},
                reorder_target: {type: "string", defaultValue: ""},
                segment: {type: "string"},
                revenue_plan: {type: "string"},

                name: {type: "string"},
                item_type: {type: "string", editable: false},
                slug: {type: "string", editable: false},
                order: {field: 'order', type: "number", editable: false},
                parentId: {
                    field: 'parent', type: "string", defaultValue: '',
                    parse: function (val) {
                        if (!val) {
                            return '';
                        }
                        return val;
                    }
                },
                is_moveable: {type: 'boolean', editable: false},
                automatic_distribution: {type: 'boolean',}
            },
            idField: "slug",
            id: "slug"
        },
        fieldTemplates = {
            actual: {type: "string", editable: true},
            actual__amount: {type: "number", defaultValue: 0, editable: true},

            plan: {type: "string", editable: true},
            plan__amount: {type: "number", defaultValue: 0, editable: true},

            variance: {type: "string", editable: false},
            variance__amount: {type: "number", defaultValue: 0, editable: false}

        };
    $.each(ICMO.core.period_types, function (period_type, periods) {
        $.each(periods, function (idx, period) {
            $.each(fieldTemplates, function (fieldName, fieldOptions) {
                schema.fields[period + "_" + fieldName] = $.extend({}, fieldOptions);
                if (period_type === 'years' || period_type === 'quarters') {
                    schema.fields[period + "_" + fieldName].editable = false;
                }
            });
        });
    });
    return kendo.data.TreeListModel.define(schema);
})();
