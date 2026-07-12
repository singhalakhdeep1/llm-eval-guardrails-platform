import React, { useState, useEffect } from 'react';

interface CostData {
  date: string;
  modelId: string;
  modelName: string;
  tokensUsed: number;
  cost: number;
}

interface TokenCostTrackingProps {
  userId: string;
}

export function TokenCostTracking({ userId }: TokenCostTrackingProps) {
  const [costData, setCostData] = useState<CostData[]>([]);
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCostData();
  }, [timeRange, selectedModel]);

  const fetchCostData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/users/${userId}/costs?range=${timeRange}&model=${selectedModel}`
      );
      if (response.ok) {
        const data = await response.json();
        setCostData(data);
      }
    } catch (error) {
      console.error('Failed to fetch cost data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const totalCost = costData.reduce((sum, item) => sum + item.cost, 0);
  const totalTokens = costData.reduce((sum, item) => sum + item.tokensUsed, 0);
  const avgCostPer1k = totalTokens > 0 ? (totalCost / totalTokens) * 1000 : 0;

  const costsByModel = costData.reduce((acc, item) => {
    if (!acc[item.modelName]) {
      acc[item.modelName] = { cost: 0, tokens: 0 };
    }
    acc[item.modelName].cost += item.cost;
    acc[item.modelName].tokens += item.tokensUsed;
    return acc;
  }, {} as Record<string, { cost: number; tokens: number }>);

  const uniqueModels = Array.from(new Set(costData.map(d => d.modelName)));

  if (isLoading) return <div>Loading cost data...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Token Cost Tracking</h2>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as any)}
          className="border rounded px-3 py-2"
        >
          <option value="day">Last 24 Hours</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
        </select>

        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="all">All Models</option>
          {uniqueModels.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">Total Cost</p>
          <p className="text-2xl font-bold">${totalCost.toFixed(2)}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">Total Tokens</p>
          <p className="text-2xl font-bold">{(totalTokens / 1000).toFixed(0)}K</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">Avg Cost / 1K Tokens</p>
          <p className="text-2xl font-bold">${avgCostPer1k.toFixed(4)}</p>
        </div>
      </div>

      {/* Cost by Model */}
      <div>
        <h3 className="font-semibold mb-3">Cost by Model</h3>
        <div className="space-y-3">
          {Object.entries(costsByModel).map(([modelName, data]) => (
            <div key={modelName} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <p className="font-semibold">{modelName}</p>
                <p className="font-bold">${data.cost.toFixed(2)}</p>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>{(data.tokens / 1000).toFixed(0)}K tokens</span>
                <span>${((data.cost / data.tokens) * 1000).toFixed(4)} / 1K</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${(data.cost / totalCost) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Over Time Chart Placeholder */}
      <div>
        <h3 className="font-semibold mb-3">Cost Over Time</h3>
        <div className="border rounded-lg p-4 h-64 flex items-center justify-center bg-gray-50">
          <p className="text-gray-500">Cost trend chart would display here</p>
        </div>
      </div>

      {/* Cost Breakdown Table */}
      <div>
        <h3 className="font-semibold mb-3">Detailed Breakdown</h3>
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Date</th>
                <th className="px-4 py-3 text-left font-semibold">Model</th>
                <th className="px-4 py-3 text-right font-semibold">Tokens</th>
                <th className="px-4 py-3 text-right font-semibold">Cost</th>
              </tr>
            </thead>
            <tbody>
              {costData.map((item, idx) => (
                <tr key={idx} className="border-t">
                  <td className="px-4 py-3">{new Date(item.date).toLocaleDateString()}</td>
                  <td className="px-4 py-3">{item.modelName}</td>
                  <td className="px-4 py-3 text-right">{item.tokensUsed.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">${item.cost.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
