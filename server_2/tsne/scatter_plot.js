// Set dimensions and margins for the chart
const margin = {top: 20, right: 30, bottom: 40, left: 40},
      width = 1200 - margin.left - margin.right,
      height = 800 - margin.top - margin.bottom;

// Append the svg object to the body of the page
const svg = d3.select("#chart")
              .append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .append("g")
              .attr("transform", `translate(${margin.left},${margin.top})`);

// Load data
d3.csv("tsne_data.csv").then(data => {
    // Add X axis
    data.forEach(d => {
      d.x_pos = parseFloat(d.x_pos);
      d.netPrice = parseFloat(d.netPrice);
    });
    // Find min and max values for normalization
    const xMin = d3.min(data, d => d.x_pos);
    const xMax = d3.max(data, d => d.x_pos);
    const yMin = d3.min(data, d => d.netPrice);
    const yMax = d3.max(data, d => d.netPrice);

    // Normalize data
    data.forEach(d => {
        d.x_pos = (d.x_pos - xMin) / (xMax - xMin);
        d.netPrice = (d.netPrice - yMin) / (yMax - yMin);
    });
    console.log(data, d3.min(data, d => d.x_pos), d3.max(data, d => Math.abs(d.x_pos)))
    const x = d3.scaleLinear()
                .domain([d3.min(data, d => d.x_pos), d3.max(data, d => d.x_pos)])
                .range([ 0, width - margin.right ]);
    svg.append("g")
       .attr("transform", `translate(0,${height})`)
       .call(d3.axisBottom(x));

    // Add Y axis
    const y = d3.scaleLinear()
                .domain([d3.min(data, d => d.netPrice), d3.max(data, d => d.netPrice)])
                .range([ height - 50, 50]);
    svg.append("g")
       .call(d3.axisLeft(y));

    // Add dots
    svg.append('g')
       .selectAll("dot")
       .data(data)
       .enter()
       .append("circle")
       .attr("cx", d => x(d.x_pos))
       .attr("cy", d => y(d.netPrice))
       .attr("r", d => d.transactionVolume)
       .attr("class", "dot");

    // Determine the best number of clusters using the elbow method
    const maxK = 10;
    const sse = calculateSSE(data, maxK);
    // const bestK = elbowMethod(sse);
    const bestK = 5

    // Log the best number of clusters
    console.log("Best number of clusters:", bestK);

    // Clustering with the best number of clusters
    const clusters = kmeans(data, bestK);
    
    // Add clustered dots with different colors
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    clusters.forEach((cluster, i) => {
        svg.append('g')
           .selectAll(`.dot${i}`)
           .data(cluster)
           .enter()
           .append("circle")
           .attr("cx", d => x(d.x_pos))
           .attr("cy", d => y(d.netPrice))
           .attr("r", d => d.transactionVolume)
           .attr("fill", color(i))
           .attr("stroke", "black")
    });
    generateClusterReports(clusters)
});

// K-means clustering function
function kmeans(data, k) {
    const centroids = initializeCentroids(data, k);
    let clusters = new Array(k);
    let hasChanged = true;
    console.log('kmeans', data);

    while (hasChanged) {
        clusters = assignClusters(data, centroids);
        const newCentroids = recomputeCentroids(clusters);
        hasChanged = !compareCentroids(centroids, newCentroids);
        centroids.forEach((c, i) => { centroids[i] = newCentroids[i]; });
    }

    return clusters;
}
 
function initializeCentroids(data, k) {
    return data.sort(() => 0.5 - Math.random()).slice(0, k);
}

function assignClusters(data, centroids) {
    return data.reduce((clusters, point) => {
        let minDist = Infinity;
        let clusterIndex = 0;
        centroids.forEach((centroid, i) => {
            const dist = Math.sqrt(Math.pow(point.x_pos - centroid.x_pos, 2) + Math.pow(point.netPrice - centroid.netPrice, 2));
            if (dist < minDist) {
                minDist = dist;
                clusterIndex = i;
            }
        });
        clusters[clusterIndex] = clusters[clusterIndex] || [];
        clusters[clusterIndex].push(point);
        return clusters;
    }, new Array(centroids.length));
}

function recomputeCentroids(clusters) {
    return clusters.map(cluster => {
        const sum = cluster.reduce((a, b) => ({
            x_pos: a.x_pos + b.x_pos,
            netPrice: a.netPrice + b.netPrice
        }), { x_pos: 0, netPrice: 0 });
        return {
            x_pos: sum.x_pos / cluster.length,
            netPrice: sum.netPrice / cluster.length
        };
    });
}

function compareCentroids(centroids, newCentroids) {
    return centroids.every((c, i) => c.x_pos === newCentroids[i].x_pos && c.netPrice === newCentroids[i].netPrice);
}
function calculateSSE(data, maxK) {
  const sse = [];
  for (let k = 1; k <= maxK; k++) {
      const clusters = kmeans(data, k);
      let sumSquaredError = 0;
      clusters.forEach(cluster => {
          const centroid = recomputeCentroids([cluster])[0];
          cluster.forEach(point => {
              const dist = Math.pow(point.x_pos - centroid.x_pos, 2) + Math.pow(point.netPrice - centroid.netPrice, 2);
              sumSquaredError += dist;
          });
      });
      sse.push(sumSquaredError);
  }
  return sse;
}

function elbowMethod(sse) {
  const diffs = [];
  for (let i = 1; i < sse.length; i++) {
      diffs.push(sse[i - 1] - sse[i]);
  }
  const secondDiffs = [];
  for (let i = 1; i < diffs.length; i++) {
      secondDiffs.push(diffs[i - 1] - diffs[i]);
  }
  const elbow = secondDiffs.indexOf(Math.max(...secondDiffs)) + 1;
  return elbow + 1;
}

// 统计每个聚类类别的均值、方差等统计指标，并将报告信息添加到 HTML 页面中
function generateClusterReports(clusters) {
  const reportDiv = document.getElementById('report');
  clusters.forEach((cluster, i) => {
      const clusterSize = cluster.length;
      const clusterData = cluster.map(point => [point.x_pos, point.netPrice]);
      const x_posMean = d3.mean(clusterData, d => d[0]);
      const netPriceMean = d3.mean(clusterData, d => d[1]);
      const x_posVariance = d3.variance(clusterData, d => d[0]);
      const netPriceVariance = d3.variance(clusterData, d => d[1]);
      const report = `
          <div>
              <h2>Cluster ${i + 1} Report:</h2>
              <p>- Size: ${clusterSize}</p>
              <p>- x_pos Mean: ${x_posMean.toFixed(2)}</p>
              <p>- netPrice Mean: ${netPriceMean.toFixed(2)}</p>
              <p>- x_pos Variance: ${x_posVariance.toFixed(2)}</p>
              <p>- netPrice Variance: ${netPriceVariance.toFixed(2)}</p>
              <!-- 还可以添加其他统计指标 -->
          </div>
      `;
      reportDiv.innerHTML += report;
  });
}
