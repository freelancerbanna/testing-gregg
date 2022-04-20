var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.leads = {};


ICMO.apps.leads.programGrid = (function () {
        var initializedTabs = [],
            programEditor = function (container, options) {
                if (options.model.item_type === 'category' || !options.model.item_type) {
                    return;
                }
                var input = $("<input/>");
                input.attr("name", options.field);
                input.appendTo(container);
            },
            generateLabel = function ($el, field, operation, userOptions) {
                var defaults = {
                    prefix: '',
                    suffix: ''
                };
                var options = $.extend({}, defaults, userOptions || {});
                return function () {
                    var value = 0,
                        counter = 0,
                        grid = $el.data('kendoTreeList'),
                        label = '<span title="#title#" data-placement="left" data-toggle="tooltip">#prefix##val##suffix#</span>';
                    $.each(grid.dataSource.data(), function (idx, data) {
                        if (data.item_type == 'program') {
                            counter += 1;
                            if (operation.toLowerCase() == 'average') {
                                value += Number(data[field]) * Number(data['marketing_mix']) / 100;
                            } else {
                                value += Number(data[field]);
                            }
                        }
                    });
                    return label
                        .replace('#val#', kendo.toString(value, 'n0'))
                        .replace('#title#', operation.toLowerCase() == 'sum' ? 'Sum' : 'Weighted Average')
                        .replace('#prefix#', options.prefix)
                        .replace('#suffix#', options.suffix);
                }
            },
            generateDefaults = function ($el) {
                return {
                    columns: [
                        {field: 'slug', hidden: true},
                        {field: 'marketing_mix_locked', hidden: true},
                        {
                            field: 'name', title: 'Name', width: 130,
                            template: function (model) {
                                return kendo.template($('#programNameTemplate').html())(model)
                            }
                        },
                        {
                            field: 'marketing_mix',
                            title: 'Marketing Mix',
                            template: '# if(item_type!="category") {# <i class="cursor-pointer marketing_mix fa fa-# if(marketing_mix_locked===false){ #un# } #lock"></i> #: marketing_mix #% # }else{ # #: marketing_mix #% # } #',
                            footerTemplate: (function ($el) {
                                return function () {
                                    var value = 0,
                                        grid = $el.data('kendoTreeList'),
                                        label = '<span title="Sum" data-placement="left"  data-toggle="tooltip"';
                                    $.each(grid.dataSource.data(), function (idx, data) {
                                        if (data.item_type == 'program') {
                                            value += data.marketing_mix;
                                        }
                                    });
                                    if (value > 100) {
                                        label += " class='text-red'";
                                    }
                                    return label + ">" + kendo.toString(value, 'n0') + '%</span>';
                                }
                            }($el)),
                            attributes: {
                                style: "border-left: 1px solid rgb(219,219,219) !important;"
                            },
                            editor: function (container, options) {
                                if (options.model.item_type === 'category' || !options.model.item_type) {
                                    return;
                                }
                                var grid = container.closest('.k-grid').data('kendoTreeList'),
                                    data = grid.dataSource.getByUid(options.model.uid),
                                    input = $("<input/>"),
                                    icon = $("<i class='cursor-pointer lock_marketing_mix fa'></i> "),
                                    marketingMix = $('input[data-bind="value:marketing_mix"]');
                                if (data.marketing_mix_locked) {
                                    icon.addClass('fa-lock');
                                    input.prop('disabled', false);
                                    marketingMix.prop('disabled', true);
                                } else {
                                    icon.addClass('fa-unlock');
                                    input.prop('disabled', true);
                                    marketingMix.prop('disabled', false);
                                }
                                input.attr("name", options.field);
                                icon.appendTo(container);
                                input.appendTo(container);
                                icon.click(function (e) {
                                    if (data.marketing_mix_locked) {
                                        $(e.target).removeClass('fa-lock').addClass('fa-unlock');
                                        data.set('marketing_mix_locked', false);
                                        input.prop('disabled', true);
                                        marketingMix.prop('disabled', false);
                                    } else {
                                        $(e.target).removeClass('fa-unlock').addClass('fa-lock');
                                        data.set('marketing_mix_locked', true);
                                        input.prop('disabled', false);
                                        marketingMix.prop('disabled', true);
                                    }
                                });
                            }
                        },
                        {
                            field: 'touches_per_contact',
                            title: 'Touches Per Contact',
                            format: '{0: # }',
                            footerTemplate: generateLabel($el, 'touches_per_contact', 'Average'),
                            editor: programEditor
                        },
                        {
                            field: 'touches_to_mql_conversion',
                            title: 'Touches to MQL Conversion',
                            format: "{0: #.#'%' }",
                            footerTemplate: generateLabel($el, 'touches_to_mql_conversion', 'Average', {suffix: '%'}),
                            editor: programEditor
                        },
                        {
                            field: 'mql_to_sql_conversion',
                            title: 'MQL to SQL Conversion',
                            format: "{0: #.#'%' }",
                            footerTemplate: generateLabel($el, 'mql_to_sql_conversion', 'Average', {suffix: '%'}),
                            editor: programEditor
                        },
                        {
                            field: 'sql_to_sale_conversion',
                            title: 'SQL to Sale Conversion',
                            format: "{0: #.#'%' }",
                            footerTemplate: generateLabel($el, 'sql_to_sale_conversion', 'Average', {suffix: '%'}),
                            editor: programEditor
                        },
                        {
                            field: 'cost_per_mql__amount',
                            title: 'Cost Per MQL',
                            template: "<span # if(cost_per_mql__amount > max_cost_per_mql){ # class='text-red' title='The maximum cost per lead to break even is $ #: max_cost_per_mql #' # } #> #: cost_per_mql__localized # </span>",
                            footerTemplate: generateLabel($el, 'cost_per_mql__amount', 'Average', {prefix: '$'}),
                            attributes: {
                                style: "border-right: 1px solid rgb(219,219,219) !important;"
                            },
                            editor: programEditor
                        },
                        {
                            field: 'contacts',
                            title: 'Contacts',
                            footerTemplate: generateLabel($el, 'contacts', 'Sum')
                        },

                        {
                            field: 'touches',
                            title: 'Touches',
                            footerTemplate: generateLabel($el, 'touches', 'Sum')
                        },
                        {
                            field: 'mql',
                            title: 'MQLs',
                            footerTemplate: generateLabel($el, 'mql', 'Sum')
                        },
                        {
                            field: 'sql',
                            title: 'SQLs',
                            footerTemplate: generateLabel($el, 'sql', 'Sum')
                        },
                        {
                            field: 'sales',
                            title: 'Sales',
                            footerTemplate: generateLabel($el, 'sales', 'Sum'),
                            attributes: {
                                style: "border-right: 1px solid rgb(219,219,219) !important;"
                            }
                        },
                        {
                            field: 'budget__amount',
                            title: 'Program Budget',
                            template: '# if(item_type=="category"){ #<span class="underline" title="This number is an estimate and does not include any custom budget line items you may have added under the budget.  See this channel in the budget app for those items.">#: budget__localized_whole_number # # }else{ # #: budget__localized_whole_number # # } #',
                            footerTemplate: generateLabel($el, 'budget__amount', 'Sum', {prefix: "$"}),
                            editor: function (container, options) {
                                if (options.model.item_type === 'category' || !options.model.item_type) {
                                    return;
                                }
                                var grid = container.closest('.k-grid').data('kendoTreeList'),
                                    data = grid.dataSource.getByUid(options.model.uid),
                                    input = $("<input/>"),
                                    icon = $("<i class='cursor-pointer lock_program_budget fa'></i> "),
                                    costPerMQL = $('input[data-bind="value:cost_per_mql__amount"]');
                                if (data.fixed_budget) {
                                    icon.addClass('fa-lock');
                                    input.prop('disabled', false);
                                    costPerMQL.prop('disabled', true);
                                } else {
                                    icon.addClass('fa-unlock');
                                    input.prop('disabled', true);
                                    costPerMQL.prop('disabled', false);
                                }
                                input.attr("name", options.field);
                                icon.appendTo(container);
                                input.appendTo(container);
                                icon.click(function (e) {
                                    if (data.fixed_budget) {
                                        $(e.target).removeClass('fa-lock').addClass('fa-unlock');
                                        data.set('fixed_budget', false);
                                        input.prop('disabled', true);
                                        costPerMQL.prop('disabled', false);
                                    } else {
                                        $(e.target).removeClass('fa-unlock').addClass('fa-lock');
                                        data.set('fixed_budget', true);
                                        input.prop('disabled', false);
                                        costPerMQL.prop('disabled', true);
                                    }
                                });
                            }
                        },
                        {
                            field: 'sales_revenue__amount',
                            title: 'Sales Goal',
                            template: "#: sales_revenue__localized_whole_number #",
                            footerTemplate: generateLabel($el, 'sales_revenue__amount', 'Sum', {prefix: "$"})
                        },
                        {
                            field: 'roi',
                            title: 'ROI',
                            format: "{0: #'%' }",
                            template: "<span class='# if (roi<0){ # text-red # } #'>#: roi #%</span>",
                            footerTemplate: generateLabel($el, 'roi', 'Average', {suffix: "%"}),
                            attributes: {
                                style: "border-right: 1px solid rgb(219,219,219) !important;"
                            }
                        },
                        {
                            field: '', title: 'Actions', template: function () {
                            return $('#rowTools').html()
                        }
                        }
                    ]
                }
            },
            aggregates = [
                {field: 'sales_revenue__amount', aggregate: 'sum'},
                {field: 'contacts', aggregate: 'sum'},
                {field: 'touches', aggregate: 'sum'},
                {field: 'mql', aggregate: 'sum'},
                {field: 'sql', aggregate: 'sum'},
                {field: 'sales', aggregate: 'sum'},
                {field: 'touches_per_contact', aggregate: 'average'},
                {field: 'touches_to_mql_conversion', aggregate: 'average'},
                {field: 'mql_to_sql_conversion', aggregate: 'average'},
                {field: 'sql_to_sale_conversion', aggregate: 'average'},
                {field: 'cost_per_mql__amount', aggregate: 'average'},
                {field: 'marketing_mix', aggregate: 'sum'},
                {field: 'budget__amount', aggregate: 'sum'},
                {field: 'roi', aggregate: 'average'}
            ],
            lm_uid_edited,
            redistributeMarketingMix = function (dataSource) {
                /*
                 Redistributes (changing) the marketing mix of each unlocked cell so that the sum
                 is 100%, EXCEPT the one currently being saved (lm_uid_edited), as that would confuse
                 the user.
                 */
                var mix_total = 100,
                    mix_distribution,
                    last_item_addition,
                    num_unlocked = 0,
                    last_data_item,
                    data = dataSource.data();
                for (var i = 0; i < data.length; i++) {
                    if (data[i].item_type == 'category') {
                        continue;
                    }
                    if (data[i].marketing_mix_locked === true) {
                        mix_total -= data[i].marketing_mix;
                    } else {
                        num_unlocked += 1;
                    }
                }
                mix_distribution = Math.floor(mix_total / num_unlocked);
                last_item_addition = mix_total - (mix_distribution * num_unlocked);
                for (i = 0; i < data.length; i++) {
                    if (data[i].item_type == 'category') {
                        continue;
                    }
                    if (data[i].marketing_mix_locked === false) {
                        data[i].set('marketing_mix', mix_distribution);
                        last_data_item = data[i]
                    }
                }
                if (last_data_item) {
                    last_data_item.set('marketing_mix', last_data_item.marketing_mix + last_item_addition);
                }
                dataSource.sync();
                lm_uid_edited = null;
            },
            bindProgramGridTools = function (grid, $el, $gridTools) {
                $gridTools.find('.grid-add-category').bind('click', function () {
                    grid.one('edit', function (e) {
                        e.model.item_type = 'category';
                    });
                    grid.addRow();
                });
                $gridTools.find('.grid-add-program').bind('click', function () {
                    grid.one('edit', function (e) {
                        e.model.item_type = 'program';
                    });
                    grid.addRow();
                });
            },
            bindMarketingMixToggles = function ($el, grid) {
                $el.on('click', 'i.marketing_mix', function (e) {
                    var data = grid.dataSource.getByUid($(e.target).closest('tr').attr('data-uid'));
                    var locked = data.marketing_mix_locked;
                    data.set('marketing_mix_locked', !locked);
                    grid.dataSource.sync();
                    redistributeMarketingMix(grid.dataSource);
                });
                /* grid save and remove     event fires *before* the item has been removed, so we do this */
                grid.bind('save', function (e) {
                    lm_uid_edited = e.container.attr('data-uid');
                    grid.dataSource.one('sync', function () {
                        redistributeMarketingMix(grid.dataSource);
                    });
                });
                grid.bind('remove', function () {
                    grid.dataSource.one('sync', function () {
                        redistributeMarketingMix(grid.dataSource);
                    });
                });
            },
            bindFunnelUpdates = function ($el, grid) {
                grid.bind('dataBound', function () {
                    updateFunnel($el, grid);
                });
                grid.bind('change', function () {
                    updateFunnel($el, grid);
                });
            },
            updateFunnel = function ($el, grid) {
                var $funnelEl = $("#" + $el.attr('id').replace('grid', 'funnels')),
                    funnelFields = [
                        'contacts', 'touches_to_mql_conversion', 'mql_to_sql_conversion',
                        'sql_to_sale_conversion', 'mql', 'sql', 'sales'
                    ];
                $.each(grid.columns, function (idx, column) {
                    if (funnelFields.indexOf(column.field)> -1) {
                        $funnelEl.find('span.funnel-' + column.field).html($(column.footerTemplate()).html(), 'n0');
                    }
                });
            };
        return {
            create: function ($el) {
                var grid = ICMO.tree.create($el, ICMO.models.Program, generateDefaults($el), {
                        aggregates: aggregates
                    }),
                    $gridTools = $('#' + $el.data('tools'));
                bindProgramGridTools(grid, $el, $gridTools);
                bindMarketingMixToggles($el, grid);
                bindFunnelUpdates($el, grid);
                return grid;
            },
            initTabs: function () {
                $('.nav-tabs .segment-tab-link a').click(function (e) {
                    var segmentSlug = $(e.target).attr('href').replace('#tab_', '');
                    if (initializedTabs.indexOf(segmentSlug) === -1) {
                        ICMO.apps.leads.programGrid.create($('#grid-segment-' + segmentSlug));
                        initializedTabs.push(segmentSlug);
                    }
                });
            }
        }
    }()
);

