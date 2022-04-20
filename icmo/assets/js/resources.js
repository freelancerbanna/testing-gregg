var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.resources = {};

ICMO.apps.resources.gantt = (function () {
    var defaults = {
            dataSource: {
                autoSync: false
            },
            dependencies: {
                autoSync: false
            },
            resources: {
                dataSource: {
                    autoSync: false
                },
                field: "taskResources",
                dataTextField: "full_name"
            },
            assignments: {
                dataSource: {
                    autoSync: false
                },
                dataTaskIdField: 'taskId',
                dataResourceIdField: 'resourceId',
                dataValueField: 'value'
            },
            resizable: true,
            defaultColumns: [
                /*{field: 'locked', title: '', editable: false, sortable: false, width: 20},*/
                {
                    field: 'start',
                    title: 'Start Date',
                    format: "{0:MM/dd/yyyy}",
                    editable: true,
                    sortable: false,
                    width: 100
                },
                {
                    field: 'end',
                    title: 'End Date',
                    format: "{0:MM/dd/yyyy}",
                    editable: true,
                    sortable: false,
                    width: 100
                },
                {field: "taskResources", title: "Task Resources"}
            ],
            views: [
                {type: "week", selected: true},
                "month",
                "year"
            ],
            showWorkHours: true,
            showWorkDays: true,
            messages: {
                deleteTaskConfirmation: "Proceed with task deletion?  <br><span class='text-red'>Caution:  Any subtasks of this task will also be deleted.</span>"
            },
            toolbar: [
                {name: 'append'},
                {
                    template: function (e) {
                        return kendo.template($("#ganttToolbarTemplate").html())({})
                    }
                }
            ],
            remove: function (e) {
                if (e.task.locked) {
                    ICMO.core.showCenteredNotification("Locked items can only be deleted in the app where they were created (Lead Mix or Budget).");
                    e.preventDefault();
                    return false;
                }
            },
            pdf: {
                allPages: true,
                proxyURL: '/k/save/'
            }
        },
        getColumns = function ($el) {
            var columns = jQuery.extend([], defaults.defaultColumns);
            if ($el.data('summary')) {
                columns.unshift(
                    {
                        field: 'fullTitle',
                        title: 'Title',
                        editable: false,
                        sortable: true,
                        width: 225
                    }
                );
            } else {
                columns.unshift(
                    {field: 'title', title: 'Title', editable: true, sortable: false, width: 225}
                );
            }
            return columns;
        },
        bindGanttTools = function (gantt, $el, $tools) {
            $tools.find('.gantt-change-view').bind('change', function (e) {
                var segment = $(e.target).val();
                var url = $el.data('api-url');
                if (segment) {
                    url += "?segment=" + segment;
                }
                gantt.dataSource.options.transport.read.url = url;
                gantt.dataSource.read();
            });
            $tools.find('.gantt-today').bind('click', function (e) {
                $el.find('.k-gantt-timeline .k-grid-content').scrollLeft($el.find('.k-current-time').css('left').replace('px', ''));
            });
            $tools.find('.gantt-pdf').bind('click', function (e) {
                console.log('saving to pdf');
                console.log(gantt);
                gantt.saveAsPDF();
            });
        },
        msg_all_segments_view_not_allows = "Editing is disabled.",
        disableEditing = function ($el, settings) {
            /* remove the append button */
            settings.toolbar = [settings.toolbar[1]];
            settings.add = blockAction(msg_all_segments_view_not_allows);
            settings.edit = blockAction(msg_all_segments_view_not_allows);
            settings.remove = blockAction(msg_all_segments_view_not_allows);
            settings.moveStart = blockAction(msg_all_segments_view_not_allows);
            settings.resizeStart = blockAction(msg_all_segments_view_not_allows);
            settings.columns.splice(2, 0, {
                field: 'segment_name',
                title: 'Segment',
                editable: false,
                sortable: false
            });
            return settings;
        },
        blockAction = function (msg) {
            return function (e) {
                e.preventDefault();
                ICMO.core.showCenteredNotification(msg);
                return false;
            }
        };
    return {
        create: function ($el) {
            var settings = $.extend({}, defaults);
            settings.dataSource.transport = ICMO.core.getTransport($el, null, 'slug');
            settings.dataSource.schema = ICMO.core.getSchema(ICMO.models.GanttTask);
            settings.dependencies.transport = ICMO.core.getTransport($el, 'dependencies-api-url', 'dependency_id');
            settings.dependencies.schema = ICMO.core.getSchema(ICMO.models.GanttDependency);
            settings.resources.dataSource.transport = ICMO.core.getTransport($el, 'resources-api-url', 'email');
            settings.resources.dataSource.schema = ICMO.core.getSchema(ICMO.models.IcmoUser);
            settings.assignments.dataSource.transport = ICMO.core.getTransport($el, 'assignments-api-url', 'email');
            settings.assignments.dataSource.schema = ICMO.core.getSchema(ICMO.models.UserTask);
            settings.columns = getColumns($el);

            if (!ICMO.core.hasChangePermission) {
                settings = disableEditing($el, settings);
            }
            $el.kendoGantt(settings);
            var gantt = $el.data('kendoGantt');

            bindGanttTools(gantt, $el, $el.find('.k-gantt-toolbar'));

            gantt.bind('dataBound', function (e) {
                $.each(gantt.dataSource.data(), function (idx, dataItem) {
                    var $tr = $('tr[data-uid="' + dataItem.uid + '"]');
                    var $task = $('.k-task-single[data-uid="' + dataItem.uid + '"]');
                    if (dataItem.locked) {
                        $tr.addClass("gantt-imported");
                        $task.addClass("gantt-imported");
                        $tr.find('td:nth-of-type(2)').html("<i class='fa fa-lock'></i>");
                    }
                    if (dataItem.pastDue) {
                        $tr.addClass("gantt-past-due");
                        $task.addClass("gantt-past-due");
                        $tr.attr("title", "Past due");
                    } else {
                        $tr.removeClass("gantt-past-due");
                        $task.removeClass("gantt-past-due");
                        $tr.attr("title", "");
                    }
                    if (dataItem.atRisk) {
                        $tr.addClass("gantt-at-risk");
                        $task.addClass("gantt-at-risk");
                        $tr.attr("title", "At Risk");
                    } else {
                        $tr.removeClass("gantt-at-risk");
                        $task.removeClass("gantt-at-risk");
                        $tr.attr("title", "");
                    }
                });
            });

            /* lock all budget items at their original orderId and parentId */
            gantt.dataSource.bind("change", function (e) {
                if (e.action === 'itemchange' && (e.field === 'orderId' || e.field === 'parentId' || e.field === 'title')) {
                    $.each(e.items, function (idx, item) {
                        if (item.locked) {
                            if (item.parentId !== item.originalParentId) {
                                ICMO.core.showCenteredNotification("Categories, programs, and other items automatically synchronized with the Budget App can only be rearranged or removed in the Budget App.");
                            }
                            if (item.title != item.originalTitle) {
                                ICMO.core.showCenteredNotification("Locked items can only be renamed in the app where they were created (Lead Mix or Budget).");
                            }
                            item.orderId = item.originalOrderId;
                            item.reorderTarget = null;
                            item.parentId = item.originalParentId;
                            item.title = item.originalTitle;
                        }
                    });
                }
            });
        },
        refreshGantt: function (e) {
            var $el;
            if ($(e.target).hasClass('collapse')) {
                $el = $(e.target).closest('.tab-pane');
            } else {
                $el = $("#" + e.target.href.split("#")[1]);
            }
            $el.find('[data-role="gantt"]').each(function (idx, item) {
                var gantt = $(item).data('kendoGantt');
                gantt.wrapper.css("height", "");
                console.log($el.find('.k-gantt-treelist'));
                $el.find('.k-gantt-treelist').width(342);
                gantt.resize();
                gantt.view('week');
            });
        }
    }

}());


