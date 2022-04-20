(function () {

    function FGDependencyHandler() {
        // To resolve the dependency info from data source.
        this._taskByID = new RadiantQ.Gantt.Dictionary();
        this._partiallyLoadDepByID = new RadiantQ.Gantt.Dictionary();
        this.depsByID = new RadiantQ.Gantt.Dictionary();
        this.depLinesList = new RadiantQ.RQ_CollectionChangeNotifier();
    }
    FGDependencyHandler.prototype.resolveDependencyInfo = function (data, idProperty, predecessorProperty) {
        var id = data[idProperty];
        var predecessor = data[predecessorProperty];
        if (this._taskByID[id] == undefined)
            this._taskByID.Add(id, data);

        RadiantQ.Gantt.Utils.InsertPropertyChangedTriggeringProperty(data, [predecessorProperty], true);
        data.PropertyChanged.subscribe(onPropertyChanged, this);

        function onPropertyChanged(data, args) {
            if (args.PropertyName == predecessorProperty) {
                this.updateDependencies(data, idProperty, predecessorProperty);
            }
        }
        // Check for dependency created by partial info for this task.
        if (this._partiallyLoadDepByID[id]) {
            var dep = this._partiallyLoadDepByID[id];
            dep.StartTask_M(data);
            this._partiallyLoadDepByID.Remove(id);
        }

        // Check for this task is depended on any other task.
        if (predecessor) {
            var predIds = predecessor.split(",");
            for (var i = 0; i < predIds.length; i++) {
                var predId = predIds[i];
                var depTypeStr = predId.match("FS|SF|FF|SS");
                if (depTypeStr) {
                    depTypeStr = depTypeStr[0];
                    predId = predId.split(depTypeStr)[0];
                }
                else
                    depTypeStr = "";

                var depType = FGDependencyHandler.GetDependencyType(depTypeStr);


                var fromData = this._taskByID[predId] || null;
                var dep = new DependencyInfo(fromData, idProperty, data, idProperty, depType);

                if (fromData == null) {
                    dep.StartID = predId;
                    this._partiallyLoadDepByID.Add(predId, dep);
                }
                this.depLinesList.push(dep);

                if (this.depsByID[id])
                    this.depsByID[id].push(dep);
                else
                    this.depsByID[id] = [dep];
            }
        }
    }
    FGDependencyHandler.GetDependencyType = function (typeStr) {
        switch (typeStr.toUpperCase()) {
            case "SS":
                return RadiantQ.Gantt.DependencyType.StartToStart;
            case "SF":
                return RadiantQ.Gantt.DependencyType.StartToFinish;
            case "FF":
                return RadiantQ.Gantt.DependencyType.FinishToFinish;
            case "FS":
            default:
                return RadiantQ.Gantt.DependencyType.FinishToStart;

        }
    }

    FGDependencyHandler.prototype.updateDependencies = function (data, idProperty, predecessorProperty) {
        var id = data[idProperty];
        if (this.depsByID[id]) {
            var deps = this.depsByID[id];
            for (var i = 0; i < deps.length; i++) {
                var dep = deps[i];
                var index = this.depLinesList.indexOf(dep);
                if (index != -1)
                    this.depLinesList.remove(index, 1);
            }
        }

        this.resolveDependencyInfo(data, idProperty, predecessorProperty);
    }


    function DependencyInfo(startTask, startTaskIdProperty, endTask, endTaskIdProperty, dependencyType) {
        this._startTask = startTask;
        this._endTask = endTask;
        this._dependencyType = dependencyType;
        this._startTaskIdProperty = startTaskIdProperty;
        this._endTaskIdProperty = endTaskIdProperty;
        if (startTask)
            this.StartID = startTask[this._startTaskIdProperty];
        if (endTask)
            this.EndID = endTask[this._endTaskIdProperty];
        this.PropertyChanged = new ObjectEvent("PropertyChanged");
    }

    if (RadiantQ.CanUseDefineProperty) {
        Object.defineProperty(DependencyInfo.prototype, "StartTask", {
            get: function () {
                return this._startTask;
            },
            set: function (value) {
                this._startTask = value;
                if (value)
                    this.StartID = value[this._startTaskIdProperty];
                this.PropertyChanged.raise(this, { PropertyName: "StartTask", Value: value });
            }
        });
        Object.defineProperty(DependencyInfo.prototype, "EndTask", {
            get: function () {
                return this._endTask;
            },
            set: function (value) {
                this._endTask = value;
                if (value)
                    this.EndID = value[this._endTaskIdProperty];
                this.PropertyChanged.raise(this, { PropertyName: "EndTask", Value: value });
            }
        });
        Object.defineProperty(DependencyInfo.prototype, "DependencyType", {
            get: function () {
                return this._dependencyType;
            },
            set: function (value) {
                this._dependencyType = value;
                this.PropertyChanged.raise(this, { PropertyName: "DependencyType", Value: value });
            }
        });
    }
    DependencyInfo.prototype.StartTask_M = function (value) {
        if (arguments.length == 0) {
            return this._startTask;
        }
        else {
            this._startTask = value;
            this.PropertyChanged.raise(this, { PropertyName: "StartTask", value: value });
        }
    }
    DependencyInfo.prototype.EndTask_M = function (value) {
        if (arguments.length == 0) {
            return this._endTask;
        }
        else {
            this._endTask = value;
            this.PropertyChanged.raise(this, { PropertyName: "EndTask", value: value });
        }
    }
    DependencyInfo.prototype.DependencyType_M = function (value) {
        if (arguments.length == 0) {
            return this._dependencyType;
        }
        else {
            this._dependencyType = value;
            this.PropertyChanged.raise(this, { PropertyName: "DependencyType", value: value });
        }
    }

    window.FGDependencyHandler = FGDependencyHandler;
    window.DependencyInfo = DependencyInfo;
})();