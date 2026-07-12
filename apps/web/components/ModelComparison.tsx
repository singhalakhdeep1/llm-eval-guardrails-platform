import React, { useState, useEffect } from 'react';

interface ModelMetrics {
  accuracy: number;
  latency: number;
  costPer1kTokens: number;
  throughput: number;
}

interface Model {
  id: string;
  name: string;
  provider: string;
  metrics: ModelMetrics;
}

interface ModelComparisonProps {
  userId: string;
}

export function ModelComparison({ userId }: ModelComparisonProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [comparisonResults, setComparisonResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/models');
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleModelSelection = (modelId: string) => {
    setSelectedModels(prev =>
      prev.includes(modelId)
        ? prev.filter(id => id !== modelId)
        : [...prev, modelId].slice(0, 4)
    );
  };

  const runComparison = async () => {
    if (selectedModels.length < 2) return;

    try {
      const response = await fetch('/api/compare-models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modelIds: selectedModels }),
      });

      if (response.ok) {
        const results = await response.json();
        setComparisonResults(results);
      }
    } catch (error) {
      console.error('Failed to run comparison:', error);
    }
  };

  const getMetricColor = (value: number, isHigherBetter: boolean) => {
    if (isHigherBetter) {
      return value > 0.8 ? 'text-green-600' : value > 0.5 ? 'text-yellow-600' : 'text-red-600';
    }
    return value < 0.5 ? 'text-green-600' : value < 1.0 ? 'text-yellow-600' : 'text-red-600';
  };

  if (isLoading) return <div>Loading models...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Model Comparison</h2>

      {/* Model Selection */}
      <div>
        <h3 className="font-semibold mb-3">Select Models to Compare (max 4)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => toggleModelSelection(model.id)}
              className={`p-4 rounded-lg border-2 text-left ${
                selectedModels.includes(model.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-semibold">{model.name}</p>
              <p className="text-sm text-gray-600">{model.provider}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Compare Button */}
      {selectedModels.length >= 2 && (
        <button
          onClick={runComparison}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg"
        >
          Compare Selected Models
        </button>
      )}

      {/* Comparison Results */}
      {comparisonResults && (
        <div className="space-y-6">
          <h3 className="font-semibold text-lg">Comparison Results</h3>

          {/* Metrics Table */}
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">Metric</th>
                  {selectedModels.map((modelId) => {
                    const model = models.find(m => m.id === modelId);
                    return (
                      <th key={modelId} className="px-4 py-3 text-left font-semibold">
                        {model?.name}
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                <tr className="border-t">
                  <td className="px-4 py-3 font-medium">Accuracy</td>
                  {selectedModels.map((modelId) => {
                    const model = models.find(m => m.id === modelId);
                    return (
                      <td key={modelId} className={`px-4 py-3 ${getMetricColor(model?.metrics.accuracy || 0, true)}`}>
                        {((model?.metrics.accuracy || 0) * 100).toFixed(1)}%
                      </td>
                    );
                  })}
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3 font-medium">Latency (ms)</td>
                  {selectedModels.map((modelId) => {
                    const model = models.find(m => m.id === modelId);
                    return (
                      <td key={modelId} className={`px-4 py-3 ${getMetricColor(model?.metrics.latency || 0, false)}`}>
                        {model?.metrics.latency.toFixed(0)}ms
                      </td>
                    );
                  })}
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3 font-medium">Cost / 1K Tokens</td>
                  {selectedModels.map((modelId) => {
                    const model = models.find(m => m.id === modelId);
                    return (
                      <td key={modelId} className={`px-4 py-3 ${getMetricColor(model?.metrics.costPer1kTokens || 0, false)}`}>
                        ${model?.metrics.costPer1kTokens.toFixed(4)}
                      </td>
                    );
                  })}
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3 font-medium">Throughput (req/s)</td>
                  {selectedModels.map((modelId) => {
                    const model = models.find(m => m.id === modelId);
                    return (
                      <td key={modelId} className={`px-4 py-3 ${getMetricColor(model?.metrics.throughput || 0, true)}`}>
                        {model?.metrics.throughput.toFixed(1)}
                      </td>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Recommendations */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">Recommendations</h4>
            <ul className="space-y-1 text-sm text-blue-700">
              <li>• Best Accuracy: {models.find(m => m.id === selectedModels[0])?.name}</li>
              <li>• Lowest Latency: {models.find(m => m.id === selectedModels[0])?.name}</li>
              <li>• Most Cost-Effective: {models.find(m => m.id === selectedModels[0])?.name}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