ICMO.models.GanttTask = kendo.data.GanttTask.define({
    id: "id",
    fields: {
        id: {from: "slug", type: "string"},
        orderId: {from: "order", type: "number", validation: {required: true}},
        originalOrderId: {from: "original_order", type: "number", readOnly: true},
        parentId: {
            from: "parent",
            type: "string",
            defaultValue: null,
            validation: {required: true}
        },
        reorderTarget: {from: "reorder_target", type: "string"},
        originalParentId: {from: "original_parent", type: "string", readOnly: true},
        start: {from: "start_date", type: "date"},
        end: {from: "end_date", type: "date"},
        title: {from: "title", defaultValue: "", type: "string"},
        fullTitle: {from: "full_title", defaultValue: "", type: "string", readOnly: true},
        originalTitle: {from: "original_title", type: "string", readOnly: true},
        percentComplete: {from: "percent_complete", type: "number"},
        summary: {from: "summary", type: "boolean"},
        expanded: {from: "expanded", type: "boolean", defaultValue: true},
        locked: {from: "locked", type: "boolean", readOnly: true},
        pastDue: {from: "past_due", type: "boolean", readOnly: true},
        atRisk: {from: "at_risk", type: "boolean", readOnly: true}
    }
});

ICMO.models.GanttDependency = kendo.data.GanttDependency.define({
    id: "id",
    fields: {
        id: {from: 'dependency_id', type: 'string'},
        predecessorId: {from: "predecessor", type: "string"},
        successorId: {from: "successor", type: "string"},
        type: {from: "item_type", type: "number"}
    }
});

ICMO.models.UserTask = kendo.data.Model.define({
    id: "id",
    fields: {
        id: {from: 'assignment_id', type: 'string'},
        taskId: {from: "task", type: "string", validation: {required: true}},
        resourceId: {from: "resource", type: "string", validation: {required: true}},
        value: {from: "value", type: "number"}
    }
});