ICMO.apps.leads.funnels = {
    /* handles updating the Marketing Mix funnels from the grid aggregates data */
    bindFunnelUpdates: function ($el, grid) {
        grid.bind('dataBound', function () {
            ICMO.apps.leads.funnels.update($el, grid.dataSource);
        });
        grid.bind('change', function () {
            ICMO.apps.leads.funnels.update($el, grid.dataSource);
        });
    },
    update: function ($el, dataSource) {
        var suffix = "",
            $funnelEl = $("#" + $el.attr('id').replace('grid', 'funnels')),
            aggregates = dataSource.aggregates();
        if (aggregates['contacts_plan'] != undefined) {
            suffix = "_plan";
        }
        $funnelEl.find('span.funnel-contacts').html(kendo.toString(aggregates['contacts' + suffix].average, 'n0'));
        $funnelEl.find('span.funnel-touches_to_mql_conversion').html(kendo.toString(aggregates['touches_to_mql_conversion' + suffix].average, 'n1') + "%");
        $funnelEl.find('span.funnel-mql_to_sql_conversion').html(kendo.toString(aggregates['mql_to_sql_conversion' + suffix].average, 'n1') + "%");
        $funnelEl.find('span.funnel-sql_to_sale_conversion').html(kendo.toString(aggregates['sql_to_sale_conversion' + suffix].average, 'n1') + "%");
        $funnelEl.find('span.funnel-mql').html(kendo.toString(aggregates['mql' + suffix].sum, 'n0'));
        $funnelEl.find('span.funnel-sql').html(kendo.toString(aggregates['sql' + suffix].sum, 'n0'));
        $funnelEl.find('span.funnel-sales').html(kendo.toString(aggregates['sales' + suffix].sum, 'n0'));
    }
};

