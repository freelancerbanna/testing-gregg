var ICMO = ICMO || {};
ICMO.tree = (function () {
    var bindTreeTools = function (grid, $el, $gridTools) {
            $gridTools.find('.grid-expand').bind('click', function () {
                var grid = $el.data('kendoTreeList');
                $.each(grid.dataSource.data(), function (idx, data) {
                    grid.expand($el.find("tr[data-uid=" + data.uid + "]"));
                })
            });
            $gridTools.find('.grid-collapse').bind('click', function () {
                var grid = $el.data('kendoTreeList');
                $.each(grid.dataSource.data(), function (idx, data) {
                    grid.collapse($el.find("tr[data-uid=" + data.uid + "]"));
                })
            });
            grid.bind('expand', function (e) {
                storeCollapseState(e.model, true);
            });
            grid.bind('collapse', function (e) {
                storeCollapseState(e.model, false);
            });
        },
        bindDragnDrop = function (grid, $el, dndTestFunc) {
            grid.bind('drop', function (e) {
                if (dndTestFunc) {
                    var response = dndTestFunc(grid, e.source, e.destination);
                    if (!response.allowed) {
                        if (response.msg) {
                            bootbox.alert(response.msg);
                            e.setValid(false);
                        }
                    }
                }
            });
            grid.dataSource.bind("change", function (e) {
                /* enable drag and drop */
                if (e.action === "itemchange" && e.field === "parentId") {
                    console.log("item has changed parentId");
                    var moved_item = e.items[0];
                    var destination_item = grid.dataSource.get(moved_item.parentId);
                    if (destination_item === undefined) {
                        /* this is coming from a delete row request or a move out */
                        console.log("No target, so this is not a drag and drop action.");
                        grid.dataSource.sync();
                        return;
                    }

                    if (destination_item.item_type !== 'category') {
                        console.log("Target is not a category, this is a reorder action.");
                        //moved_item.set('weight', destination_item.weight - 1);
                        var original_order = moved_item.order;
                        moved_item.set('parentId', destination_item.parentId);
                        moved_item.set('reorder_target', destination_item.slug);
                        var newOrder = 0;
                        $.each(grid.dataSource.data(), function (idx, dataItem) {
                            if (dataItem.order > newOrder && dataItem.order < destination_item.order) {
                                newOrder = dataItem.order;
                            }
                        });
                        reOrderItem($el, moved_item, original_order, newOrder);

                    } else {
                        console.log('legit move');
                        grid.expand(grid.content.find("tr[data-uid=" + destination_item.uid + "]"));
                        grid.dataSource.sync();
                    }
                }
            });
        },
    /* this code duplicates the server side ordering mechanism.
     Silly yes, but the only way I could figure out how to do this without
     refreshing the entire screen each time something is reordered.
     Fixme See if this code can be replaced now that we can save and restore collapse state
     */
        reOrderItem = function ($el, movedItem, original_order, new_order) {
            if (original_order == new_order) {
                return;
            }
            console.log('redordering ' + movedItem.slug + ' from ' + original_order + ' to ' + new_order);
            $.each($el.data('kendoTreeList').dataSource.data(), function (idx, data) {
                if (original_order > new_order) {
                    if (data.order < original_order && data.order >= new_order) {
                        console.log('changing order of ' + data.slug + ' from ' + data.order + ' to ' + (data.order + 1));
                        data.set('order', data.order + 1);
                        data.order = data.order + 1;
                    }
                } else {
                    if (data.order > original_order && data.order <= new_order) {
                        console.log('changing order of ' + data.slug + ' from ' + data.order + ' to ' + (data.order - 1));
                        data.set('order', data.order - 1);
                        data.order = data.order - 1;
                    }
                }
            });
            movedItem.order = new_order;
            $el.data('kendoTreeList').dataSource.sync();
        },
        moveTargetRowUpALevel = function ($el, finishedCallback) {
            console.log("attempting to move the target up a level");
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoTreeList'),
                dataItem = grid.dataItem($targetRow);
            if (!dataItem.parentId) {
                console.log("this is already a root level item");
                return;
            }
            var parent = grid.dataSource.get(dataItem.parentId);
            dataItem.set('parentId', parent.parentId);
            grid.dataSource.sync();
            finishedCallback();
        },
    /*
     Removing rows requires that we set the parent of all children to the parent
     of the row to be removed, so that the children do not become orphaned.
     */
        removeTargetRow = function ($el, finishedCallback) {
            var $targetRow = ICMO.grid.contextMenu.get$TargetRow($el),
                grid = $el.data('kendoTreeList'),
                toBeDeletedItem = grid.dataItem($targetRow),
                data = grid.dataSource.data();
            console.log("attempting to remove: " + ICMO.grid.contextMenu.get$TargetRow($el));
            bootbox.confirm("Are you sure you want to delete this item?", function (response) {
                if (response === true) {
                    for (var i = 0; i < data.length; i++) {
                        if (data[i].parentId === toBeDeletedItem.slug) {
                            console.log('moving ' + data[i].slug + ' to ' + toBeDeletedItem.parentId);
                            data[i].set('parentId', toBeDeletedItem.parentId);
                        }
                    }
                    grid.removeRow($targetRow);
                }
                finishedCallback();
            });
        },
    /*
     The dataSource.read operation resets the collapse state,
     so it needs to be preserved and restored
     */
        collapseStates = {},
        storeCollapseState = function (dataItem, expanded) {
            collapseStates[dataItem.slug] = expanded;
        },
        restoreCollapseStates = function (grid) {
            $.each(grid.dataSource.data(), function (idx, dataItem) {
                if (collapseStates[dataItem.slug] !== undefined) {
                    grid.expand('tr[data-uid="' + dataItem.uid + '"]');
                }
            });
        },
        hideEditTools = function ($el) {
            var grid = $el.data('kendoTreeList'),
                lastCol = grid.columns[grid.columns.length - 1],
                $gridTools = $('.' + $el.attr('data-tools'));
            if (lastCol.title == 'Actions') {
                grid.hideColumn(lastCol);
            }
            $gridTools.find('.tree-add').hide();
        };
    return {
        create: function ($el, model, userGridSettings, userOptions) {
            var optionDefaults = {
                    aggregators: [],
                    contextMenuOptions: ['edit'],
                    dndTestFunc: null,
                    moveOutTestFunc: null,
                    deleteTestFunc: null
                },
                options = $.extend({}, optionDefaults, userOptions || {}),
                gridDefaults = {
                    dataSource: {
                        autoSync: false,
                        sort: {field: 'order', dir: 'asc'},
                        transport: ICMO.core.getTransport($el),
                        aggregate: options.aggregators,
                        schema: ICMO.core.getSchema(model)
                    },
                    editable: {
                        mode: 'inline',
                        move: true
                    },
                    resizable: true
                },
                gridSettings = $.extend({}, gridDefaults, userGridSettings || {});

            $el.kendoTreeList(gridSettings);

            var grid = $el.data('kendoTreeList');
            var $gridTools = $('#' + $el.attr('data-tools'));

            /* once the grid has loaded run all the bindings */
            ICMO.grid.bindTools(grid, $el, $gridTools);
            bindTreeTools(grid, $el, $gridTools);

            options.contextMenuOptions.push(
                {
                    label: 'Move Out', action: 'move-out',
                    callback: moveTargetRowUpALevel,
                    visible: function ($el) {
                        var item = ICMO.grid.contextMenu.get$TargetRowDataItem($el);
                        if (item.parentId === "") {
                            return false;
                        }
                        if (options.moveOutTestFunc) {
                            if (!options.moveOutTestFunc(item)) {
                                return false;
                            }
                        }
                        return true;
                    }
                },
                {
                    label: 'Delete', action: 'delete',
                    callback: removeTargetRow,
                    visible: function ($el) {
                        var item = ICMO.grid.contextMenu.get$TargetRowDataItem($el);
                        if (options.deleteTestFunc) {
                            if (!options.deleteTestFunc(item)) {
                                return false;
                            }
                        }
                        return true;
                    }
                }
            );
            ICMO.grid.contextMenu.init($el, options.contextMenuOptions);

            grid.bind("dataBound", function () {
                $.each($el.find('tbody tr'), function (idx, row) {
                    if ($(row).attr('role') != 'row') {
                        /* skip footer, etc */
                        return;
                    }
                    var dataItem = $el.data('kendoTreeList').dataItem(row);
                    $(row).attr('data-item-type', dataItem.item_type);
                });
            });
            bindDragnDrop(grid, $el, options.dndTestFunc);

            grid.dataSource.bind('sync', function () {
                grid.dataSource.read().done(function () {
                    var scrollPosition = $('body').scrollTop();
                    restoreCollapseStates(grid);
                    $('body').scrollTop(scrollPosition);
                });
            });

            if (!ICMO.core.hasChangePermission) {
                hideEditTools($el);
            }
            return grid;
        }
    }
})();