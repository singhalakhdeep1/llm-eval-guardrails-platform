import React, { useState, useEffect } from 'react';

interface LatencyData {
  timestamp: string;
  modelId: string;
  modelName: string;
  latency: number;
  p50: number;
  p95: number;
  p99: number;
}

interface LatencyMonitoringProps {
  userId: string;
}

export function LatencyMonitoring({ userId }: LatencyMonitoringProps) {
  const [latencyData, setLatencyData] = useState<LatencyData[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<'hour' | 'day' | 'week'>('hour');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchLatencyData();
    const interval = setInterval(fetchLatencyData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [selectedModel, timeRange]);

  const fetchLatencyData = async () => {
    try {
      const response = await fetch(
        `/api/latency?model=${selectedModel}&range=${timeRange}`
      );
      if (response.ok) {
        const data = await response.json();
        setLatencyData(data);
      }
    } catch (error) {
      console.error('Failed to fetch latency data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const recentLatency = latencyData.slice(-1)[0];
  const avgLatency = latencyData.reduce((sum, d) => sum + d.latency, 0) / (latencyData.length || 1);
  const maxLatency = Math.max(...latencyData.map(d => d.latency));
  const minLatency = Math.min(...latencyData.map(d => d.latency));

  const getLatencyStatus = (latency: number) => {
    if (latency < 500) return { color: 'green', label: 'Good' };
    if (latency < 1000) return { color: 'yellow', label: 'Fair' };
    return { color: 'red', label: 'Slow' };
  };

  const uniqueModels = Array.from(new Set(latencyData.map(d => d.modelName)));

  if (isLoading) return <div>Loading latency data...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Latency Monitoring</h2>

      {/* Filters */}
      <div className="flex gap-4">
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

        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as any)}
          className="border rounded px-3 py-2"
        >
          <option value="hour">Last Hour</option>
          <option value="day">Last 24 Hours</option>
          <option value="week">Last 7 Days</option>
        </select>
      </div>

      {/* Current Status */}
      {recentLatency && (
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Current Latency</p>
              <p className="text-3xl font-bold">{recentLatency.latency.toFixed(0)}ms</p>
            </div>
            <div className={`px-4 py-2 rounded-full bg-${getLatencyStatus(recentLatency.latency).color}-100 text-${getLatencyStatus(recentLatency.latency).color}-700`}>
              {getLatencyStatus(recentLatency.latency).label}
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">Average</p>
          <p className="text-xl font-bold">{avgLatency.toFixed(0)}ms</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">P50</p>
          <p className="text-xl font-bold">{recentLatency?.p50.toFixed(0) || 0}ms</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">P95</p>
          <p className="text-xl font-bold">{recentLatency?.p95.toFixed(0) || 0}ms</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-gray-600">P99</p>
          <p className="text-xl font-bold">{recentLatency?.p99.toFixed(0) || 0}ms</p>
        </div>
      </div>

      {/* Latency Chart Placeholder */}
      <div>
        <h3 className="font-semibold mb-3">Latency Over Time</h3>
        <div className="border rounded-lg p-4 h-64 flex items-center justify-center bg-gray-50">
          <p className="text-gray-500">Real-time latency chart would display here</p>
        </div>
      </div>

      {/* Latency by Model */}
      <div>
        <h3 className="font-semibold mb-3">Latency by Model</h3>
        <div className="space-y-3">
          {uniqueModels.map((modelName) => {
            const modelData = latencyData.filter(d => d.modelName === modelName);
            const modelAvg = modelData.reduce((sum, d) => sum + d.latency, 0) / (modelData.length || 1);
            const status = getLatencyStatus(modelAvg);

            return (
              <div key={modelName} className="border rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <p className="font-semibold">{modelName}</p>
                  <div className="flex items-center gap-2">
                    <p className="font-bold">{modelAvg.toFixed(0)}ms</p>
                    <span className={`px-2 py-1 rounded text-xs bg-${status.color}-100 text-${status.color}-700`}>
                      {status.label}
                    </span>
                  </div>
                </div>
                <div className="mt-2 flex gap-4 text-sm text-gray-600">
                  <span>P50: {modelData[modelData.length - 1]?.p50.toFixed(0) || 0}ms</span>
                  <span>P95: {modelData[modelData.length - 1]?.p95.toFixed(0) || 0}ms</span>
                  <span>P99: {modelData[modelData.length - 1]?.p99.toFixed(0) || 0}ms</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Alerts */}
      {recentLatency && recentLatency.latency > 1000 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="font-semibold text-red-800">⚠️ High Latency Alert</h4>
          <p className="text-sm text-red-700">
            Current latency ({recentLatency.latency.toFixed(0)}ms) exceeds threshold (1000ms)
          </p>
        </div>
      )}
    </div>
  );
}
