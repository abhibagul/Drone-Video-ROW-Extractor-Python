{
  function myScript(thisObj) {
    function myScript_buildUI(thisObj) {
      var myPanel =
        thisObj instanceof Panel
          ? thisObj
          : new Window("palette", "ROW Plotter by Abhishek Bagul", undefined, {
              resizeable: true,
              closeButton: false,
            });

      //Panel Structure
      res =
        "group{orientation:'column',\
                        alignment: ['fill','top'],\
                        groupOne: Group{orientation:'row',\
                        selectCompText: StaticText{text:'ROW Plotter by Abhishek Bagul',alignment: ['fill','top']},\
               },\
               groupLink: Group{orientation:'row',\
                        selectCompText: StaticText{text:'https://github.com/abhibagul/ROW-Drone-Extractor-and-Plotter-After-Effects',alignment: ['fill','top']},\
               },\
               groupSelectComp: Panel{orientation:'row',\
                        alignment: ['fill','top'],\
                        selectCompText: StaticText{text:'Composition',alignment: ['fill','top']},\
                        selectCompDropDown: DropDownList{alignment: ['fill','top']},\
               },\
                groupSelectJSON: Panel{orientation:'row',\
                        alignment: ['fill','top'],\
                        selectJsonText: StaticText{text:'JSON file',alignment: ['fill','top']},\
                        selectJsonDropDown: DropDownList{alignment: ['fill','top'], enabled: false},\
               },\
               groupProgress: Group{orientation:'row',\
                       alignment: ['fill','top'],\
                       progressBar: Progressbar{alignment: ['fill','top'], enabled: true},\
               },\
               groupThree: Group{orientation:'row',\
                       alignment: ['fill','top'],\
                       applyButton: Button{text:'Apply',alignment: ['fill','top'], enabled: false},\
                       refButton: Button{text:'Refresh',alignment: ['fill','top']},\
               },\
         }";

      // Adding the ui
      myPanel.grp = myPanel.add(res);

      /**
       * Creates shape and applies the keyframes
       * from JSON file
       */
      myPanel.grp.groupThree.applyButton.onClick = function () {
        //grab the comp and json again!

        //disable
        myPanel.grp.groupThree.applyButton.enabled = false;
        myPanel.grp.groupThree.refButton.enabled = false;

        var ActElem = myPanel.grp.groupSelectComp.selectCompDropDown.selection;

        //get slected composition
        var myComp;
        for (var k = 1; k <= app.project.numItems; k++) {
          var CompName = app.project.item(k).name;
          if (
            app.project.item(k) instanceof CompItem &&
            CompName.toString() === ActElem.toString()
          ) {
            myComp = app.project.item(k);
            break;
          }
        }

        //FPS
        var FPS = 1 / myComp.frameDuration;

        //get selected JSON
        var myJson;
        var ActJson = myPanel.grp.groupSelectJSON.selectJsonDropDown.selection;
        for (var j = 1; j <= myComp.numLayers; j++) {
          var lname = myComp.layer(j).name;
          var jname = ActJson.toString();
          if (lname.toString() === jname) {
            myJson = myComp.layer(j);
            break;
          }
        }

        //lets try to read values of json!
        var LeftLine = myComp.layers.addShape();
        LeftLine.name = "ROW [Left]";

        var RightLine = myComp.layers.addShape();
        RightLine.name = "ROW [Right]";

        var CenterLine = myComp.layers.addShape();
        CenterLine.name = "CenterLine";

        //LEFT
        LeftLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Shape - Group"
        );
        LeftLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Graphic - Stroke"
        );

        //RIGHT
        RightLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Shape - Group"
        );
        RightLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Graphic - Stroke"
        );

        //CENTER
        CenterLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Shape - Group"
        );
        CenterLine.property("ADBE Root Vectors Group").addProperty(
          "ADBE Vector Graphic - Stroke"
        );

        // LEFT CORDS
        lx1 = myJson
          .property("Data")
          .property(1)
          .property(1)
          .property(1)
          .property(1)
          .property(1).value;
        ly1 = myJson
          .property("Data")
          .property(1)
          .property(1)
          .property(1)
          .property(1)
          .property(2).value;
        lx2 = myJson
          .property("Data")
          .property(1)
          .property(1)
          .property(1)
          .property(1)
          .property(3).value;
        ly2 = myJson
          .property("Data")
          .property(1)
          .property(1)
          .property(1)
          .property(1)
          .property(4).value;

        // CENTER CORDS
        cx1 = myJson
          .property("Data")
          .property(1)
          .property(3)
          .property(1)
          .property(1)
          .property(1)
          .property(1).value;
        cy1 = myJson
          .property("Data")
          .property(1)
          .property(3)
          .property(1)
          .property(1)
          .property(1)
          .property(2).value;
        cx2 = myJson
          .property("Data")
          .property(1)
          .property(3)
          .property(1)
          .property(1)
          .property(1)
          .property(3).value;
        cy2 = myJson
          .property("Data")
          .property(1)
          .property(3)
          .property(1)
          .property(1)
          .property(1)
          .property(4).value;

        // RIGHT CORDS
        rx1 = myJson
          .property("Data")
          .property(1)
          .property(2)
          .property(1)
          .property(1)
          .property(1).value;
        ry1 = myJson
          .property("Data")
          .property(1)
          .property(2)
          .property(1)
          .property(1)
          .property(2).value;
        rx2 = myJson
          .property("Data")
          .property(1)
          .property(2)
          .property(1)
          .property(1)
          .property(3).value;
        ry2 = myJson
          .property("Data")
          .property(1)
          .property(2)
          .property(1)
          .property(1)
          .property(4).value;

        //Left Line
        var myShape = new Shape();
        myShape.vertices = [
          [lx1, ly1],
          [lx2, ly2],
        ];
        myShape.closed = false;
        LeftLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Shape - Group")
          .property("ADBE Vector Shape")
          .setValue(myShape);
        LeftLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Graphic - Stroke")
          .property("Stroke Width")
          .setValue(10);

        //Right Line
        var myShape2 = new Shape();
        myShape2.vertices = [
          [rx1, ry1],
          [rx2, ry2],
        ];
        myShape2.closed = false;
        RightLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Shape - Group")
          .property("ADBE Vector Shape")
          .setValue(myShape2);
        RightLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Graphic - Stroke")
          .property("Stroke Width")
          .setValue(10);

        //CENTER LINE
        var myShape3 = new Shape();
        myShape3.vertices = [
          [cx1, cy1],
          [cx2, cy2],
        ];
        myShape3.closed = false;
        CenterLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Shape - Group")
          .property("ADBE Vector Shape")
          .setValue(myShape3);
        CenterLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Graphic - Stroke")
          .property("Stroke Width")
          .setValue(10);

        //set on zero
        LeftLine.property("Transform").property("Position").setValue([0, 0]);
        RightLine.property("Transform").property("Position").setValue([0, 0]);
        CenterLine.property("Transform").property("Position").setValue([0, 0]);

        // Set yellow color for ROW
        LeftLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Graphic - Stroke")
          .property("ADBE Vector Stroke Color")
          .setValue([1, 0.91, 0]);
        RightLine.property("ADBE Root Vectors Group")
          .property("ADBE Vector Graphic - Stroke")
          .property("ADBE Vector Stroke Color")
          .setValue([1, 0.91, 0]);

        //SET progress bar to 0
        myPanel.grp.groupProgress.progressBar.value = 0;

        //Get the number of keyframes needed to be added
        var propsL = myJson
          .property("Data")
          .property(1)
          .property(1).numProperties;
        var countSt = 1;

        //$.writeln(LeftLine.index);
        //property("ADBE Root Vectors Group").property("ADBE Vector Shape - Group").property("ADBE Vector Shape")
        //recProps(myPanel,countSt,props,myJson,LeftLine.index,RightLine.index,CenterLine.index, myPanel.grp.groupProgress.progressBar, FPS,myComp)

        for (var countSt = 1; countSt < propsL; countSt++) {
          //$.writeln("starting " + countSt + " which is less then " + propsL);
          //$.writeln(rComp);
          var time = countSt / FPS;

          //left
          applyKeyframes(countSt, LeftLine.index, time, myComp, 1, myJson);

          //right
          applyKeyframes(countSt, RightLine.index, time, myComp, 2, myJson);

          //center
          applyKeyframes(countSt, CenterLine.index, time, myComp, 3, myJson);

          // Progressbar progress update
          var progress = (countSt / propsL) * 100;

          myPanel.grp.groupProgress.progressBar.value = progress;

          if (countSt % 100 == 0) {
            $.sleep(2000);
          }
        }
      };

      /**
       * Lists all the json files inside
       *  the composition.
       */
      myPanel.grp.groupSelectComp.selectCompDropDown.onChange = function () {
        // Disable json dropdown and apply button
        myPanel.grp.groupSelectJSON.selectJsonDropDown.enabled = false;
        myPanel.grp.groupThree.applyButton.enabled = false;

        //empty json dropdown
        myPanel.grp.groupSelectJSON.selectJsonDropDown.removeAll();

        // User comp selection
        var ActElem = myPanel.grp.groupSelectComp.selectCompDropDown.selection;

        //Loop through all to find the comp
        var myComp;
        for (var k = 1; k <= app.project.numItems; k++) {
          var CompName = app.project.item(k).name;
          if (
            app.project.item(k) instanceof CompItem &&
            CompName.toString() === ActElem.toString()
          ) {
            myComp = app.project.item(k);
            break;
          }
        }

        //List all the json inside the selected comp.
        var JsonItem = [];
        for (var j = 1; j <= myComp.numLayers; j++) {
          if (myComp.layer(j).name.indexOf(".json") > 0) {
            JsonItem.push(myComp.layer(j).name);
          }
        }

        // Return if the JSON dosent exist in the comp file.
        if (JsonItem.length < 1) {
          alert("This composition do not have a valid JSON file.");
          return;
        }

        //Everything went well, enable furter actions.
        myPanel.grp.groupSelectJSON.selectJsonDropDown.enabled = true;
        myPanel.grp.groupThree.applyButton.enabled = true;

        //Add the JSON files to the list
        populateDropDown(
          myPanel.grp.groupSelectJSON.selectJsonDropDown,
          JsonItem
        );
      };

      /**
       * Adds all the compositions to the
       * composition dropdown.
       */
      myPanel.grp.groupThree.refButton.onClick = function () {
        var arrItem = [];
        for (var i = 1; i <= app.project.numItems; i++) {
          if (app.project.item(i) instanceof CompItem) {
            arrItem.push(app.project.item(i).name);
          }
        }

        // Fallback, if the project is empty warn user and stop.
        if (arrItem.length < 1) {
          alert("Project is empty and do not have compositons.");
          return;
        }

        // Add the Compositions to the list
        populateDropDown(
          myPanel.grp.groupSelectComp.selectCompDropDown,
          arrItem
        );
      };

      /**
       * Panel resize function
       */
      myPanel.onResizing = myPanelonResize = function () {
        this.layout.resize();
      };

      myPanel.layout.layout(true);
      return myPanel;
    }

    var myScriptPal = myScript_buildUI(thisObj);

    if (myScriptPal != null && myScriptPal instanceof Window) {
      myScriptPal.center();
      myScriptPal.show();
    }
  }
  myScript(this);
}

