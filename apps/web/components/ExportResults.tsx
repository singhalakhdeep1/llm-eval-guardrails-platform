import React, { useState, useEffect } from 'react';

interface EvaluationResult {
  id: string;
  evaluationId: string;
  evaluationName: string;
  modelId: string;
  modelName: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
    latency: number;
  };
  timestamp: Date;
}

interface ExportResultsProps {
  userId: string;
}

export function ExportResults({ userId }: ExportResultsProps) {
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [selectedResults, setSelectedResults] = useState<string[]>([]);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'pdf'>('csv');
  const [isExporting, setIsExporting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchResults();
  }, [userId]);

  const fetchResults = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/evaluation-results`);
      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch (error) {
      console.error('Failed to fetch results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleResultSelection = (resultId: string) => {
    setSelectedResults(prev =>
      prev.includes(resultId)
        ? prev.filter(id => id !== resultId)
        : [...prev, resultId]
    );
  };

  const selectAll = () => {
    setSelectedResults(results.map(r => r.id));
  };

  const clearSelection = () => {
    setSelectedResults([]);
  };

  const exportResults = async () => {
    if (selectedResults.length === 0) return;

    setIsExporting(true);
    try {
      const response = await fetch('/api/export/results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resultIds: selectedResults,
          format: exportFormat,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evaluation-results.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export results:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const generateReport = async () => {
    if (selectedResults.length === 0) return;

    setIsExporting(true);
    try {
      const response = await fetch('/api/export/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resultIds: selectedResults,
          userId,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'evaluation-report.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) return <div>Loading results...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Export Results</h2>

      {/* Selection Controls */}
      <div className="flex justify-between items-center bg-gray-50 p-4 rounded-lg">
        <div className="flex gap-2">
          <button
            onClick={selectAll}
            className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-100"
          >
            Select All
          </button>
          <button
            onClick={clearSelection}
            className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-100"
          >
            Clear Selection
          </button>
          <span className="text-sm text-gray-600 self-center">
            {selectedResults.length} selected
          </span>
        </div>

        <div className="flex gap-2">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as any)}
            className="border rounded px-3 py-1 text-sm"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="pdf">PDF</option>
          </select>

          <button
            onClick={exportResults}
            disabled={selectedResults.length === 0 || isExporting}
            className="px-4 py-1 bg-blue-500 text-white rounded text-sm disabled:bg-gray-300"
          >
            {isExporting ? 'Exporting...' : 'Export'}
          </button>

          <button
            onClick={generateReport}
            disabled={selectedResults.length === 0 || isExporting}
            className="px-4 py-1 bg-green-500 text-white rounded text-sm disabled:bg-gray-300"
          >
            Generate Report
          </button>
        </div>
      </div>

      {/* Results List */}
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 w-10">
                <input
                  type="checkbox"
                  checked={selectedResults.length === results.length && results.length > 0}
                  onChange={selectedResults.length === results.length ? clearSelection : selectAll}
                />
              </th>
              <th className="px-4 py-3 text-left font-semibold">Evaluation</th>
              <th className="px-4 py-3 text-left font-semibold">Model</th>
              <th className="px-4 py-3 text-left font-semibold">Accuracy</th>
              <th className="px-4 py-3 text-left font-semibold">F1 Score</th>
              <th className="px-4 py-3 text-left font-semibold">Latency</th>
              <th className="px-4 py-3 text-left font-semibold">Date</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => (
              <tr key={result.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedResults.includes(result.id)}
                    onChange={() => toggleResultSelection(result.id)}
                  />
                </td>
                <td className="px-4 py-3 font-medium">{result.evaluationName}</td>
                <td className="px-4 py-3">{result.modelName}</td>
                <td className="px-4 py-3">{(result.metrics.accuracy * 100).toFixed(1)}%</td>
                <td className="px-4 py-3">{result.metrics.f1Score.toFixed(3)}</td>
                <td className="px-4 py-3">{result.metrics.latency.toFixed(0)}ms</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {new Date(result.timestamp).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Export Options */}
      <div className="border rounded-lg p-4">
        <h3 className="font-semibold mb-3">Export Options</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked />
              <span className="text-sm">Include raw data</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked />
              <span className="text-sm">Include metrics</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" />
              <span className="text-sm">Include model parameters</span>
            </label>
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked />
              <span className="text-sm">Include timestamps</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" />
              <span className="text-sm">Include error analysis</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" />
              <span className="text-sm">Include visualizations</span>
            </label>
          </div>
        </div>
      </div>

      {/* Scheduled Exports */}
      <div className="border rounded-lg p-4">
        <h3 className="font-semibold mb-3">Scheduled Exports</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <div>
              <p className="font-medium">Daily Summary</p>
              <p className="text-sm text-gray-600">Every day at 9:00 AM</p>
            </div>
            <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <div>
              <p className="font-medium">Weekly Report</p>
              <p className="text-sm text-gray-600">Every Monday at 8:00 AM</p>
            </div>
            <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
          </div>
        </div>
        <button className="mt-3 text-blue-600 hover:text-blue-800 text-sm">
          + Add Schedule
        </button>
      </div>
    </div>
  );
}
