import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface UtilizationData {
  service: string;
  resource: string;
  utilization: number;
  cost: number;
}

interface UtilizationHeatmapProps {
  data: UtilizationData[];
  width?: number;
  height?: number;
  className?: string;
}

export const UtilizationHeatmap: React.FC<UtilizationHeatmapProps> = ({
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

    const margin = { top: 50, right: 50, bottom: 50, left: 100 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Group data by service
    const serviceGroups = Array.from(d3.group(data, d => d.service).entries());
    const maxResourcesPerService = Math.max(...serviceGroups.map(([, resources]) => resources.length));

    // Scales
    const xScale = d3.scaleBand()
      .domain(serviceGroups.map(([service]) => service))
      .range([0, innerWidth])
      .padding(0.1);

    const yScale = d3.scaleBand()
      .domain(Array.from({length: maxResourcesPerService}, (_, i) => `Resource ${i + 1}`))
      .range([0, innerHeight])
      .padding(0.1);

    // Color scale for utilization
    const colorScale = d3.scaleSequential(d3.interpolateRdYlBu)
      .domain([100, 0]); // Red for high utilization, blue for low

    // Size scale for cost (bubble size)
    const sizeScale = d3.scaleSqrt()
      .domain(d3.extent(data, d => d.cost) as [number, number])
      .range([4, 20]);

    // Create main group
    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create cells for each service-resource combination
    serviceGroups.forEach(([service, resources]) => {
      resources.forEach((resource, index) => {
        const x = xScale(service)! + xScale.bandwidth() / 2;
        const y = yScale(`Resource ${index + 1}`)! + yScale.bandwidth() / 2;

        // Create cell background
        g.append("rect")
          .attr("x", xScale(service)!)
          .attr("y", yScale(`Resource ${index + 1}`)!)
          .attr("width", xScale.bandwidth())
          .attr("height", yScale.bandwidth())
          .attr("fill", "#f8f9fa")
          .attr("stroke", "#dee2e6")
          .attr("stroke-width", 1);

        // Create utilization circle
        g.append("circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", sizeScale(resource.cost))
          .attr("fill", colorScale(resource.utilization))
          .attr("stroke", "#fff")
          .attr("stroke-width", 2)
          .style("cursor", "pointer")
          .on("mouseover", function(event) {
            // Tooltip
            const tooltip = d3.select("body").append("div")
              .attr("class", "tooltip")
              .style("position", "absolute")
              .style("background", "rgba(0, 0, 0, 0.8)")
              .style("color", "white")
              .style("padding", "10px")
              .style("border-radius", "6px")
              .style("font-size", "12px")
              .style("pointer-events", "none")
              .style("opacity", 0);

            tooltip.transition()
              .duration(200)
              .style("opacity", 0.9);

            tooltip.html(`
              <div><strong>${service}</strong></div>
              <div>Resource: ${resource.resource}</div>
              <div>Utilization: ${resource.utilization.toFixed(1)}%</div>
              <div>Cost: $${resource.cost.toLocaleString()}</div>
            `)
              .style("left", (event.pageX + 10) + "px")
              .style("top", (event.pageY - 28) + "px");

            // Highlight effect
            d3.select(this)
              .transition()
              .duration(200)
              .attr("r", sizeScale(resource.cost) + 3)
              .attr("stroke-width", 3);
          })
          .on("mouseout", function() {
            d3.selectAll(".tooltip").remove();
            
            // Remove highlight effect
            d3.select(this)
              .transition()
              .duration(200)
              .attr("r", sizeScale(resource.cost))
              .attr("stroke-width", 2);
          });

        // Add utilization text
        g.append("text")
          .attr("x", x)
          .attr("y", y)
          .attr("dy", "0.35em")
          .attr("text-anchor", "middle")
          .style("font-size", "10px")
          .style("font-weight", "bold")
          .style("fill", resource.utilization > 50 ? "white" : "black")
          .style("pointer-events", "none")
          .text(`${resource.utilization.toFixed(0)}%`);
      });
    });

    // Add X axis
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)");

    // Add Y axis
    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("Resource Utilization Heatmap");

    // Add legend
    const legendWidth = 200;
    const legendHeight = 20;
    const legend = svg.append("g")
      .attr("transform", `translate(${width - legendWidth - 20}, 30)`);

    // Create gradient for legend
    const legendGradient = svg.append("defs")
      .append("linearGradient")
      .attr("id", "legend-gradient")
      .attr("x1", "0%")
      .attr("x2", "100%");

    legendGradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", colorScale(0));

    legendGradient.append("stop")
      .attr("offset", "50%")
      .attr("stop-color", colorScale(50));

    legendGradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", colorScale(100));

    legend.append("rect")
      .attr("width", legendWidth)
      .attr("height", legendHeight)
      .style("fill", "url(#legend-gradient)");

    // Legend labels
    legend.append("text")
      .attr("x", 0)
      .attr("y", -5)
      .style("font-size", "12px")
      .text("0%");

    legend.append("text")
      .attr("x", legendWidth / 2)
      .attr("y", -5)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Utilization");

    legend.append("text")
      .attr("x", legendWidth)
      .attr("y", -5)
      .attr("text-anchor", "end")
      .style("font-size", "12px")
      .text("100%");

  }, [data, width, height]);

  return (
    <div className={`utilization-heatmap ${className}`}>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default UtilizationHeatmap;