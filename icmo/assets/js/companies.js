var ICMO = ICMO || {};
ICMO.apps = ICMO.apps || {};
ICMO.models = ICMO.models || {};
ICMO.apps.companies = {};

ICMO.apps.companies.yourCompanies = (function () {
    var getFiscalYearStartMonthEditor = function (container, options) {
            var $select = $('<select/>'),
                $option;
            $select.attr('name', 'fiscal_year_start');
            $.each(ICMO.core.monthNames, function (idx, month) {
                    $option = $('<option/>');
                $option.attr('value', idx + 1);
                $option.html(month);
                $select.append($option);
            });
            $select.val(parseInt(options.model.fiscal_year_start));
            container.append($select);
        },
        getLogoEditor = function (container, options) {
            var html = $("#logoEditor").html();
            container.append(html);
            var $logoEditor = $('.logo-editor'),
                $img = $logoEditor.find('img'),
                $imgContainer = $logoEditor.find('.logo-container'),
                $fileInput = $logoEditor.find('input[type="file"]'),
                $progressBar = $logoEditor.find('.progress-bar'),
                $logoInput = $logoEditor.find('input[name="logo"]');

            $fileInput.hide();
            // Create the thumbnail
            if (options.model.logo) {
                $img.attr('src', options.model.logo_thumbnail);
            } else {
                $img.attr('src', $imgContainer.data('no-logo-url'));
            }
            $imgContainer.click(function (e) {
                $fileInput.trigger('click');
            });

            // initialize Cloudinary File Upload
            $fileInput.unsigned_cloudinary_upload("vwv7hlpe",
                {cloud_name: 'hwuwmbjeo', tags: 'company_logos'},
                {multiple: false}
            ).bind('cloudinarydone', function (e, data) {
                    var r = data.result;
                    $img.attr('src', $.cloudinary.url(r.public_id,
                        {format: 'jpg', height: 40, crop: 'thumb'}
                    ));
                    $logoInput.val(r.resource_type + "/" + r.type + "/" + r.path).change();
                    $progressBar.hide();
                    $progressBar.css('width', 0);
                }
            ).bind('cloudinaryprogress', function (e, data) {
                    $progressBar.show();
                    $progressBar.css('width',
                        Math.round((data.loaded * 100.0) / data.total) + '%');

                });
        },
        getLogoDisplay = function (dataItem) {
            if (dataItem.logo_thumbnail) {
                return "<img src='" + dataItem.logo_thumbnail + "' height=40/>";
            } else {
                return "No logo";
            }
        },
        defaults = {
            columns: [
                {field: 'slug', hidden: true},
                {
                    field: 'name',
                    title: 'Name',
                    template: '<a href="#:url#"><b>#: name #</b></a>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'fiscal_year_start',
                    title: 'Fiscal Year Start Month',
                    template: '#: fiscal_year_start_full_name#',
                    editor: getFiscalYearStartMonthEditor
                },
                {field: 'logo', title: 'Logo', template: getLogoDisplay, editor: getLogoEditor},
                {field: 'modified', title: 'Modified', format: "{0:g}"},
                {field: 'modified_by_name', title: 'Modified By'},
                {field: 'created', title: 'Created', format: "{0:g}"},
                {
                    field: '', title: 'Actions',
                    template: function (model) {
                        return kendo.template($('#rowTools').html())(model)
                    }
                }
            ]
        },

        addCompany = function ($el, grid) {
            var max_companies = $el.data('max-companies');
            console.log(max_companies);
            if (grid.dataSource.data().length >= max_companies) {
                bootbox.alert("You have reached your company limit.  To add more companies please upgrade your account.");
            } else {
                grid.addRow();
            }
        };
    return {
        createCompanyGrid: function ($el, userOptions, userContextMenuOptions, selectedCompanySlug) {
            var contextMenuOptions = userContextMenuOptions || ['edit', 'delete'],
                settings = $.extend({}, defaults, userOptions || {});

            ICMO.grid.create($el, ICMO.models.Company, settings, null, contextMenuOptions);
            var grid = $el.data("kendoGrid");
            var $gridTools = $("." + $el.data('tools'));
            grid.bind('dataBound', function () {
                $.each(grid.dataSource.data(), function (idx, dataItem) {
                    if (dataItem.slug == selectedCompanySlug) {
                        $('tr[data-uid="' + dataItem.uid + '"]').addClass("selected-plan")
                    }
                });
            });
            $gridTools.find('.grid-add').unbind('click');
            $gridTools.find('.grid-add').bind('click', function () {
                addCompany($el, grid);
            });
        }
    }
}());


ICMO.apps.companies.sharedCompanies = (function () {
    var defaults = {
            columns: [
                {field: 'slug', hidden: true},
                {
                    field: 'name',
                    title: 'Name',
                    template: '<a href="#:url#"><b>#: name #</b></a>',
                    attributes: {
                        style: "border-right: 1px solid rgb(219,219,219) !important;"
                    }
                },
                {
                    field: 'fiscal_year_start',
                    title: 'Fiscal Year Start Month',
                    template: '#: fiscal_year_start_full_name#',
                }
            ]
        };
    return {
        createCompanyGrid: function ($el, userOptions, userContextMenuOptions, selectedCompanySlug) {
            var contextMenuOptions = userContextMenuOptions || ['edit', 'delete'],
                settings = $.extend({}, defaults, userOptions || {});

            ICMO.grid.create($el, ICMO.models.Company, settings, null, contextMenuOptions);
            var grid = $el.data("kendoGrid");
            grid.bind('dataBound', function () {
                $.each(grid.dataSource.data(), function (idx, dataItem) {
                    if (dataItem.slug == selectedCompanySlug) {
                        $('tr[data-uid="' + dataItem.uid + '"]').addClass("selected-plan")
                    }
                });
            });
        }
    }
}());

ICMO.models.Company = kendo.data.Model.define({
    fields: {
        created: {
            type: "date",
            editable: false
        },
        is_published: {type: "boolean"},
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
        fiscal_year_start: {
            required: true,
            type: "string",
            validation: {
                required: true
            },
            defaultValue: 1
        },
        fiscal_year_start_full_name: {
            type: "string",
            editable: false,
        },
        name: {
            required: true,
            type: "string",
            validation: {
                required: true
            }
        },
        slug: {
            type: "string",
            editable: false
        },
        logo: {
            type: "string",
            required: false
        },
        logo_thumbnail: {
            type: "string",
            editable: false
        }
    },
    idField: "slug",
    id: "slug"
});
