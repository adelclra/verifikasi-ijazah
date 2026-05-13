let barChartInstance = null;
let pieChartInstance = null;

document.addEventListener("DOMContentLoaded", function () {
  const rawData = JSON.parse(document.getElementById("chart-data").textContent);

  const dataValues = [rawData.valid, rawData.not_valid, rawData.pending, rawData.unknown_year || 0];
  const labels = ["Valid", "Tidak Valid", "Menunggu", "Tidak Terdeteksi"];
  const bgColors = ["#27ae60", "#e74c3c", "#3498db", "#f39c12"];

  if (barChartInstance) barChartInstance.destroy();
  if (pieChartInstance) pieChartInstance.destroy();

  // ================= BAR =================
  barChartInstance = new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          data: dataValues,
          backgroundColor: bgColors,
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
        },
      },
    },
  });

  // ================= PIE =================
  pieChartInstance = new Chart(document.getElementById("pieChart"), {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: dataValues,
          backgroundColor: bgColors,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
});