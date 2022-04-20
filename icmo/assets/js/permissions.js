var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.permissions = {};

ICMO.apps.permissions.users = (function () {
    var getGroupEditor = function (container, options, groupDataSource) {
            if (options.model.owner) {
                $('<span>Cannot change owners group</span>').appendTo(container);
            } else {

                $('<input required data-text-field="name" data-value-field="slug" data-bind="value:' + options.field + '"/>')
                    .appendTo(container)
                    .kendoDropDownList({
                        autoBind: false,
                        dataSource: groupDataSource
                    });
            }
        },
        getSegmentRestrictionEditor = function (container, options) {
            if (options.model.owner) {
                $('<span>Cannot restrict owners segments</span>').appendTo(container);
            } else {

                $('<textarea data-bind="value:' + options.field + '"/>')
                    .appendTo(container);
            }
        },
        getDefaults = function (groupDataSource) {
            return {
                columns: [
                    {field: 'slug', hidden: true},
                    {
                        field: 'user',
                        title: 'Name',
                        template: "#: user_name #",
                        attributes: {
                            style: "border-right: 1px solid rgb(219,219,219) !important;"
                        }
                    },
                    {field: 'user_email', title: 'Email'},
                    {
                        field: 'group', title: 'Group',
                        template: "#: group_name #",
                        editor: function (container, options) {
                            return getGroupEditor(container, options, groupDataSource);
                        }
                    },
                    {field: 'title', title: 'Title'},
                    {
                        field: 'permitted_segments_list',
                        title: 'Segment Restrictions',
                        editor: getSegmentRestrictionEditor
                    },
                    {field: 'owner', title: 'Owner', template: "# if (owner){ #Yes#}else{#No#}#"},
                    {
                        field: '', title: 'Actions',
                        template: function (model) {
                            return kendo.template($('#rowTools').html())(model)
                        }
                    }
                ]
            }
        };
    return {
        createGrid: function ($el, groupDataSource) {
            var contextMenuOptions = ['edit',
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
                settings = $.extend({}, getDefaults(groupDataSource));

            ICMO.grid.create($el, ICMO.models.CompanyUser, settings, null, contextMenuOptions);
            var grid = $el.data("kendoGrid");
            var $gridTools = $("." + $el.data('tools'));
            grid.bind('dataBound', function () {
                $gridTools.find('.grid-add-user').click(function () {
                    var $container = $('#addUserModal');
                    $container.data('company-slug', $el.attr('id').replace('grid-users-', ''));
                    $container.data('api-url', $el.data('api-url')).modal();
                    $container.find('input[name="group"]').kendoDropDownList({
                        autoBind: false,
                        dataSource: $('#grid-groups-' + $container.data('company-slug')).data('kendoGrid').dataSource
                    });
                    $container.find('form')[0].reset();
                });
            });
            return grid;
        }
    }
}());

ICMO.apps.permissions.initAddUserForm = function () {
    var $container = $('#addUserModal'),
        $form = $container.find('form'),
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
            $container.data('api-url'),
            $form.serialize(),
            function (data) {
                if (data.slug) {
                    $container.modal('hide');
                    $('#grid-users-' + $container.data('company-slug')).data('kendoGrid').dataSource.read();
                }
            }
        ).fail(function (e) {
            if (e.responseJSON) {
                bootbox.alert(e.responseJSON[0]);
            }
        });
    });
    $submit.click(function (e) {
        $form.submit();
    })
};


