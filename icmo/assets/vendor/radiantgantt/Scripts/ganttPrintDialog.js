/// <reference path="../Src/Scripts/jquery-1.11.2.min.js" />
/// <reference path="../Src/Scripts/jquery-ui-1.11.2/jquery-ui.min.js" />

$.widget("radiantq.ganttPrintDialog", {
    options: {

    },
    _create: function () {
        this.element.dialog(this.options);
        var dialog = this.element.data("uiDialog");
        dialog.uiDialogTitlebarClose.click(function (event) {
            $(window).unbind("resize.printDialog", this._adjustTheOverlay);
        });
    },
    open: function (ganttWidget) {
        this.element.dialog("open");

        var $contDiv = $("<div></div>");
        var $ths = $("th", ganttWidget.GetGanttTable().uiGridHeadTable);
        $contDiv.append("<div>Header/Title of page:&nbsp;<input id='customTitle' type='text' value='" + document.title + "' /></div><br />");

        var $options = $("<div><b>Select the column headers to print:</b><br/></div>")
        $ths.each(function (key, val) {
            var $opt = $('<input type="checkbox" class="headCol" value="' + key + '" checked="checked"/><span> ' + $(val).text() + '</span><br />');
            $options.append($opt);
        });
        $contDiv.append($options);

        var $viewStartPicker = $('<input type="text" id="viewStartPicker" />');
        var $viewEndPicker = $('<input type="text" id="viewEndPicker" />');
        var $datePicks = $("<br/><div><span>View StartTime <sub> (optional)</sub>&nbsp;: </span></div>");

        $viewStartPicker.datepicker({
             onClose: function (e) {
                }
        });

        $viewEndPicker.datepicker().change(function () {
            var d = new Date(this.value);
            if (d == "Invalid Date")
                this.value = "Invalid Date";
        });

        $datePicks.append($viewStartPicker);
        $datePicks.append("<br/><span> View EndTime <sub> (optional)</sub>&nbsp;:&nbsp;&nbsp;</span>");
        $datePicks.append($viewEndPicker);

        $contDiv.append($datePicks);
        this.element.empty().append($contDiv);
        this._adjustTheOverlay();

        $(window).bind("resize.printDialog", this._adjustTheOverlay);
    },
    getSelectedOptions: function () {
        var options = {};
        options.Title = $("#customTitle", this.element).val();
        var $select = $("input.headCol:checked", this.element);
        if ($select.length != 0) {
            options.VisibleColumnIndices = [];
            for (var i = 0; i < $select.length; i++) {
                options.VisibleColumnIndices.push($select[i].value);
            }
        }
        else
            options.IsGridVisible = false;

        options.ViewStartTime = $("#viewStartPicker", this.element).datepicker("getDate");
        options.ViewEndTime = $("#viewEndPicker", this.element).datepicker("getDate");
        return options;
    },
    _adjustTheOverlay: function () {
        var docBody = document.body;
        $(".ui-widget-overlay").css({ 'height': docBody.scrollHeight || docBody.clientHeight, 'width': docBody.scrollWidth || docBody.clientWidth, "z-index": 3 });
    },
    close: function () {
        $(window).unbind("resize.printDialog", this._adjustTheOverlay);
        this.element.dialog("close");
    }
});