var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};

ICMO.apps.notifications = (function () {
    var defaults = {
        columns: [
            {field: 'id', hidden: true},
            {field: 'notification_type_display', title: 'Notification Type'},
            {
                field: 'frequency', title: 'Frequency',
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
            ICMO.grid.create($el, ICMO.models.CompanyUserNotificationSubscription, settings, null, contextMenuOptions);
            var grid = $el.data("kendoGrid");
            var $gridTools = $("." + $el.data('tools'));
            grid.bind('dataBound', function () {
                $gridTools.find('.grid-add-notification').click(function () {
                    var $container = $('#addNotificationModal');
                    $container.data('company-slug', $el.attr('id').replace('grid-', ''));
                    $container.data('api-url', $el.data('api-url')).modal();
                    $container.find('form')[0].reset();
                });
            });
            return grid;
        },
        initAddNotificationForm: function () {
            var $container = $('#addNotificationModal'),
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
                        if (data.notification_type) {
                            $container.modal('hide');
                            $('#grid-' + $container.data('company-slug')).data('kendoGrid').dataSource.read();
                        }
                    }
                ).fail(function (e) {
                    if (e.responseJSON) {
                        bootbox.alert(e.responseJSON['non_field_errors'][0]);
                    }
                });
            });
            $submit.click(function (e) {
                $form.submit();
            })
        }
    }
}());

ICMO.models.CompanyUserNotificationSubscription = kendo.data.Model.define({
    fields: {
        company: {
            type: "string",
            editable: false
        },
        company_user: {
            type: "string",
            editable: false
        },
        company_name: {
            type: "string",
            editable: false
        },
        notification_type: {
            type: "string",
            editable: false
        },
        notification_type_display: {
            type: "string",
            editable: false
        },
        frequency: {
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
    id: "id"
});