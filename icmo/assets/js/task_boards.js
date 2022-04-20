var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.user = '';
ICMO.models = ICMO.models || {};
ICMO.apps.task_boards = {};
ICMO.apps.task_boards.cache = {};
ICMO.apps.task_boards.tags = [];
ICMO.apps.task_boards.task_boards_list = (function () {
    var defaults = {
        columns: [
            {field: 'slug', hidden: true},
            {
                field: 'name', title: 'Name',
                template: '<a href="#:url#"><b>#: name #</b></a>',
                attributes: {
                    style: "border-right: 1px solid rgb(219,219,219) !important;"
                }
            },
            {field: 'modified', title: 'Modified', format: "{0:g}"},
            {field: 'modified_by_name', title: 'Modified By'},
            {
                field: 'created', title: 'Created', format: "{0:g}", attributes: {
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
    };
    return {
        createGrid: function ($el) {
            var contextMenuOptions = [
                    {
                        action: 'delete',
                        visible: function ($el) {
                            var grid = ICMO.grid.tools.getGridBy$El($el),
                                $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                                dataItem = grid.dataItem($targetRow);
                            if (dataItem.owner) {
                                return false;
                            }
                            return ICMO.core.hasChangePermission;
                        }
                    }
                ],
                settings = $.extend({}, defaults);
            ICMO.core.hasChangePermission = true;
            ICMO.grid.create($el, ICMO.models.TaskBoard, settings, null, contextMenuOptions);
            return $el.data("kendoGrid");
        }
    }
}());

ICMO.apps.task_boards.task_board = (function () {
    var getTasksDataSource = function ($el, dataReadFilter) {
            var dataSource = new kendo.data.DataSource({
                transport: ICMO.core.getTransportByURL($el.data('tasks-api-url'), 'uuid', dataReadFilter),
                schema: {
                    model: ICMO.models.Task,
                    hasChildren: false
                }
            });
            dataSource.bind("error", ICMO.core.alertErrorAndRefresh);
            return dataSource;
        },
        getTaskListsDataSource = function ($el) {
            var dataSource = new kendo.data.DataSource({
                transport: ICMO.core.getTransportByURL($el.data('task-lists-api-url'), 'uuid'),
                schema: {
                    model: ICMO.models.TaskList
                }
            });
            dataSource.bind("error", ICMO.core.alertErrorAndRefresh);
            return dataSource;
        },
        placeholder = function (element) {
            return element.clone().addClass("placeholder");
        },
        hint = function (element) {
            return element.clone().addClass("hint")
                .height(element.height())
                .width(element.width());
        },
        addTaskExpander = function ($task) {
            $task.on('show.bs.collapse', function (e) {
                $(e.target).find('.task-expander i').removeClass('fa-expand').addClass('fa-compress');
            });
            $task.on('hide.bs.collapse', function (e) {
                $(e.target).find('.task-expander i').removeClass('fa-compress').addClass('fa-expand');
            });
        },
        saveTaskChanges = function (task, $task) {
            task.dirty = true;
            TasksDataSource.sync().done(function () {
                replaceTask(task, $task);
            });
        },
        getTaskListEditableHandler = function () {
            return function (e, params) {
                var propName = $(this).data('editable').options.name,
                    $list = $(e.target).closest('.task-list'),
                    taskList = TaskListsDataSource.getByUid($list.data('kendo-uid'));
                taskList[propName] = params.newValue;
                taskList.dirty = true;
                TaskListsDataSource.sync();
            }
        },
        getTaskEditableHandler = function () {
            return function (e, params) {
                var propName = $(this).data('editable').options.name,
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                task[propName] = params.newValue;
                saveTaskChanges(task, $task);
            }
        },
        getAddChecklistHandler = function () {
            return function (e) {
                var $checklist = $(e.target).closest('.new-checklist'),
                    name = $checklist.find('input[type="text"]').val(),
                    checked = $checklist.find('input[type="checkbox"]').prop('checked'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                task.checklist.push({name: name, completed: checked || false});
                saveTaskChanges(task, $task);
            }
        },
        getModifyChecklistHandler = function () {
            return function (e, params) {
                var $checklist = $(e.target).closest('.existing-checklist'),
                    uuid = $checklist.data('checklist-uuid'),
                    checked = $checklist.find('input[type="checkbox"]').prop('checked'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.checklist.length; i++) {
                    if (task.checklist[i].uuid == uuid) {
                        task.checklist[i].completed = checked || false;
                        task.checklist[i].action = 'modify';
                        if (params) {
                            task.checklist[i].name = params.newValue;
                        }
                    }
                }
                saveTaskChanges(task, $task);
            }
        },
        getDeleteChecklistHandler = function () {
            return function (e) {
                var $checklist = $(e.target).closest('.existing-checklist'),
                    uuid = $checklist.data('checklist-uuid'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.checklist.length; i++) {
                    if (task.checklist[i].uuid == uuid) {
                        task.checklist[i].action = 'delete';
                    }
                }
                saveTaskChanges(task, $task);
            }
        },
        getAddCommentHandler = function () {
            return function (e) {
                var $task = $(e.target).closest('.task'),
                    comment = $task.find('.new-comment').val(),
                    task = TasksDataSource.get($task.data('uuid'));
                task.comments.push({comment: comment});
                saveTaskChanges(task, $task);
            }
        },
        getModifyCommentHandler = function () {
            return function (e, params) {
                var $comment = $(e.target).closest('.comment'),
                    uuid = $comment.data('comment-uuid'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.comments.length; i++) {
                    if (task.comments[i].uuid == uuid && task.comments[i].author == ICMO.user) {
                        task.comments[i].action = 'modify';
                        task.comments[i].comment = params.newValue;
                    }
                }
                saveTaskChanges(task, $task);
            }
        },
        getModifyCheckboxHandler = function () {
            return function (e) {
                var $target = $(e.target),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                task[$target.data('name')] = $target.prop('checked');
                saveTaskChanges(task, $task);
            }
        },
        getDeleteCommentHandler = function () {
            return function (e) {
                var $comment = $(e.target).closest('.comment'),
                    uuid = $comment.data('comment-uuid'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.comments.length; i++) {
                    if (task.comments[i].uuid == uuid && task.comments[i].author == ICMO.user) {
                        task.comments[i].action = 'delete';
                        task.dirty = true;
                    }
                }
                saveTaskChanges(task, $task);
            }
        },
        getStatusButtonHandler = function () {
            return function (e) {
                var $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                task['status'] = $(e.target).data('next-status');
                saveTaskChanges(task, $task);
            }
        },
        replaceTask = function (task, $task) {
            var $list = $task.closest('.task-list'),
                $newTask = renderTask(task, $list);
            // restore expansion
            $newTask.find('.collapse').attr('class', $task.find('.collapse').attr('class'));
            // restore tab
            var activeTab = $task.find('a[role="tab"][aria-expanded="true"]').attr('href');
            $task.replaceWith($newTask);
            $('a[href="' + activeTab + '"]').tab('show');
        },
        getMoveTargetUUID = function ($el, selector, index) {
            console.log($el.data('kendoSortable'));
            var sortable = $el.data('kendoSortable');
            if (sortable.items().get(index)) {
                return $(sortable.items().get(index)).data('uuid');
            }
            return 'bottom';
        },
        renderTaskList = function (taskList) {
            var list_template = kendo.template($('#blankTaskList').html());
            var $list = $(list_template(taskList));
            $list.find('.editable').editable();
            $list.find('.editable').on('save', getTaskListEditableHandler());

            $list.find('.box-body').kendoSortable({
                filter: ">.task",
                cursor: "move",
                placeholder: placeholder,
                hint: hint,
                connectWith: '.task-list .box-body',
                ignore: 'input,select,textarea',
                change: function (e) {
                    console.log("from " + e.oldIndex + " to " + e.newIndex + " action " + e.action);
                    var $task = $(e.item),
                        $list = $task.closest('.task-list'),
                        task = TasksDataSource.get($task.data('uuid'));
                    if (e.action == 'receive') {
                        task.task_list = $list.data('uuid');
                        task.move_above = getMoveTargetUUID($list.find('.box-body'), '.task', e.newIndex + 1);
                    } else if (e.action == 'sort') {
                        task.move_above = getMoveTargetUUID($list.find('.box-body'), '.task', e.newIndex + 1);
                    } else if (e.action == 'remove') {
                        return;
                    }
                    console.log('move ' + task.uuid + ' above ' + task.move_above);
                    task.dirty = true;
                    TasksDataSource.sync();
                }
            });
            return $list;
        },
        renderTask = function (task) {
            var task_template = kendo.template($('#blankTask').html()),
                $task = $(task_template(task));
            $task.find('.editable').editable();
            $task.find('.editable').on('save', getTaskEditableHandler(TaskListsDataSource));
            $task.find('button.status-change').on('click', getStatusButtonHandler());
            if (task.segment) {
                $task.find('.bli-select').editable({
                    name: 'budget_line_item',
                    value: task.budget_line_item,
                    type: 'select',
                    mode: 'popup',
                    source: getBLIList(task)
                }).on('save', getTaskEditableHandler());
                $task.find('.program-select').editable({
                    name: 'program',
                    value: task.program,
                    type: 'select',
                    mode: 'popup',
                    source: getProgramList(task)
                }).on('save', getTaskEditableHandler());
            }
            /* checklists */
            $task.find('.add-new-checklist').click(getAddChecklistHandler());
            $task.find('.existing-checklist input[type="checkbox"]').click(getModifyChecklistHandler());
            $task.find('.existing-checklist .delete-checklist').click(getDeleteChecklistHandler());
            $task.find('.existing-checklist .rename-checklist').editable();
            $task.find('.existing-checklist .rename-checklist').on('save', getModifyChecklistHandler());

            /* comments */
            $task.find('.add-comment').click(getAddCommentHandler());
            $task.find('.delete-comment').click(getDeleteCommentHandler());
            $task.find('.edit-comment').editable();
            $task.find('.edit-comment').on('save', getModifyCommentHandler());

            /* tags */
            $task.find('.edit-tags').editable({
                select2: {
                    tags: ICMO.apps.task_boards.tags,
                    tokenSeparators: [","]
                }
            });
            $task.find('.edit-tags').on('save', getTaskEditableHandler(TaskListsDataSource));
            $task.find('.private').change(getModifyCheckboxHandler());
            $task.find('.assign_gantt').change(getModifyCheckboxHandler());

            $task.find('.delete-task').click(function (e) {
                bootbox.confirm("Are you sure you want to delete this task?", function () {
                    var $task = $(e.target).closest('.task'),
                        task = TasksDataSource.get($task.data('uuid'));
                    console.log(task);
                    TasksDataSource.remove(task);
                    TasksDataSource.sync().done(function () {
                        $task.remove();
                    });
                });
            });
            $task.find('.add-user').click(function (e) {
                var $container = $(e.target).closest('.add-user-container'),
                    email = $container.find('.add-user-email').val(),
                    role = $container.find('.add-user-role').val(),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                if (!email || !role) {
                    return;
                }
                task['assigned_users'].push({user: email, role: role, action: 'new'});
                saveTaskChanges(task, $task);
            });
            $task.find('.delete-user').click(function (e) {
                var $container = $(e.target).closest('.existing-user-container'),
                    email = $container.data('user-email'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.assigned_users.length; i++) {
                    if (task.assigned_users[i].user == email) {
                        task.assigned_users[i].action = 'delete';
                    }
                }
                saveTaskChanges(task, $task);
            });
            $task.find('.existing-user-role').editable();
            $task.find('.existing-user-role').on('save', function (e, params) {
                var $container = $(e.target).closest('.existing-user-container'),
                    email = $container.data('user-email'),
                    $task = $(e.target).closest('.task'),
                    task = TasksDataSource.get($task.data('uuid'));
                for (var i = 0; i < task.assigned_users.length; i++) {
                    if (task.assigned_users[i].user == email) {
                        task.assigned_users[i].action = 'modify';
                        task.assigned_users[i].role = params.newValue;
                    }
                }
                saveTaskChanges(task, $task);
            });

            addTaskExpander($task);
            return $task;
        },
        loadTaskBoard = function () {
            $.each(TaskListsDataSource.data(), function (idx, taskList) {
                var $list = renderTaskList(taskList);
                $('#add-task-list-container').before($list);
                loadTaskList(taskList, $list);
            });

        },
        loadTaskList = function (taskList, $list) {
            $.each(getTasks(taskList), function (t_idx, task) {
                var $task = renderTask(task);
                $list.find('.box-body').append($task);
            });
        },
        getTasks = function (taskList) {
            var tasks = [];
            for (var i = 0; i < TasksDataSource.data().length; i++) {
                if (TasksDataSource.data()[i].task_list == taskList.uuid) {
                    tasks.push(TasksDataSource.data()[i]);
                }
            }
            return tasks;
        },
        getProgramList = function (task) {
            if (!ICMO.apps.task_boards.cache.programs) {
                $.ajax({
                    url: $('#taskBoard').data('segments-list-api-url') + task.segment + '/programs/',
                    async: false,
                    dataType: 'json',
                    success: function (data) {
                        var output = [];
                        $.each(data, function (idx, item) {
                            output.push({value: item.slug, text: item.name});
                        });
                        ICMO.apps.task_boards.cache.programs = output;
                        return ICMO.apps.task_boards.cache.programs;
                    }
                })
            }
            return ICMO.apps.task_boards.cache.programs;
        },
        getBLIList = function (task) {
            if (!ICMO.apps.task_boards.cache.budget_line_items) {
                $.ajax({
                    url: $('#taskBoard').data('segments-list-api-url') + task.segment + '/budget_line_items/',
                    async: false,
                    dataType: 'json',
                    success: function (data, textStatus, jqXHR) {
                        var output = [];
                        $.each(data, function (idx, bli) {
                            output.push({
                                value: bli.slug,
                                text: bli.name + ' (' + bli.item_type + ')'
                            });
                        });
                        ICMO.apps.task_boards.cache.budget_line_items = output;
                        return ICMO.apps.task_boards.cache.budget_line_items;
                    }
                })
            }
            return ICMO.apps.task_boards.cache.budget_line_items;
        },
        storeDataReadFilter = function (dataReadFilter) {
            var hashes = dataReadFilter.split("&"),
                hash = null;
            for (var i = 0; i < hashes.length; i++) {
                hash = hashes[i].split('=');
                if (hash[0] == 'segment') {
                    filterSegment = hash[1];
                } else if (hash[0] == 'program') {
                    filterProgram = hash[1];
                } else if (hash[0] == 'bli') {
                    filterBLI = hash[1];
                }
            }
        },
        filterSegment = null,
        filterProgram = null,
        filterBLI = null,
        TasksDataSource = null,
        TaskListsDataSource = null;
    return {
        createTaskBoard: function ($el, userEmail, dataReadFilter) {
            ICMO.user = userEmail;
            storeDataReadFilter(dataReadFilter);
            // configuration of the products service end-point
            TasksDataSource = getTasksDataSource($el, dataReadFilter);
            TaskListsDataSource = getTaskListsDataSource($el);
            TaskListsDataSource.read().done(function () {
                TasksDataSource.read().done(function () {
                    loadTaskBoard();
                })
            });

            $el.find('.add-task-list').click(function () {
                var taskList = TaskListsDataSource.add({name: 'New Task List'});
                TaskListsDataSource.sync().done(function () {
                    var $list = renderTaskList(taskList);
                    $('#add-task-list-container').before($list);
                });
            });

            $(document).on('click', '.add-task', function (e) {
                var $list = $(e.target).closest('.task-list'),
                    task = TasksDataSource.add({
                        task_list: $list.data('uuid'),
                        segment: filterSegment,
                        program: filterProgram,
                        budget_line_item: filterBLI
                    });
                TasksDataSource.sync().done(function () {
                    var $task = renderTask(task, $list);
                    $list.find('.box-body').append($task);
                });
            });
            $(document).on('click', '.delete-tasklist', function (e) {
                bootbox.confirm("Are you sure you want to delete this task list?", function () {
                    var $list = $(e.target).closest('.task-list'),
                        list = TaskListsDataSource.get($list.data('uuid'));
                    TaskListsDataSource.remove(list);
                    TaskListsDataSource.sync().done(function () {
                        $list.remove();
                    });
                });
            });
            $el.kendoSortable({
                filter: ">.task-list",
                cursor: "move",
                placeholder: placeholder,
                hint: hint,
                handler: ".box-header",
                ignore: '.task, .task-header,input,select,textarea',
                change: function (e) {
                    console.log("from " + e.oldIndex + " to " + e.newIndex + " action " + e.action);
                    var $list = $(e.item),
                        list = TaskListsDataSource.get($list.data('uuid'));
                    console.log($list);
                    list.move_above = getMoveTargetUUID($el, '.task-list', e.newIndex + 1);
                    list.dirty = true;
                    TaskListsDataSource.sync();
                }
            });
            $('.task-filter').find('select').change(function (e) {
                var url = location.pathname,
                    args = [],
                    $taskFilter = $('.task-filter'),
                    segmentFilter = $taskFilter.find('.segment-filter').val(),
                    programFilter = $taskFilter.find('.program-filter').val(),
                    bliFilter = $taskFilter.find('.bli-filter').val();
                if (segmentFilter) {
                    args.push("segment=" + segmentFilter);
                    if (programFilter) {
                        args.push("program=" + programFilter);
                    }
                    if (bliFilter) {
                        args.push("bli=" + bliFilter);
                    }
                }
                if (args) {
                    url += "?" + args.join("&");
                }
                location.href = url;
            });
            console.log(TaskListsDataSource);
        }
    }
}());


ICMO.models.TaskBoard = kendo.data.Model.define({
    fields: {
        company: {
            type: "string",
            editable: false
        },
        revenue_plan: {
            type: "string",
            editable: false
        },
        name: {
            type: "string",
            editable: true
        },
        url: {
            type: "string",
            editable: false
        },
        slug: {
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
        }
    },
    id: "slug"
});


ICMO.models.TaskList = kendo.data.Model.define({
    fields: {
        task_board: {
            type: "string",
            editable: false
        },
        name: {
            type: "string",
            editable: true
        },
        uuid: {
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
        }
    },
    id: "uuid"
});


ICMO.models.Task = kendo.data.Model.define({
    fields: {
        "budget_line_item": {
            "type": "string"
        },
        "budget_line_item_name": {
            "type": "string",
            "editable": false
        },
        "created": {
            "type": "date",
            "editable": false
        },
        "description": {
            "type": "string"
        },
        "checklist_status": {
            "type": "string",
            "editable": false
        },
        "comments_count": {
            "type": "string",
            "editable": false
        },
        "modified": {
            "type": "date",
            "editable": false
        },
        "modified_by": {
            "type": "string",
            "editable": false
        },
        "modified_by_name": {
            "type": "string",
            "editable": false
        },
        "name": {
            "type": "string"
        },
        "priority": {
            "type": "string"
        },
        "priority_name": {
            "type": "string",
            "editable": false
        },
        "program": {
            "type": "string"
        },
        "program_name": {
            "type": "string",
            "editable": false
        },
        "segment": {
            "type": "string"
        },
        "segment_name": {
            "type": "string",
            "editable": false
        },
        "status": {
            "type": "string"
        },
        "status_name": {
            "type": "string",
            "editable": false
        },
        "task_board": {
            "type": "string",
            "editable": false
        },
        "task_board_name": {
            "type": "string",
            "editable": false
        },
        "task_list": {
            "required": true,
            "type": "string",
            "validation": {
                "required": true
            }
        },
        "task_list_name": {
            "type": "string",
            "editable": false
        },
        "task_type": {
            "type": "string"
        },
        "task_type_name": {
            "type": "string",
            "editable": false
        },
        "user_initials": {
            "type": "string",
            "editable": false
        },
        "user_names": {
            "type": "string",
            "editable": false
        },
        "users": {
            "type": "string"
        },
        "uuid": {
            "type": "string",
            "editable": false
        }
    },
    id: "uuid"
});