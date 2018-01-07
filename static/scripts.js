$(document).ready(function() {
  $.getJSON("/analytics", function(data) {
    console.log(data); // this will show the info it in firebug console

// Source: https://bl.ocks.org/d3noob/bdf28027e0ce70bd132edc64f1dd7ea4

    var svg = d3.select("svg");
// Set up margins
    var top_margin = 120;
    var right_margin = 120;
    var bottom_margin = 120;
    var left_margin = 120;

    var width = svg.attr("width") - left_margin - right_margin;
    var height = svg.attr("height") - top_margin - bottom_margin;

    var x = d3.scaleBand().rangeRound([0, width]).padding(0.1);
    var y = d3.scaleLinear().rangeRound([height, 0]);

    var g = svg.append("g").attr("transform", "translate(" + left_margin + ", " + top_margin + ")");

    // Get the user_id and COUNT columns
    x.domain(data.map(function(obj) { return obj["user_id"] }))
    y.domain([0, d3.max(data, function(obj) { return obj["COUNT(*)"]})])

    g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y))
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("text-anchor", "end")
      .text("user_id");

  // Male the bar graph
    g.selectAll(".bar")
    .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(obj) { return x(obj["user_id"]); })
      .attr("y", function(obj) { return y(obj["COUNT(*)"]); })
      .attr("width", x.bandwidth())
      .attr("height", function(obj) { return height - y(obj["COUNT(*)"]); });
  });
});