/**
 * Adds items to the dropdown
 * @param {dropdown element} dr
 * @param {Array of items to be added to dropdown} items
 */
function populateDropDown(dr, items) {
  //Remove all existing items
  dr.removeAll();
  for (var i = 0; i < items.length; i++) {
    dr.add("item", items[i]);
  }
  //Show 1st item as selected.
  dr.selection = 0;
}

/**
 * Applies the keyframes to the line
 * @param {Frame Number} pos
 * @param {index of the line in composition} line
 * @param {time at which keyframe to be placed} rtime
 * @param {composition} rcom
 * @param {Type of line} d
 * @param {json file} jso
 */
function applyKeyframes(pos, line, rtime, rcom, d, jso) {
  var vert;
  if (d < 3) {
    vert = getJsonValuesRow(jso, pos, d);
  } else {
    //seperate method as it has a extra depth
    vert = getJsonValuesCenter(jso, pos);
  }

  // Temp shape
  var selLayer = rcom
    .layer(line)
    .property("ADBE Root Vectors Group")
    .property("ADBE Vector Shape - Group")
    .property("ADBE Vector Shape");
  var tShp = new Shape();
  tShp.vertices = vert;
  tShp.closed = false;
  selLayer.setValueAtTime(rtime, tShp);
}

/**
 * Returns the vertices for ROW
 * @param {json file} jso
 * @param {frame number} y
 * @param {type of line} z
 * @returns [[x1,y1],[x2,y2]] two points of line
 */
