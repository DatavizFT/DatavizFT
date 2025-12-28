/**
 * Graphique d'évolution des compétences avec Apache ECharts
 */

import ReactECharts from 'echarts-for-react';
import type { SkillEvolutionPoint } from '../../types';

interface SkillsEvolutionChartProps {
  data: SkillEvolutionPoint[];
  isLoading?: boolean;
  totalJobs?: number;
}

// Palette de couleurs pour les compétences
const COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f97316', // orange
  '#6366f1', // indigo
];

export function SkillsEvolutionChart({
  data,
  isLoading,
  totalJobs,
}: SkillsEvolutionChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Chargement des données...</div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">
            Aucune donnée disponible pour les filtres sélectionnés
          </div>
        </div>
      </div>
    );
  }

  // Organiser les données par date et compétence
  const dates = [...new Set(data.map((d) => d.date))].sort();
  const skills = [...new Set(data.map((d) => d.skill))];

  // Créer une map pour accès rapide
  const dataMap = new Map<string, number>();
  data.forEach((d) => {
    dataMap.set(`${d.date}_${d.skill}`, d.count);
  });

  // Créer les séries pour chaque compétence
  const series = skills.map((skill, index) => ({
    name: skill,
    type: 'line' as const,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: {
      width: 2,
    },
    itemStyle: {
      color: COLORS[index % COLORS.length],
    },
    data: dates.map((date) => dataMap.get(`${date}_${skill}`) || 0),
  }));

  const option = {
    title: {
      text: 'Évolution des compétences recherchées',
      subtext: totalJobs ? `${totalJobs.toLocaleString()} offres analysées` : '',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1f2937',
      },
      subtextStyle: {
        fontSize: 12,
        color: '#6b7280',
      },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: {
        color: '#374151',
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6366f1',
        },
      },
    },
    legend: {
      data: skills,
      bottom: 0,
      type: 'scroll',
      textStyle: {
        fontSize: 11,
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates.map((d) => {
        const date = new Date(d);
        return date.toLocaleDateString('fr-FR', {
          day: '2-digit',
          month: 'short',
        });
      }),
      axisLine: {
        lineStyle: {
          color: '#e5e7eb',
        },
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 11,
      },
      splitLine: {
        lineStyle: {
          color: '#f3f4f6',
        },
      },
    },
    series,
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <ReactECharts
        option={option}
        style={{ height: '400px', width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  );
}
