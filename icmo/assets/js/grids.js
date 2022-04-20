var ICMO = ICMO || {};
ICMO.grid = (function () {
    var defaults = {
        dataSource: {
            autoSync: false,
            pageSize: 100
        },
        sortable: true,
        /*selectable: "multiple cell",
         allowCopy: true,*/
        pageable: true,
        navigatable: true,
        editable: {
            mode: 'inline',
            confirmation: false
        },
        scrollable: true,
        mobile: true,
        resizable: true,
        noRecords: {
            template: "<tr><td colspan=8>No items found.</td></tr>"
        },
        excel: {
            allPages: true,
            proxyURL: '/k/save/'
        },
        excelExport: function (e) {
            var rows = e.workbook.sheets[0].rows;
            for (var ri = 0; ri < rows.length; ri++) {
                var row = rows[ri];
                if (row.type == "group-footer" || row.type == "footer") {
                    for (var ci = 0; ci < row.cells.length; ci++) {
                        var cell = row.cells[ci];
                        if (cell.value) {
                            // Use jQuery.fn.text to remove the HTML and get only the text
                            cell.value = $(cell.value).text();
                        }
                    }
                }
            }
        },
        pdf: {
            allPages: true,
            proxyURL: '/k/save/'
        }
    };
    return {
        create: function ($el, model, userOptions, userAggregators, userContextMenuOptions, finishedCallback) {
            var settings = $.extend({}, defaults, userOptions),
                contextMenuOptions = userContextMenuOptions || ['edit', 'delete'];

            settings.dataSource.aggregate = userAggregators || [];
            settings.dataSource.transport = ICMO.core.getTransport($el);
            settings.dataSource.schema = ICMO.core.getSchema(model);
            settings = ICMO.grid.tools.removeInputNumberSpinners(settings);

            $el.kendoGrid(settings);

            var grid = $el.data("kendoGrid");
            var $gridTools = $('#' + $el.attr('data-tools'));


            ICMO.grid.tools.hideEmptyPager(grid);
            ICMO.grid.contextMenu.init($el, contextMenuOptions);
            this.bindTools(grid, $el, $gridTools, finishedCallback);
            if (!ICMO.core.hasChangePermission) {
                ICMO.grid.tools.hideEditTools($el);
            }
        },
        bindTools: function (grid, $el, $gridTools, finishedCallback) {
            /* once the grid has loaded run all the bindings */
            ICMO.grid.tools.bindGridEvents(grid, $el, $gridTools);
            ICMO.grid.tools.bindGridTools(grid, $gridTools);
            ICMO.grid.tools.bindLeavePageWarning($el);
            ICMO.grid.tools.bindKeyPresses($el);
            grid.one("dataBound", function () {
                ICMO.grid.tools.bindGridRowTools($el);
            });
            grid.dataSource.bind('requestStart', function () {
                kendo.ui.progress($el, true);
            });
            grid.dataSource.bind('requestEnd', function () {
                kendo.ui.progress($el, false);
            });
            // handle errors more gracefully
            grid.dataSource.bind('error', function (e) {
                var response = e.xhr.responseJSON;
                if (response === undefined){
                    bootbox.alert("An unknown error has occurred.  Our support team has been notified.  Please try your request again later.");
                } else if (response.non_field_errors === undefined) {
                    Object.keys(response).forEach(function (key, index) {
                        var input_name = key;
                        if(key.indexOf('_actual') > -1 || key.indexOf('_plan') > -1 || key.indexOf('_variance') > -1){
                            input_name +="__amount";
                        }
                        $('input[name="' + input_name + '"]').popover({
                            content: response[key],
                            placement: 'bottom'
                        }).popover('show');
                    });
                } else {
                    bootbox.alert(response.non_field_errors.join("<br>"));
                }
            });
            if (finishedCallback) {
                finishedCallback($el, grid);
            }
        },
        $contextMenuRow: null
    }
}());

