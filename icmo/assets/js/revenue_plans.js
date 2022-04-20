var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};


ICMO.apps.revenue = (function () {
    var planDefaults = {
            columns: [
                {field: 'slug', hidden: true},
                {
                    field: 'name', title: 'Name',
                    template: '<a href="#:url#"><b>#: name #</b></a>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {field: 'plan_year', title: 'Plan Year', format: "{0:####}"},
                {field: 'plan_type', hidden: true},
                {field: 'modified', title: 'Modified', format: "{0:g}"},
                {field: 'modified_by_name', title: 'Modified By'},
                {field: 'created', title: 'Created', format: "{0:g}"},
                {
                    field: 'owner_name', title: 'Owner',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: '', title: 'Actions',
                    template: function (model) {
                        return kendo.template($('#rowTools').html())(model)
                    }
                }
            ]
        },
        segmentDefaults = {
            columns: [
                {field: 'slug', hidden: true},
                {
                    field: 'name', title: 'Name',
                    template: '<b>#: name #</b>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'average_sale__amount',
                    title: 'Average Sale',
                    template: "#: average_sale__localized #",
                    footerTemplate: '<span title="Average" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(average, "n0") #</span>'

                },
                {
                    field: 'goal_q1__amount',
                    title: 'Q1',
                    template: "#: goal_q1__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'goal_q2__amount',
                    title: 'Q2',
                    template: "#: goal_q2__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },

                {
                    field: 'goal_q3__amount',
                    title: 'Q3',
                    template: "#: goal_q3__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },

                {
                    field: 'goal_q4__amount',
                    title: 'Q4',
                    template: "#: goal_q4__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'goal_annual__amount',
                    title: 'Annual Sales Goal',
                    template: "#: goal_annual__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'prev_average_sale__amount',
                    title: 'Previous Year Average Sale',
                    hidden: true,
                    template: "#: prev_average_sale__localized #",
                    footerTemplate: '<span title="Average" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(average, "n0") #</span>'
                },
                {
                    field: 'prev_q1__amount',
                    title: 'Previous Year Q1',
                    hidden: true,
                    template: "#: prev_q1__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'prev_q2__amount',
                    title: 'Previous Year Q2',
                    hidden: true,
                    template: "#: prev_q2__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },

                {
                    field: 'prev_q3__amount',
                    title: 'Previous Year Q3',
                    hidden: true,
                    template: "#: prev_q3__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'prev_q4__amount',
                    title: 'Previous Year Q4',
                    hidden: true,
                    template: "#: prev_q4__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>'
                },
                {
                    field: 'prev_annual__amount',
                    title: 'Previous Year Sales',
                    hidden: true,
                    template: "#: prev_annual__localized_whole_number #",
                    footerTemplate: '<span title="Sum" data-placement="left"  data-toggle="tooltip" >$#= kendo.toString(sum, "n0") #</span>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: '', title: 'Actions',
                    template: function (model) {
                        return kendo.template($('#rowTools').html())(model)
                    }
                }
            ]
        },
        segmentGridAggregators = [
            {field: 'goal_annual__amount', aggregate: 'sum'},
            {field: 'goal_q1__amount', aggregate: 'sum'},
            {field: 'goal_q2__amount', aggregate: 'sum'},
            {field: 'goal_q3__amount', aggregate: 'sum'},
            {field: 'goal_q4__amount', aggregate: 'sum'},
            {field: 'average_sale__amount', aggregate: 'average'},

            {field: 'prev_annual__amount', aggregate: 'sum'},
            {field: 'prev_q1__amount', aggregate: 'sum'},
            {field: 'prev_q2__amount', aggregate: 'sum'},
            {field: 'prev_q3__amount', aggregate: 'sum'},
            {field: 'prev_q4__amount', aggregate: 'sum'},
            {field: 'prev_average_sale__amount', aggregate: 'average'}
        ],
        clonePlan = function ($el, finishedCallback) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoGrid'),
                dataItem = grid.dataItem($targetRow),
                $container = $('#clonePlanModal');
            $container.modal();
            $('#clonePlanTargetName').html(dataItem.name);
            $container.data('item-slug', dataItem.slug);
            $container.find('form')[0].reset();
            $('#id_name').val(dataItem.name + " - Copy");
            $('#id_year').val(dataItem.plan_year);
        },
        publishPlan = function ($el, finishedCallback) {
            setPlanPublished($el, finishedCallback, 'published');
        },
        unpublishPlan = function ($el, finishedCallback) {
            setPlanPublished($el, finishedCallback, 'draft');
        },
        archivePlan = function ($el, finishedCallback) {
            setPlanPublished($el, finishedCallback, 'archived');
        },
        setPlanPublished = function ($el, finishedCallback, state) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoGrid'),
                dataItem = grid.dataItem($targetRow),
                numPublishedPlans = $('#grid-published').data('kendoGrid').dataSource.data().length;
            if (state == 'published' && numPublishedPlans !== 0) {
                bootbox.alert("Only one plan can be published at a time.");
                return false;
            }
            dataItem.set('plan_type', state);
            grid.dataSource.sync().done(
                function () {
                    if (state == 'published' || state == 'draft') {
                        window.location.reload();
                    }
                    /*$('#grid-published').data('kendoGrid').dataSource.read();
                     $('#grid-draft').data('kendoGrid').dataSource.read();
                     $('#grid-archived').data('kendoGrid').dataSource.read();
                     $('#grid-segments').data('kendoGrid').dataSource.read();
                     */
                }
            )
        },
        cloneSegment = function ($el, finishedCallback) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoGrid'),
                dataItem = grid.dataItem($targetRow),
                $container = $('#cloneSegmentModal');
            $container.modal();
            $('#cloneSegmentTargetName').html(dataItem.name);
            $container.data('item-slug', dataItem.slug);
            $container.find('form')[0].reset();
        },
        toggleColumns = function (grid, hide_column_names, show_column_names) {
            $.each(hide_column_names, function (idx, name) {
                grid.hideColumn(name);
            });
            $.each(show_column_names, function (idx, name) {
                grid.showColumn(name);
            });
        },
        current_columns = [
            'goal_q1__amount', 'goal_q2__amount', 'goal_q3__amount', 'goal_q4__amount',
            'goal_annual__amount', 'average_sale__amount'
        ],
        previous_columns = [
            'prev_q1__amount', 'prev_q2__amount', 'prev_q3__amount', 'prev_q4__amount',
            'prev_annual__amount', 'prev_average_sale__amount'
        ],
        isContextItemVisible = function ($el, plan_type) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoGrid'),
                dataItem = grid.dataItem($targetRow);
            return dataItem.plan_type === plan_type;
        };
    return {
        createRevenueGrid: function ($el, selected_slug) {
            var contextMenuOptions = ['edit', 'delete'];
            contextMenuOptions.push(
                {
                    label: 'Publish', action: 'publish',
                    callback: publishPlan,
                    visible: function ($el) {
                        return isContextItemVisible($el, 'draft');
                    }
                },
                {
                    label: 'Unpublish', action: 'unpublish',
                    callback: unpublishPlan,
                    visible: function ($el) {
                        return isContextItemVisible($el, 'published');
                    }
                },
                {
                    label: 'Archive', action: 'archive',
                    callback: archivePlan,
                    visible: function ($el) {
                        return isContextItemVisible($el, 'draft');
                    }
                },
                {
                    label: 'Unarchive', action: 'unarchive',
                    callback: unpublishPlan,
                    visible: function ($el) {
                        return isContextItemVisible($el, 'archived');
                    }
                },
                {
                    label: 'Clone', action: 'clone',
                    callback: clonePlan,
                    visible: function ($el) {
                        return true;
                    }
                }
            );
            ICMO.grid.create($el, ICMO.models.Plan, planDefaults, null, contextMenuOptions);
            var grid = $el.data('kendoGrid');

            grid.bind('dataBound', function () {
                $.each(grid.dataSource.data(), function (idx, dataItem) {
                    if (dataItem.slug == selected_slug) {
                        $('tr[data-uid="' + dataItem.uid + '"]').addClass("selected-plan")
                    }
                });
            });
        },
        createSegmentGrid: function ($el) {
            var contextMenuOptions = ['edit', 'delete'];
            contextMenuOptions.push({
                label: 'Clone', action: 'clone',
                callback: cloneSegment,
                visible: function ($el) {
                    return true;
                }
            });
            ICMO.grid.create($el, ICMO.models.Segment, segmentDefaults, segmentGridAggregators, contextMenuOptions);
            var grid = $el.data('kendoGrid');
            var $gridTools = $('.' + $el.attr('data-tools'));
            $gridTools.find('.grid-change-view').bind('change', function (e) {
                grid.cancelRow();
                grid.trigger('cancel');
                var view = $(e.target).val();
                if (view === 'current') {
                    toggleColumns(grid, previous_columns, current_columns);
                } else if (view === 'previous') {
                    toggleColumns(grid, current_columns, previous_columns);
                }
            });
        },
        initCloneForm: function ($container, itemType) {
            var $form = $container.find('form'),
                $submit = $container.find('button[type="submit"]');
            $form.formValidation({
                framework: 'bootstrap',
                icon: {
                    valid: 'glyphicon glyphicon-ok',
                    invalid: 'glyphicon glyphicon-remove',
                    validating: 'glyphicon glyphicon-refresh'
                },
                excluded: ':disabled'
            }).on('success.form.fv', function (e) {
                e.preventDefault();
                $.post(
                    $container.data('api-url') + $container.data('item-slug') + "/clone/",
                    $form.serialize(),
                    function (data) {
                        $container.modal('hide');
                        if (itemType.toLowerCase() == 'plan') {
                            $('#grid-draft').data('kendoGrid').dataSource.read();
                        } else {
                            $('#grid-segments').data('kendoGrid').dataSource.read();
                        }
                        bootbox.alert(itemType + " cloned succesfully.  It may take a few minutes for all details to finish copying, depending on the size of the plan.");
                    }
                ).fail(function (e) {
                    if (e.responseJSON) {
                        bootbox.alert(e.responseJSON['error']);
                    }
                });
            });
            $submit.click(function (e) {
                $form.submit();
            })
        }
    }
}());


