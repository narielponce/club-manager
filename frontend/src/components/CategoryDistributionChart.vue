<script setup>
import { Pie } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { computed } from 'vue';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const props = defineProps({
  chartData: {
    type: Array,
    required: true,
  },
  chartTitle: {
    type: String,
    required: true,
  }
});

// A set of colors for the pie chart slices
const chartColors = [
  '#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFCE56', '#4BC0C0', 
  '#9966FF', '#FF9F40', '#36A2EB', '#FF6384', '#C9CBCF', '#4D5360'
];

const pieChartData = computed(() => {
  if (!props.chartData || props.chartData.length === 0) {
    return { labels: [], datasets: [] };
  }

  const labels = props.chartData.map(item => item.category);
  const data = props.chartData.map(item => item.total);

  return {
    labels,
    datasets: [
      {
        backgroundColor: chartColors.slice(0, data.length),
        data: data,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: props.chartTitle,
      font: {
        size: 16
      }
    }
  }
};
</script>

<template>
  <div style="height: 400px">
    <Pie v-if="pieChartData.labels.length" :data="pieChartData" :options="chartOptions" />
    <div v-else class="d-flex justify-content-center align-items-center h-100">
      <p class="text-muted">No hay datos para mostrar.</p>
    </div>
  </div>
</template>