function getJsonValuesRow(jso, y, z) {
  lx1 = jso
    .property("Data")
    .property(1)
    .property(z)
    .property(y)
    .property(1)
    .property(1).value;
  ly1 = jso
    .property("Data")
    .property(1)
    .property(z)
    .property(y)
    .property(1)
    .property(2).value;
  lx2 = jso
    .property("Data")
    .property(1)
    .property(z)
    .property(y)
    .property(1)
    .property(3).value;
  ly2 = jso
    .property("Data")
    .property(1)
    .property(z)
    .property(y)
    .property(1)
    .property(4).value;
  return [
    [lx1, ly1],
    [lx2, ly2],
  ];
}
/**
 * Returns the vertices of centerline
 * @param {json file} jso
 * @param {frame number} y
 * @returns [[x1,y1],[x2,y2]] two points of line
 */
function getJsonValuesCenter(jso, y) {
  cx1 = jso
    .property("Data")
    .property(1)
    .property(3)
    .property(y)
    .property(1)
    .property(1)
    .property(1).value;
  cy1 = jso
    .property("Data")
    .property(1)
    .property(3)
    .property(y)
    .property(1)
    .property(1)
    .property(2).value;
  cx2 = jso
    .property("Data")
    .property(1)
    .property(3)
    .property(y)
    .property(1)
    .property(1)
    .property(3).value;
  cy2 = jso
    .property("Data")
    .property(1)
    .property(3)
    .property(y)
    .property(1)
    .property(1)
    .property(4).value;
  return [
    [cx1, cy1],
    [cx2, cy2],
  ];
}
