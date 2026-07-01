let barChartInstance = null;
let pieChartInstance = null;

document.addEventListener("DOMContentLoaded", function () {
  const rawData = JSON.parse(document.getElementById("chart-data").textContent);

  const dataValues = [
    rawData.valid,
    rawData.not_valid,
    rawData.perlu_diperiksa,
    rawData.tidak_terdeteksi
  ];
  const labels = [
    "Valid",
    "Tidak Memenuhi Syarat",
    "Perlu Diperiksa",
    "Tidak Terdeteksi"
  ];
  const bgColors = ["#27ae60", "#e74c3c", "#f39c12", "#3498db"];

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