ICMO.grid.tools = {
    getGridBy$El: function ($el) {
        var grid = $el.data('kendoGrid') || $el.data('kendoTreeList');
        if (grid === undefined) {
            throw new Error("Could not determine grid!");
        }
        return grid;
    },
    getClosestDataItem: function (grid, $el) {
        var uid = $el.closest('tr').attr('data-uid');
        return grid.dataSource.getByUid(uid);
    },
    hideEmptyPager: function (grid) {
        /* hide the pager if there is only one page */
        if (grid.dataSource.totalPages() <= 1) {
            if (grid.pager !== undefined) {
                grid.pager.element.hide();
            }
        }
    },
    markDirty: function ($el, $gridTools) {
        $el.data("dirty", true);
        $gridTools.find('.grid-save').attr('disabled', false).removeClass("btn-primary").addClass("btn-danger btn-danger-highlight");
        $gridTools.find('.grid-cancel').attr('disabled', false);
    },
    markClean: function ($el, $gridTools) {
        $gridTools.find('.grid-save').attr('disabled', true).removeClass("btn-danger").addClass("btn-primary");
        $gridTools.find('.grid-cancel').attr('disabled', true);
        $('.grid-actions').show();
        $('.grid-save').hide();
        $el.data("dirty", false);
    },
    removeInputNumberSpinners: function (settings) {
        /* Removes the spinners from all number fields */
        var dsfields = settings.dataSource.schema.model.fields;
        var numeric_fields = [];
        for (var key in dsfields) {
            if (dsfields.hasOwnProperty(key) && dsfields[key].type === "number") {
                numeric_fields.push(key)
            }
        }
        for (var i = 0; i < settings.columns.length; i++) {
            if (numeric_fields.indexOf(settings.columns[i].field) > -1) {
                settings.columns[i].editor = this.gridEditNumber
            }
        }
        return settings;
    },
    gridEditNumber: function (container, options) {
        $('<input data-bind="value:' + options.field + '"/>')
            .appendTo(container)
            .kendoNumericTextBox({
                spinners: false
            });
    },
    bindGridEvents: function (grid, $el, $gridTools) {
        var that = this;
        grid.bind("edit", function (e) {
            if (!ICMO.core.hasChangePermission) {
                bootbox.alert('You do not have permission to make changes here.');
                return false;
            }
            that.markDirty($el, $gridTools);
            e.container.find('.grid-save').show();
            e.container.find('.grid-actions').hide();
        });
        grid.bind("cancel", function () {
            that.markClean($el, $gridTools);
        });
        grid.dataSource.bind("sync", function () {
            that.markClean($el, $gridTools);
        });
    },
    bindGridTools: function (grid, $gridTools) {
        grid.element.delegate("tbody>tr", "dblclick", function (e) {
            if (grid.options.editable && !$(e.target).closest('tr').hasClass('k-grid-edit-row')) {
                grid.editRow($(this));
            }
        });
        $gridTools.find('.grid-add').click(function () {
            if (!ICMO.core.hasChangePermission) {
                bootbox.alert('You do not have permission to make changes here.');
                return false;
            }
            grid.addRow();
        });
        $gridTools.find('.grid-excel').click(function () {
            grid.saveAsExcel();
        });
        $gridTools.find('.grid-pdf').click(function () {
            grid.saveAsPDF();
        });
        $gridTools.find('.grid-cancel').click(function () {
            if (grid.cancelChanges !== undefined) {
                grid.cancelChanges();
            } else {
                grid.cancelRow();
            }
            grid.trigger('cancel');
        });
    },
    bindGridRowTools: function ($el) {
        /* when a new row is added we want to bind to that row, and not every other as well */
        $el.on('click', '.grid-actions', function ($el) {
            return function (e) {
                ICMO.grid.contextMenu.set$TargetRow($el, $(e.target).closest('tr'));
                console.log("Opening the CM, with target:");
                console.log(e.target);
                ICMO.grid.contextMenu.getBy$El($el).open(e.target);
            }
        }($el));
        $el.on('click', '.grid-save', function ($el) {
            return function (e) {
                var grid = ICMO.grid.tools.getGridBy$El($el),
                    event = jQuery.Event("preSave");
                $el.trigger(event, [ICMO.grid.tools.getClosestDataItem(grid, $(e.target))]);
                if (!event.isDefaultPrevented()) {
                    /* treelist and grid handle saves slightly differently */
                    if (grid.saveChanges !== undefined) {
                        grid.saveChanges();
                    } else {
                        grid.saveRow();
                    }
                }
            }
        }($el));
    },
    bindKeyPresses: function ($el) {
        $el.bind('keyup', function (e) {
            var code = e.keyCode || e.which,
                grid = ICMO.grid.tools.getGridBy$El($(e.target).closest('.k-grid'));
            if (code == 13) { //"Enter" keycode
                e.preventDefault();
                e.target.blur();  // Datasource only updates on blur

                // Trigger a custom presave event which can block this save
                var event = jQuery.Event("preSave");
                $el.trigger(event, [ICMO.grid.tools.getClosestDataItem(grid, $(e.target))]);
                if (!event.isDefaultPrevented()) {  // If the save isn't blocked...
                    /* treelist and grid handle saves slightly differently */
                    if (grid.saveChanges !== undefined) {
                        grid.saveChanges();
                    } else {
                        grid.saveRow();
                    }
                }
            } else if (code == 27) {  // cancel on escape key
                e.preventDefault();
                if (grid.cancelChanges !== undefined) {
                    grid.cancelChanges();
                } else {
                    grid.cancelRow();
                }
                grid.trigger('cancel');
            }
        });
    },
    bindLeavePageWarning: function ($el) {
        window.addEventListener("beforeunload", function (e) {
            if ($el.data('dirty') === true) {
                var confirmationMessage = 'You have unsaved changes.';
                confirmationMessage += 'If you leave before saving, your changes will be lost.';

                (e || window.event).returnValue = confirmationMessage; //Gecko + IE
                return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
            }
        });
    },
    hideEditTools: function ($el) {
        var grid = $el.data('kendoGrid'),
            lastCol = grid.columns[grid.columns.length - 1],
            $gridTools = $('.' + $el.attr('data-tools'));
        if (lastCol.title == 'Actions') {
            grid.hideColumn(lastCol);
        }
        $gridTools.find('.grid-add').hide();
    }
};