ICMO.apps.leads.summaryGrid = (function () {
    var defaults = {
            columns: [
                {
                    field: 'segment_name',
                    title: "Segment",
                    template: "<b>#: segment_name #</b>",
                    width: 130,
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'touches_per_contact_plan',
                    title: 'Touches Per Contact',
                    format: '{0: # }',
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #</span>',
                },
                {
                    field: 'touches_to_mql_conversion_plan',
                    title: 'Touches to MQL Conversion',
                    format: "{0: #.#'%' }",
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
                },
                {
                    field: 'mql_to_sql_conversion_plan',
                    title: 'MQL to SQL Conversion',
                    format: "{0: #.#'%' }",
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>'
                },
                {
                    field: 'sql_to_sale_conversion_plan',
                    title: 'SQL to Sale Conversion',
                    format: "{0: #.#'%' }",
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
                },
                {
                    field: 'cost_per_mql_plan__amount',
                    title: 'Cost Per MQL',
                    template: "#: cost_per_mql_plan__localized #",
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">$#= kendo.toString(average, "n0") #</span>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'contacts_plan',
                    title: 'Contacts',
                    format: '{0: #,##}',
                    footerTemplate: '<span title="Sum" data-placement="left" data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>'
                },

                {
                    field: 'touches_plan',
                    title: 'Touches',
                    format: '{0: #,##}',
                    footerTemplate: '<span title="Sum" data-placement="left" data-toggle="tooltip">#= kendo.toString(sum, "n0")#</span>'
                },
                {
                    field: 'mql_plan',
                    title: 'MQLs',
                    format: '{0: #,##}',
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0")#</span>'
                },
                {
                    field: 'sql_plan',
                    title: 'SQLs',
                    format: '{0: #,##}',
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'sales_plan',
                    title: 'Sales',
                    format: '{0: #,##}',
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">#= kendo.toString(sum, "n0") #</span>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'budget_plan__amount',
                    title: 'Program Budget',
                    template: "#: budget_plan__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip">$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'roi_plan',
                    title: 'ROI',
                    template: "<span class='# if (roi_plan<0){ # text-red # } #'># if(roi_plan){ # #: roi_plan # # } else { # 0 # } #%</span>",
                    footerTemplate: '<span title="Average" data-placement="left" data-toggle="tooltip">#= kendo.toString(average, "n0") #%</span>',
                }
            ],
            editable: false
        },
        aggregates = [
            {field: 'contacts_plan', aggregate: 'sum'},
            {field: 'touches_plan', aggregate: 'sum'},
            {field: 'mql_plan', aggregate: 'sum'},
            {field: 'sql_plan', aggregate: 'sum'},
            {field: 'sales_plan', aggregate: 'sum'},
            {field: 'touches_per_contact_plan', aggregate: 'average'},
            {field: 'touches_to_mql_conversion_plan', aggregate: 'average'},
            {field: 'mql_to_sql_conversion_plan', aggregate: 'average'},
            {field: 'sql_to_sale_conversion_plan', aggregate: 'average'},
            {field: 'cost_per_mql_plan__amount', aggregate: 'average'},
            {field: 'budget_plan__amount', aggregate: 'sum'},
            {field: 'roi_plan', aggregate: 'average'}
        ];
    return {
        create: function ($el) {
            ICMO.grid.create($el, ICMO.models.Period, defaults, aggregates, []);
            var grid = $el.data('kendoGrid');
            ICMO.apps.leads.funnels.bindFunnelUpdates($el, grid);
            return grid;
        }
    }
}());

