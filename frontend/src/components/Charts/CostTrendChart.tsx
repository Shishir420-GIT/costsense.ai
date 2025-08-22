import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { CostDataPoint } from '@/types/cost.types';

interface CostTrendChartProps {
  data: CostDataPoint[];
  width?: number;
  height?: number;
  className?: string;
}

export const CostTrendChart: React.FC<CostTrendChartProps> = ({
  data,
  width = 800,
  height = 400,
  className = ''
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Parse dates and prepare data
    const parseDate = d3.timeParse("%Y-%m-%d");
    const processedData = data.map(d => ({
      ...d,
      date: parseDate(d.date) || new Date(),
      cost: +d.cost
    }));

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(processedData, d => d.date) as [Date, Date])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(processedData, d => d.cost) as number])
      .nice()
      .range([innerHeight, 0]);

    // Create main group
    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add gradient definition
    const gradient = svg.append("defs")
      .append("linearGradient")
      .attr("id", "cost-gradient")
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", 0).attr("y1", innerHeight)
      .attr("x2", 0).attr("y2", 0);

    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", "#3B82F6")
      .attr("stop-opacity", 0.1);

    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "#3B82F6")
      .attr("stop-opacity", 0.8);

    // Line generator
    const line = d3.line<any>()
      .x(d => xScale(d.date))
      .y(d => yScale(d.cost))
      .curve(d3.curveMonotoneX);

    // Area generator
    const area = d3.area<any>()
      .x(d => xScale(d.date))
      .y0(innerHeight)
      .y1(d => yScale(d.cost))
      .curve(d3.curveMonotoneX);

    // Add area
    g.append("path")
      .datum(processedData)
      .attr("fill", "url(#cost-gradient)")
      .attr("d", area);

    // Add line
    g.append("path")
      .datum(processedData)
      .attr("fill", "none")
      .attr("stroke", "#3B82F6")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    g.selectAll(".dot")
      .data(processedData)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.cost))
      .attr("r", 4)
      .attr("fill", "#3B82F6")
      .style("cursor", "pointer")
      .on("mouseover", function(event, d) {
        // Tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.8)")
          .style("color", "white")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("opacity", 0);

        tooltip.transition()
          .duration(200)
          .style("opacity", 0.9);

        tooltip.html(`
          <div>Date: ${d3.timeFormat("%Y-%m-%d")(d.date)}</div>
          <div>Cost: $${d.cost.toLocaleString()}</div>
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        d3.selectAll(".tooltip").remove();
      });

    // Add X axis
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%b %Y")));

    // Add Y axis
    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d => `$${d3.format(".2s")(d)}`));

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (innerHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Cost ($)");

    g.append("text")
      .attr("transform", `translate(${innerWidth / 2}, ${innerHeight + margin.bottom})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Date");

  }, [data, width, height]);

  return (
    <div className={`cost-trend-chart ${className}`}>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default CostTrendChart;