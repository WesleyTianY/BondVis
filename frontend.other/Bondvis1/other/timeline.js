/* eslint-disable */
var timeline = (function() {
  return function() {
    var timelines = [];
    var dateAccessor = function(d) {
      return new Date(d);
    };
    var processedTimelines = [];
    var startAccessor = function(d) {
      return d.start;
    };
    var endAccessor = function(d) {
      return d.end;
    };
    var size = [500, 100];
    var timelineExtent = [-Infinity, Infinity];
    var setExtent = [];
    var displayScale = d3.scaleLinear();
    var swimlanes = [];
    var padding = 0;
    var fixedExtent = false;
    var maximumHeight = Infinity;

    function processTimelines() {
      timelines.forEach(function(band) {
        var projectedBand = { start: null, end: null, lane: null };
        for (var x in band) {
          if (band.hasOwnProperty(x)) {
            projectedBand[x] = band[x];
          }
        }
        projectedBand.start = dateAccessor(startAccessor(band));
        projectedBand.end = dateAccessor(endAccessor(band));
        projectedBand.lane = 0;
        processedTimelines.push(projectedBand);
      });
    }

    function projectTimelines() {
      if (fixedExtent === false) {
        var minStart = d3.min(processedTimelines, function(d) {
          return d.start;
        });
        var maxEnd = d3.max(processedTimelines, function(d) {
          return d.end;
        });
        timelineExtent = [minStart, maxEnd];
      } else {
        timelineExtent = [
          +dateAccessor(setExtent[0]),
          +dateAccessor(setExtent[1])
        ];
      }

      displayScale.domain(timelineExtent).range([0, size[0]]);

      processedTimelines.forEach(function(band) {
        band.originalStart = band.start;
        band.originalEnd = band.end;
        band.start = displayScale(band.start);
        band.end = displayScale(band.end);
      });
    }

    function fitsIn(lane, band) {
      if (lane.end < band.start || lane.start > band.end) {
        return true;
      }
      var filteredLane = lane.filter(function(d) {
        return d.start <= band.end && d.end >= band.start;
      });
      if (filteredLane.length === 0) {
        return true;
      }
      return false;
    }

    function findlane(band) {
      //make the first array
      if (swimlanes[0] === undefined) {
        swimlanes[0] = [band];
        return;
      }
      var l = swimlanes.length - 1;
      var x = 0;

      while (x <= l) {
        if (fitsIn(swimlanes[x], band)) {
          swimlanes[x].push(band);
          return;
        }
        x++;
      }
      swimlanes[x] = [band];
      return;
    }

    function timeline(data) {
      if (!arguments.length) return timeline;

      timelines = data;

      processedTimelines = [];
      swimlanes = [];

      processTimelines();
      projectTimelines();

      processedTimelines.forEach(function(band) {
        findlane(band);
      });

      var height = size[1] / swimlanes.length;
      height = Math.min(height, maximumHeight);

      swimlanes.forEach(function(lane, i) {
        lane.forEach(function(band) {
          band.y = i * height;
          band.dy = height - padding;
          band.lane = i;
        });
      });

      return processedTimelines;
    }

    timeline.dateFormat = function(_x) {
      if (!arguments.length) return dateAccessor;
      dateAccessor = _x;
      return timeline;
    };

    timeline.bandStart = function(_x) {
      if (!arguments.length) return startAccessor;
      startAccessor = _x;
      return timeline;
    };

    timeline.bandEnd = function(_x) {
      if (!arguments.length) return endAccessor;
      endAccessor = _x;
      return timeline;
    };

    timeline.size = function(_x) {
      if (!arguments.length) return size;
      size = _x;
      return timeline;
    };

    timeline.padding = function(_x) {
      if (!arguments.length) return padding;
      padding = _x;
      return timeline;
    };

    timeline.extent = function(_x) {
      if (!arguments.length) return timelineExtent;
      fixedExtent = true;
      setExtent = _x;
      if (_x.length === 0) {
        fixedExtent = false;
      }
      return timeline;
    };

    timeline.maxBandHeight = function(_x) {
      if (!arguments.length) return maximumHeight;
      maximumHeight = _x;
      return timeline;
    };

    return timeline;
  };
})()