ICMO.models.Program = kendo.data.TreeListModel.define({
    fields: {
        slug: {
            type: "string",
            editable: false,
            defaultValue: ""
        },
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
        reorder_target: {type: "string", defaultValue: ""},
        item_type: {type: "string", editable: false},
        roi: {
            editable: false,
            type: "number"
        },
        mql_to_sql_conversion: {
            type: "number",
            validation: {
                required: true,
                min: 0
            },
            defaultValue: 10
        },
        name: {
            type: "string",
            validation: {
                required: true
            }
        },
        sql_to_sale_conversion: {
            type: "number",
            validation: {
                required: true,
                min: 0
            },
            defaultValue: 15
        },
        "cost_per_mql__amount": {
            type: "number",
            defaultValue: 100,
            validation: {
                required: true,
                min: 0
            }
        },
        "cost_per_mql__localized": {
            type: "string"
        },
        sales: {
            editable: false,
            type: "number"
        },
        mql: {
            editable: false,
            type: "number"
        },
        contacts: {
            editable: false,
            type: "number"
        },
        sql: {
            editable: false,
            type: "number"
        },
        "budget__amount": {
            validation: {
                required: false,
                min: 0
            },
            defaultValue: 0
        },
        fixed_budget: {
            type: "boolean",
            defaultValue: false
        },
        "budget__localized_whole_number": {
            type: "string"
        },
        "sales_revenue__amount": {
            editable: false,
            type: "number"
        },
        "sales_revenue__localized_whole_number": {
            editable: false,
            type: "string"
        },
        touches_to_mql_conversion: {
            type: "number",
            validation: {
                required: true,
                min: 0
            },
            defaultValue: 1
        },
        segment: {
            required: true,
            type: "string",
            validation: {
                required: true
            }
        },
        marketing_mix: {
            type: "number"
        },
        marketing_mix_locked: {
            type: "boolean"
        },
        touches_per_contact: {
            type: "number",
            defaultValue: 10,
            min: 0
        },
        max_cost_per_mql: {
            type: "number"
        },
        touches: {
            editable: false,
            type: "number"
        }
    },
    id: "slug",
    idField: "slug"
});