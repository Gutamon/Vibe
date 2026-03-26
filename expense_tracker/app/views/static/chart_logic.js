/**
 * chart_logic.js
 * 負責從 API 取得資料並渲染 Chart.js 圖表。
 */

const PALETTE = [
  "#c8f04a", "#4af0c8", "#f04a4a", "#f0c84a",
  "#4a8af0", "#c84af0", "#4af04a", "#f08c4a",
];

Chart.defaults.color = "#6b6b78";
Chart.defaults.borderColor = "#2a2a30";
Chart.defaults.font.family = "'Noto Sans TC', sans-serif";

// ── Monthly Chart ─────────────────────────────────────────────────────────────

async function renderMonthly() {
  const res = await fetch("/api/charts/monthly");
  const data = await res.json();

  const labels = data.map(d => `${d.year}/${String(d.month).padStart(2, "0")}`);
  const values = data.map(d => d.total);

  const ctx = document.getElementById("monthly-chart").getContext("2d");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "支出（NT$）",
        data: values,
        backgroundColor: "rgba(200,240,74,0.18)",
        borderColor: "#c8f04a",
        borderWidth: 2,
        borderRadius: 6,
        hoverBackgroundColor: "rgba(200,240,74,0.35)",
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` NT$ ${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          ticks: {
            callback: v => `$${(v / 1000).toFixed(0)}k`,
          },
        },
      },
    },
  });
}

// ── Category Donut Chart ──────────────────────────────────────────────────────

async function renderCategory() {
  const res = await fetch("/api/charts/category");
  const data = await res.json();

  const labels = data.map(d => d.category);
  const values = data.map(d => d.total);
  const total = values.reduce((a, b) => a + b, 0);

  // Donut chart
  const ctx = document.getElementById("category-chart").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: PALETTE.slice(0, labels.length),
        borderColor: "#18181c",
        borderWidth: 3,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      cutout: "62%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` NT$ ${ctx.parsed.toLocaleString()} (${((ctx.parsed / total) * 100).toFixed(1)}%)`,
          },
        },
      },
    },
  });

  // Table
  const tbody = document.getElementById("cat-tbody");
  data.forEach((d, i) => {
    const pct = ((d.total / total) * 100).toFixed(1);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="dot" style="background:${PALETTE[i % PALETTE.length]}"></span>${d.category}</td>
      <td class="amount">NT$ ${d.total.toLocaleString()}</td>
      <td>${pct}%</td>
    `;
    tbody.appendChild(tr);
  });
}

// ── Init ─────────────────────────────────────────────────────────────────────

renderMonthly();
renderCategory();