ICMO.apps.permissions.groups = (function () {
    var getPermissionEditor = function (container, options) {
            var $select = $('<select/>'),
                $option,
                permissionOptions = {'none': 'None', 'view': 'View', 'change': 'Change'};
            $select.attr('name', options.field);
            $.each(permissionOptions, function (value, label) {
                $option = $('<option/>');
                $option.attr('value', value);
                $option.html(label);
                $select.append($option);
            });
            $select.val(options.model[options.field]);
            container.append($select);
        },

        defaults = {
            columns: [
                {field: 'slug', hidden: true},
                {
                    field: 'name',
                    title: 'Name',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {field: 'revenue_plans', title: 'Revenue Plans', editor: getPermissionEditor},
                {field: 'program_mix', title: 'Marketing Mix', editor: getPermissionEditor},
                {field: 'budgets', title: 'Budgets', editor: getPermissionEditor},
                {field: 'resources', title: 'Team Schedule', editor: getPermissionEditor},
                {field: 'task_boards', title: 'Task Boards', editor: getPermissionEditor},
                {field: 'performance', title: 'Performance', editor: getPermissionEditor},
                {field: 'dashboards', title: 'Dashboards', editor: getPermissionEditor},
                {field: 'permissions', title: 'Permissions', editor: getPermissionEditor},
                {field: 'live_plan_only', title: 'Live Plan Only'},
                {field: 'permitted_segments_list', title: 'Segment Restrictions'}
                /*
                 {
                 field: '', title: 'Actions',
                 template: function (model) {
                 return kendo.template($('#rowTools').html())(model)
                 }
                 }*/
            ]
        };
    return {
        createGrid: function ($el) {
            var contextMenuOptions = [
                    {
                        action: 'edit',
                        visible: function ($el) {
                            var grid = ICMO.grid.tools.getGridBy$El($el),
                                $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                                dataItem = grid.dataItem($targetRow);
                            if (!dataItem.editable) {
                                return false;
                            }
                            return ICMO.core.hasChangePermission;
                        }
                    },
                    {
                        action: 'delete',
                        visible: function ($el) {
                            var grid = ICMO.grid.tools.getGridBy$El($el),
                                $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                                dataItem = grid.dataItem($targetRow);
                            if (!dataItem.editable) {
                                return false;
                            }
                            return ICMO.core.hasChangePermission;
                        }
                    }
                ],
                settings = $.extend({}, defaults);
            ICMO.grid.create($el, ICMO.models.CompanyUserGroup, settings, null, contextMenuOptions);
            return $el.data("kendoGrid");
        }
    }
}());

ICMO.models.CompanyUser = kendo.data.Model.define({
    fields: {
        company: {
            type: "string",
            editable: false
        },
        company_name: {
            type: "string",
            editable: false
        },
        created: {
            type: "date",
            editable: false
        },
        group: {
            required: true,
            type: "string",
            validation: {
                required: true
            }
        },
        group_name: {
            type: "string",
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
        owner: {
            type: 'boolean',
            editable: false
        },
        permitted_segments_list: {
            type: "string"
        },
        slug: {
            type: "string",
            editable: false
        },
        title: {
            type: "string"
        },
        user: {
            required: true,
            type: "string",
            editable: false
        },
        user_name: {
            type: "string",
            editable: false
        },
        user_email: {
            type: "string",
            editable: false
        }
    },
    idField: "slug",
    id: "slug"
});


ICMO.models.CompanyUserGroup = kendo.data.Model.define({
    fields: {
        archive_plans: {type: 'boolean'},
        budgets: {
            type: "string",
            defaultValue: 'none'
        },
        company: {
            type: "string",
            editable: false
        },
        company_name: {
            type: "string",
            editable: false
        },
        created: {
            type: "date",
            editable: false
        },
        dashboards: {
            type: "string",
            defaultValue: 'none'
        },
        editable: {
            type: 'boolean',
            editable: false
        },
        live_plan_only: {
            type: 'boolean',
            defaultValue: true
        },
        moderate_shares: {type: 'boolean'},
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
        performance: {
            type: "string",
            defaultValue: 'none'
        },
        permissions: {
            type: "string",
            defaultValue: 'none'
        },
        permitted_segments_list: {
            type: "string",
            defaultValue: ''
        },
        program_mix: {
            type: "string",
            defaultValue: 'none'
        },
        publish_plans: {string: 'boolean', defaultValue: false},
        resources: {
            type: "string",
            defaultValue: 'none'
        },
        revenue_plans: {
            type: "string",
            defaultValue: 'none'
        },
        share: {
            type: "string"
        },
        slug: {
            type: "string",
            editable: false
        },
        task_boards: {
            type: "string",
            defaultValue: 'none'
        }
    },
    idField: "slug",
    id: "slug"
});