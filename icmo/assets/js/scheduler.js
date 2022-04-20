var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.resources = {};

ICMO.apps.resources.scheduler = (function () {
    var defaults = {
            dataSource: {
                autoSync: false
            },
            startTime: new Date("2013/6/13 07:00 AM"),
            timezone: "Etc/UTC",
            views: [
                {
                    type: "timelineWeek",
                    startTime: new Date("2013/6/13 00:00 AM"),
                    majorTick: 1440
                },
                {
                    type: "timelineMonth",
                    startTime: new Date("2013/6/13 00:00 AM"),
                    majorTick: 1440
                },
                "month"

            ],
            editable:false,
            height: 600,
            toolbar: [
                {name: 'append'},
                {
                    template: function (e) {
                        return kendo.template($("#schedulerToolbarTemplate").html())({})
                    }
                }
            ],
            remove: function (e) {
                if (e.task.locked) {
                    ICMO.core.showCenteredNotification("Locked items can only be deleted in the app where they were created (Lead Mix or Budget).");
                    e.preventDefault();
                    return false;
                }
            }
        },
        bindSchedulerTools = function (scheduler, $el, $tools) {
            $tools.find('.scheduler-today').bind('click', function (e) {
                $el.find('.k-scheduler-timeline .k-grid-content').scrollLeft($el.find('.k-current-time').css('left').replace('px', ''));
            });
        },
        msg_all_segments_view_not_allows = "This action can not be performed on the summary view.  Please switch to a segment view and try again.",
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
            settings.dataSource.schema = ICMO.core.getSchema(ICMO.models.SchedulerEvent);

            $el.kendoScheduler(settings);
            var scheduler = $el.data('kendoScheduler');

            bindSchedulerTools(scheduler, $el, $('.k-scheduler-toolbar'));

            scheduler.bind('dataBound', function (e) {
                $.each(scheduler.dataSource.data(), function (idx, dataItem) {
                });
            });

            /* lock all budget items at their original orderId and parentId */
            scheduler.dataSource.bind("change", function (e) {
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
                            item.parentId = item.originalParentId;
                            item.title = item.originalTitle;
                        }
                    });
                }
            });
        }
    }

}());


ICMO.models.SchedulerEvent = kendo.data.SchedulerEvent.define({
    fields: {
        company: {
            type: "string",
            editable: false
        },
        created: {
            type: "date",
            editable: false
        },
        description: {
            type: "string"
        },
        end: {
            from: "end_datetime",
            required: true,
            type: "date",
            validation: {
                required: true
            }
        },
        gantt_task: {
            type: "string",
            editable: false
        },
        isAllDay: {from: "is_all_day", type: "boolean"},
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
        recurrenceId: {
            from: "recurrence",
            type: "string"
        },
        recurrenceException: {
            from: "recurrence_exception",
            type: "string"
        },
        recurrenceRule: {
            from: "recurrence_rule",
            type: "string"
        },
        revenue_plan: {
            type: "string",
            editable: false
        },
        taskId: {
            from: "slug",
            type: "string",
            editable: false
        },
        start: {
            from: "start_datetime",
            required: true,
            type: "date",
            validation: {
                required: true
            }
        },
        title: {
            required: true,
            type: "string",
            validation: {
                required: true
            }
        }
    },
    idField: "taskId",
    id: "taskId"
});