ICMO.apps.revenue.chart = {
    refresh: function () {
        $('#grid-segments').data('kendoGrid').dataSource.fetch().then(function () {
            var data = $('#grid-segments').data('kendoGrid').dataSource.data();
            var output = [];
            for (var i = 0; i < data.length; i++) {
                output.push({
                    name: data[i].name,
                    amount: data[i].goal_q1__amount,
                    quarter: 'Q1'
                });
                output.push({
                    name: data[i].name,
                    amount: data[i].goal_q2__amount,
                    quarter: 'Q2'
                });
                output.push({
                    name: data[i].name,
                    amount: data[i].goal_q3__amount,
                    quarter: 'Q3'
                });
                output.push({
                    name: data[i].name,
                    amount: data[i].goal_q4__amount,
                    quarter: 'Q4'
                });
            }
            var chartDataSource = new kendo.data.DataSource({
                data: output,
                group: {field: 'name'},
                sort: {field: 'quarter', dir: 'asc'}
            });
            $("#chart").kendoChart({
                theme: 'metro',
                dataSource: chartDataSource,
                seriesDefaults: {
                    type: 'area'
                },
                series: [
                    {
                        field: 'amount',
                        stack: true
                    }
                ],
                valueAxis: [{
                    labels: {
                        format: "${0:n0}"
                    }
                }],
                categoryAxis: {
                    field: 'quarter',
                    labels: {
                        format: "#= series.quarter #"
                    }
                },
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    visible: true,
                    format: "{0}%",
                    template: "#= series.name #: $#= kendo.toString(value, 'n0') #"
                }
            });
        });
    },
    init: function () {
        var that = this;
        $('#grid-segments').data('kendoGrid').dataSource.bind('sync', function () {
            that.refresh();
        });
        this.refresh();
    }
};


