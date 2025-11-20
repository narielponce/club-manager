<script setup>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { computed } from 'vue';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps({
  reportData: {
    type: Object,
    required: true,
  },
});

const chartData = computed(() => {
  if (!props.reportData || !props.reportData.items) {
    return { labels: [], datasets: [] };
  }
  
  const labels = props.reportData.items.map(item => item.month_name);
  const incomeData = props.reportData.items.map(item => item.income);
  const expenseData = props.reportData.items.map(item => item.expense);

  return {
    labels,
    datasets: [
      {
        label: 'Ingresos',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgb(75, 192, 192)',
        borderWidth: 1,
        data: incomeData,
      },
      {
        label: 'Gastos',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgb(255, 99, 132)',
        borderWidth: 1,
        data: expenseData,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};
</script>

<template>
  <div style="height: 400px">
    <Bar v-if="chartData.labels.length" :data="chartData" :options="chartOptions" />
  </div>
</template>