ICMO.grid.contextMenu = {
    targetRowUid: null,
    getId: function ($el) {
        return "context-menu-" + $el.attr('id');
    },
    getBy$El: function ($el) {
        return $("#" + ICMO.grid.contextMenu.getId($el)).data('kendoContextMenu');
    },
    getContainerBy$El: function ($el) {
        return $('#' + this.getId($el));
    },
    get$TargetRowUid: function ($el) {
        return this.targetRowUid;
    },
    set$TargetRowUid: function ($el, uid) {
        this.targetRowUid = uid;
        console.log("setting " + $el.attr('id') + " target-row-uid to " + uid);
    },
    get$TargetRow: function ($el) {
        var uid = this.get$TargetRowUid($el);
        if (!uid) {
            return null;
        }
        return $el.find("tr[data-uid=" + uid + "]");
    },
    set$TargetRow: function ($el, $targetRow) {
        if (!$targetRow) {
            throw new Error("$target is not specified!");
        }
        console.log("Setting target row to:");
        console.log($targetRow);
        /* Note that a row's UID will change after grid save, and jquery caches data() calls, so you
         * would get the old UID not the current one! */
        var uid = $targetRow.attr('data-uid');
        this.set$TargetRowUid($el, uid);
        //$targetRow.addClass('debug-highlight');
        return true;
    },
    clear$TargetRow: function ($el) {
        var $targetRow = this.get$TargetRow($el);
        if ($targetRow) {
            //$targetRow.removeClass('debug-highlight');
        }
        console.log("clearing target row");
        this.targetRowUid = null;
    },
    get$TargetRowDataItem: function ($el) {
        return ICMO.grid.tools.getGridBy$El($el).dataItem(this.get$TargetRow($el));
    },
    defaultActions: {
        edit: {
            label: 'Edit', action: 'edit',
            callback: function ($el, finishedCallback) {
                var grid = ICMO.grid.tools.getGridBy$El($el);
                grid.editRow(ICMO.grid.contextMenu.get$TargetRow($el));
                finishedCallback();
            },
            visible: function ($el) {
                return ICMO.core.hasChangePermission;
            }
        },
        delete: {
            label: 'Delete', action: 'delete',
            callback: function ($el, finishedCallback) {
                var grid = ICMO.grid.tools.getGridBy$El($el);
                var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el);
                bootbox.confirm("Are you sure you want to delete this item?", function (response) {
                    if (response === true) {
                        console.log("attempting to remove: " + ICMO.grid.contextMenu.get$TargetRow($el));
                        grid.removeRow($targetRow);
                    }
                    finishedCallback();
                });
            },
            visible: function ($el) {
                return ICMO.core.hasChangePermission;
            }
        }
    },
    init: function ($el, userOptions) {
        /* build the menu from the options and attach to the body */
        var that = this;
        var option,
            options = userOptions || [],
            $contextMenu = $("<ul class='contextMenu' style='display:none' data-target-row-uid='0' id='" + this.getId($el) + "'></ul>");
        $.each(options, function (idx, user_option) {
            if (typeof user_option === "string") {
                option = that.defaultActions[user_option];
            } else {
                option = $.extend({}, that.defaultActions[user_option.action] || {}, user_option);
            }
            var $li = $("<li data-action='" + option.action + "'>" + option.label + "</li>");
            $contextMenu.append($li);
            $li.click(function ($el, option) {
                return function (e) {
                    if (ICMO.grid.contextMenu.get$TargetRow($el) === null) {
                        return false;
                    }
                    var action = $(e.item).attr('data-action');
                    if (option.visible($el)) {
                        option.callback($el, function () {
                            ICMO.grid.contextMenu.getBy$El($el).close();
                        });
                    }
                }
            }($el, option));
        });
        $('body').append($contextMenu);

        /* initialize the kendo menu */
        $contextMenu.kendoContextMenu({
            orientation: 'vertical',
            filter: "#" + $el.attr('id') + " .grid-actions",
            animation: {
                open: {effects: "fadeIn"},
                duration: 200
            },
            open: function (e) {
                /* This widget is buggy (see github) and cannot be relied upon to
                 work simply supporting both the gear trigger and context menu trigger,
                 so contextmenu trigger is effectively disabled here.
                 */
                if (!ICMO.grid.contextMenu.get$TargetRowUid($el)) {
                    e.preventDefault();
                    return false;
                }
                /* run visible on each option */
                var $container = ICMO.grid.contextMenu.getContainerBy$El($el);
                $.each(options, function (idx, user_option) {
                    if (typeof user_option === "string") {
                        option = that.defaultActions[user_option];
                    } else {
                        option = $.extend({}, that.defaultActions[user_option.action] || {}, user_option);
                    }
                    var $li = $container.find('li[data-action="' + option.action + '"]');
                    if (option.visible($el)) {
                        $li.show();
                    } else {
                        $li.hide();
                    }
                });
                return true;
            },
            close: function (e) {
                ICMO.grid.contextMenu.clear$TargetRow($el);
            }
        });
        return $contextMenu.data('kendoContextMenu');
    }
};