ICMO.models.Plan = kendo.data.Model.define({
    fields: {
        modified_by_name: {
            type: "string",
            editable: false
        },
        name: {
            type: "string",
            validation: {
                required: true
            }
            //defaultValue: "Revenue Plan " + new Date().getFullYear(),
        },
        created: {
            type: "date",
            editable: false
        },
        modified: {
            type: "date",
            editable: false
        },
        "owner_name": {
            type: "string",
            editable: false
        },
        slug: {
            type: "string",
            editable: false,
            defaultValue: ""
        },
        plan_year: {
            type: "string",
            validation: {
                required: true,
                min: new Date().getFullYear(),
                max: 2050
            },
            editable: true,
            defaultValue: new Date().getFullYear()
        },
        plan_type: {
            type: "string",
            defaultValue: "draft"
        },
        url: {
            type: "string",
            editable: false
        }
    },
    idField: "slug",
    id: "slug"
});

ICMO.models.Segment = kendo.data.Model.define({
    fields: {
        revenue_plan: {
            type: "string",
            editable: false
        },
        modified_by: {
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
        programs: {
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
        average_sale__amount: {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        average_sale__localized: {
            type: "string"
        },
        "goal_annual__amount": {
            type: "number",
            editable: false
        },
        "goal_annual__localized_whole_number": {
            type: "string"
        },
        modified_by_name: {
            type: "string",
            editable: false
        },
        "goal_q1__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "goal_q1__localized_whole_number": {
            type: "string"
        },
        "goal_q2__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "goal_q2__localized_whole_number": {
            type: "string"
        },
        "goal_q3__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "goal_q3__localized_whole_number": {
            type: "string"
        },
        "goal_q4__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "goal_q4__localized_whole_number": {
            type: "string"
        },


        prev_average_sale__amount: {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        prev_average_sale__localized: {
            type: "string"
        },
        "prev_annual__amount": {
            type: "number",
            editable: false
        },
        "prev_annual__localized_whole_number": {
            type: "string"
        },
        "prev_q1__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "prev_q1__localized_whole_number": {
            type: "string"
        },
        "prev_q2__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "prev_q2__localized_whole_number": {
            type: "string"
        },
        "prev_q3__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "prev_q3__localized_whole_number": {
            type: "string"
        },
        "prev_q4__amount": {
            type: "number",
            validation: {
                required: true,
                min: 0
            }
        },
        "prev_q4__localized_whole_number": {
            type: "string"
        },
        slug: {
            type: "string",
            editable: false
        }
    },
    idField: "slug",
    id: "slug"
});
