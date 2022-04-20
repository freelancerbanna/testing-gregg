/// <reference path="../Src/Scripts/jquery-1.9.1.min.js" />
/// <reference path="../Src/Scripts/jquery-ui-1.10.3/jquery-ui.min.js" />

// Look & Functionalities implemented based on https://dl.dropboxusercontent.com/u/3406366/gantt-chart.swf

function showDetailedView(ActivityView, gridContentTmpl, chartContentTmpl) {
    var $tableRow = ActivityView.TableRow();
    var $chartRow = ActivityView.ChartRow();
    var $uiGridBody = $tableRow.parents(".ui-grid-body");
    var $uiGridBodyTable = $(".ui-grid-body-table", $uiGridBody);
    var $uiGridPanel = $uiGridBody.parents(".ui-gridpanel");
    var $gantt_container = $uiGridPanel.parents(".radiantq-ui-GanttBase");
    var ganttControl = $gantt_container.data("GanttControl");
    var GanttChart = ganttControl.GetGanttChartInstance();
    var $ganttChart = GanttChart.element;
    var $ganttChartTable = $(".rq-gc-rowsParent-table", $ganttChart);
    var $chartRowsContainer = $(".rq-gc-rowsParent", $ganttChart);
    var hasVertScrollbar = ($uiGridBody[0].scrollHeight > $uiGridBody[0].clientHeight);
    var prevScrollTop = $uiGridBody.scrollTop();
    var prevGridMarginTop = $uiGridBodyTable.css("margin-top");
    var prevChartMarginTop = $ganttChartTable.css("margin-top");

    // To Prevent the Gantt from updating the View on Add, Remove and Scroll.
    ganttControl.PreventDefaultFns = true;

    $uiGridBody.scrollTop(0);
    $uiGridBodyTable[0].style.setProperty("margin-top", "0px", "important");
    $ganttChartTable[0].style.setProperty("margin-top", "0px", "important");

    // Hiding Dependency Lines from View.
    var $dependencyLines = $(".rq-gc-dependencysParent", $ganttChart).css("display", "none");

    // Hiding rows from view.
    var $tableRows = $("tr", $uiGridBody).css("display", "none");
    var $chartRows = $("tr", $chartRowsContainer).css("display", "none");
    $tableRow.css("display", "table-row");
    $chartRow.css("display", "table-row");

    var $gridOverlay = $chartOverlay = $("<div class='overlay-div'></div>");
    var $newTableRow = $("<tr class='custom-detail-row'></tr>");
    var $newTableTD = $("<td style='padding:0px !important'></td>");
    $newTableRow.append($newTableTD);
    var $newChartRow = $("<tr class='custom-detail-row'></tr>");
    var $newChartTD = $("<td style='padding:0px !important'></td>");
    $newChartRow.append($newChartTD);
    var $detailViewGrid = $("<div class='detail-view-grid'></div>");
    var $detailViewChart = $("<div class='detail-view-chart'></div>");
    var $chartContent = $("<div class='content-container'></div>");
    $detailViewChart.append("<div class='tab-switch'><div class='closeBtn'>Close X</div><div id='tab-1' class='tab'></div><div id='tab-2' class='tab'></div></div>");
    $detailViewChart.append($chartContent);

    $newTableTD.append($detailViewGrid);
    $newChartTD.append($detailViewChart);
    var selectedTabId = "tab-1";
    $(".tab", $detailViewChart).click(function () {
        if (this.id != selectedTabId) {
            selectedTabId = this.id;
            onSelectedTabChange(this);
        }
    });

    onSelectedTabChange();
    function onSelectedTabChange() {
        $chartContent.empty();
        if (selectedTabId == "tab-1") {
            var resources = [{ Name: "Resource1" }, { Name: "Resource2" }, { Name: "Resource3" }, { Name: "Resource4" }, { Name: "Resource5" }];
            $detailViewGrid.append($.tmpl(gridContentTmpl, { resources: resources }));
            $chartContent.append($.tmpl(chartContentTmpl, { resources: resources }));
        }
        else {
            // Add the Bar Chart into $chartContent element
            $chartContent.append("<div style='position: absolute; left: 0px;'>TEST</div>");
        }
    }

    //OnLoad
    var height = $uiGridBody.height() - $tableRow.outerHeight(true);
    $detailViewGrid.height(height);
    var width = hasVertScrollbar ? ($ganttChart.width() - 16/*For ScrollBar width*/) : $ganttChart.width();
    var left = GanttChart.HScrollBar.scrollLeft();
    $detailViewChart.css({ "margin-left": left, height: height, width: width });
    $gridOverlay.height($uiGridPanel.height());

    if (hasVertScrollbar) {
        if (GanttChart.options.ShowVerticalScrollBar == true)
            $ganttChart.append($gridOverlay);
        var vertScroll = $uiGridBody.css("overflow-y") != "hidden";
        if (vertScroll) {
            $chartOverlay = $gridOverlay.clone();
            $uiGridPanel.append($chartOverlay);
        }
    }

    GanttChart.BeforeChartHZScroll.subscribe(beforeChartHZScroll);
    function beforeChartHZScroll(sender, args) {
        $detailViewChart.css("margin-left", args.newValue);
    }

    var layoutElement = $gantt_container.children();
    layoutElement.bind("layout.onresize", function () {
        var width = hasVertScrollbar ? ($ganttChart.width() - 16/*For ScrollBar width*/) : $ganttChart.width();
        $detailViewChart.width(width);
    });

    $(".closeBtn", $detailViewChart).click(function () {
        $uiGridBody.scrollTop(prevScrollTop);
        $uiGridBodyTable[0].style.setProperty("margin-top", prevGridMarginTop, "important");
        $ganttChartTable[0].style.setProperty("margin-top", prevChartMarginTop, "important");

        ganttControl.PreventDefaultFns = false;

        GanttChart.BeforeChartHZScroll.unsubscribe(beforeChartHZScroll);
        layoutElement.unbind("layout.onresize");

        $gridOverlay.remove();
        $chartOverlay.remove();
        $newTableRow.remove();
        $newChartRow.remove();
        $tableRows.css("display", "table-row");
        $chartRows.css("display", "table-row");
        $dependencyLines.css("display", "block");
    });

    $newTableRow.insertAfter($tableRow);
    $newChartRow.insertAfter($chartRow);
}