var testData = [
  {times: [{"starting_time": 1355752800000, "ending_time": 1355759900000}, {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {times: [{"starting_time": 1355759910000, "ending_time": 1355761900000}, ]},
  {times: [{"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var rectAndCircleTestData = [
  {times: [{"starting_time": 1355752800000,
            "display": "circle"}, {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {times: [{"starting_time": 1355759910000,
  "display":"circle"}, ]},
  {times: [{"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var labelTestData = [
  {label: "person a", times: [{"starting_time": 1355752800000, "ending_time": 1355759900000}, {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {label: "person b", times: [{"starting_time": 1355759910000, "ending_time": 1355761900000}, ]},
  {label: "person c", times: [{"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var iconTestData = [
  {class:"jackie", icon: "jackie.png", times: [
    {"starting_time": 1355752800000, "ending_time": 1355759900000}, 
    {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {class:"troll", icon: "troll.png", times: [
    {"starting_time": 1355759910000, "ending_time": 1355761900000,
    "display":"circle"}, ]},
  {class:"wat", icon: "wat.png", times: [
    {"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var labelColorTestData = [
  {label: "person a", times: [{"color":"green", "label":"Weeee", "starting_time": 1355752800000, "ending_time": 1355759900000}, {"color":"blue", "label":"Weeee", "starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {label: "person b", times: [{"color":"pink", "label":"Weeee", "starting_time": 1355759910000, "ending_time": 1355761900000}, ]},
  {label: "person c", times: [{"color":"yellow", "label":"Weeee", "starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var testDataWithColor = [
  {label: "fruit 1", fruit: "orange", times: [
    {"starting_time": 1355759910000, "ending_time": 1355761900000}]},
  {label: "fruit 2", fruit: "apple", times: [
    {"starting_time": 1355752800000, "ending_time": 1355759900000},
    {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {label: "fruit3", fruit: "lemon", times: [
    {"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var testDataWithColorPerTime = [
  {label: "fruit 2", fruit: "apple", times: [
    {fruit: "orange", "starting_time": 1355752800000, "ending_time": 1355759900000},
    {"starting_time": 1355767900000, "ending_time": 1355774400000},
    {fruit: "lemon", "starting_time": 1355774400000, "ending_time": 1355775500000}]}
];
var testDataRelative = [
  {times: [{"starting_time": 1355752800000, "ending_time": 1355759900000}, {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
  {times: [{"starting_time": 1355759910000, "ending_time": 1355761900000}]},
  {times: [{"starting_time": 1355761910000, "ending_time": 1355763910000}]}
];
var width = 500;

function timelineRect() {
  var chart = d3.timeline();
  var svg = d3.select("#timeline1").append("svg").attr("width", width)
    .datum(testData).call(chart);
}
function timelineRectNoAxis() {
  var chart = d3.timeline().showTimeAxis();
  var svg = d3.select("#timeline1_noaxis").append("svg").attr("width", width)
    .datum(testData).call(chart);
}
function timelineCircle() {
  var chart = d3.timeline()
    .tickFormat( //
      {format: d3.time.format("%I %p"),
      tickTime: d3.time.hours,
      tickInterval: 1,
      tickSize: 30})
    .display("circle"); // toggle between rectangles and circles
  var svg = d3.select("#timeline2").append("svg").attr("width", width)
    .datum(testData).call(chart);
}
function timelineRectAndCircle() {
  var chart = d3.timeline();
  var svg = d3.select("#timeline2_combine").append("svg").attr("width", width)
    .datum(rectAndCircleTestData).call(chart);
}
function timelineHover() {
  var chart = d3.timeline()
    .width(width*4)
    .stack()
    .margin({left:70, right:30, top:0, bottom:0})
    .hover(function (d, i, datum) {
    // d is the current rendering object
    // i is the index during d3 rendering
    // datum is the id object
      var div = $('#hoverRes');
      var colors = chart.colors();
      div.find('.coloredDiv').css('background-color', colors(i))
      div.find('#name').text(datum.label);
    })
    .click(function (d, i, datum) {
      alert(datum.label);
    })
    .scroll(function (x, scale) {
      $("#scrolled_date").text(scale.invert(x) + " to " + scale.invert(x+width));
    });
  var svg = d3.select("#timeline3").append("svg").attr("width", width)
    .datum(labelTestData).call(chart);
}
function timelineStackedIcons() {
  var chart = d3.timeline()
    .beginning(1355752800000) // we can optionally add beginning and ending times to speed up rendering a little
    .ending(1355774400000)
    .showTimeAxisTick() // toggles tick marks
    .stack() // toggles graph stacking
    .margin({left:70, right:30, top:0, bottom:0})
    ;
  var svg = d3.select("#timeline5").append("svg").attr("width", width)
    .datum(iconTestData).call(chart);
}
function timelineLabelColor() {
  var chart = d3.timeline()
    .beginning(1355752800000) // we can optionally add beginning and ending times to speed up rendering a little
    .ending(1355774400000)
    .stack() // toggles graph stacking
    .margin({left:70, right:30, top:0, bottom:0})
    ;
  var svg = d3.select("#timeline6").append("svg").attr("width", width)
    .datum(labelColorTestData).call(chart);
}
function timelineRotatedTicks() {
  var chart = d3.timeline()
    .rotateTicks(45);
  var svg = d3.select("#timeline7").append("svg").attr("width", width)
    .datum(testData).call(chart);
}
function timelineRectColors() {
  var colorScale = d3.scale.ordinal().range(['#6b0000','#ef9b0f','#ffee00'])
      .domain(['apple','orange','lemon']);
  var chart = d3.timeline()
      .colors( colorScale )
      .colorProperty('fruit');
  var svg = d3.select("#timelineColors").append("svg").attr("width", width)
    .datum(testDataWithColor).call(chart);
}
function timelineRectColorsPerTime() {
  var colorScale = d3.scale.ordinal().range(['#6b0000','#ef9b0f','#ffee00'])
    .domain(['apple','orange','lemon']);
  var chart = d3.timeline()
    .colors( colorScale )
    .colorProperty('fruit');      
  var svg = d3.select("#timelineColorsPerTime").append("svg").attr("width", width)
    .datum(testDataWithColorPerTime).call(chart);  
}
function timelineRelativeTime() {
  //This solution is for relative time is from
  //http://stackoverflow.com/questions/11286872/how-do-i-make-a-custom-axis-formatter-for-hours-minutes-in-d3-js
  var chart = d3.timeline()
    .relativeTime()
    .tickFormat({
      format: function(d) { return d3.time.format("%H:%M")(d) },
      tickTime: d3.time.minutes,
      tickInterval: 30,
      tickSize: 15,
    });
  var svg = d3.select("#timelineRelativeTime").append("svg").attr("width", width)
    .datum(testDataRelative).call(chart);
    console.log(testDataRelative);
}
function timelineAxisTop() {
  var chart = d3.timeline().showAxisTop().stack();
  var svg = d3.select("#timelineAxisTop").append("svg").attr("width", width)
      .datum(testData).call(chart);
}
function timelineBgndTick() {
  var chart = d3.timeline().stack().showTimeAxisTick().background('grey');
  var svg = d3.select("#timelineBgndTick").append("svg").attr("width", width)
      .datum(testData).call(chart);
}
function timelineBgnd() {
  var chart = d3.timeline().stack().background('grey');
  var svg = d3.select("#timelineBgnd").append("svg").attr("width", width)
      .datum(testData).call(chart);
}
function timelineComplex() {
      var chart = d3.timeline();
    chart.stack();
    chart.showTimeAxisTick();
//     chart.showAxisTop();
//     chart.showToday();
//     chart.itemHeight(50);
    chart.margin({left: 250, right: 0, top: 20, bottom: 0});
    chart.itemMargin(0);
    chart.labelMargin(25);
    var backgroundColor = "#FCFCFD";
    var altBackgroundColor = "red";
    chart.background(function (datum, i) {
      var odd = (i % 2) === 0;
      return odd ? altBackgroundColor : backgroundColor;
    });
    chart.fullLengthBackgrounds();
      var svg = d3.select("#timelineComplex").append("svg").attr("width", width)
          .datum(labelTestData).call(chart);
}

// timelineRect();
// timelineRectNoAxis();
// timelineCircle();
// timelineRectAndCircle();
// timelineHover();
// timelineStackedIcons();
// timelineLabelColor();
// timelineRotatedTicks();
// timelineRectColors();
// timelineRectColorsPerTime();
// timelineRelativeTime();
// timelineAxisTop();
// timelineBgndTick();
// timelineBgnd();
// timelineComplex();
export default d3.timeline;

