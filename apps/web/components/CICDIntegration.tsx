import React, { useState, useEffect } from 'react';

interface Pipeline {
  id: string;
  name: string;
  provider: 'github' | 'gitlab' | 'jenkins';
  repository: string;
  branch: string;
  status: 'active' | 'inactive' | 'error';
  lastRun: Date;
  lastRunStatus: 'success' | 'failed' | 'running';
  triggerOn: string[];
}

interface CICDIntegrationProps {
  userId: string;
}

export function CICDIntegration({ userId }: CICDIntegrationProps) {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPipeline, setNewPipeline] = useState({
    name: '',
    provider: 'github' as const,
    repository: '',
    branch: 'main',
    triggerOn: ['push'],
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchPipelines();
  }, [userId]);

  const fetchPipelines = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/ci-cd-pipelines`);
      if (response.ok) {
        const data = await response.json();
        setPipelines(data);
      }
    } catch (error) {
      console.error('Failed to fetch pipelines:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createPipeline = async () => {
    try {
      const response = await fetch('/api/ci-cd-pipelines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newPipeline,
          userId,
        }),
      });

      if (response.ok) {
        const pipeline = await response.json();
        setPipelines(prev => [...prev, pipeline]);
        setShowCreateModal(false);
        setNewPipeline({
          name: '',
          provider: 'github',
          repository: '',
          branch: 'main',
          triggerOn: ['push'],
        });
      }
    } catch (error) {
      console.error('Failed to create pipeline:', error);
    }
  };

  const triggerPipeline = async (pipelineId: string) => {
    try {
      const response = await fetch(`/api/ci-cd-pipelines/${pipelineId}/trigger`, {
        method: 'POST',
      });

      if (response.ok) {
        setPipelines(prev =>
          prev.map(p =>
            p.id === pipelineId ? { ...p, lastRunStatus: 'running' } : p
          )
        );
      }
    } catch (error) {
      console.error('Failed to trigger pipeline:', error);
    }
  };

  const deletePipeline = async (pipelineId: string) => {
    try {
      const response = await fetch(`/api/ci-cd-pipelines/${pipelineId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setPipelines(prev => prev.filter(p => p.id !== pipelineId));
      }
    } catch (error) {
      console.error('Failed to delete pipeline:', error);
    }
  };

  const toggleTrigger = (trigger: string) => {
    setNewPipeline(prev => ({
      ...prev,
      triggerOn: prev.triggerOn.includes(trigger)
        ? prev.triggerOn.filter(t => t !== trigger)
        : [...prev.triggerOn, trigger],
    }));
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-700',
      inactive: 'bg-gray-100 text-gray-700',
      error: 'bg-red-100 text-red-700',
      success: 'text-green-600',
      failed: 'text-red-600',
      running: 'text-blue-600',
    };
    return colors[status] || colors.inactive;
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      github: '🐙',
      gitlab: '🦊',
      jenkins: '⚙️',
    };
    return icons[provider] || '📦';
  };

  if (isLoading) return <div>Loading CI/CD pipelines...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">CI/CD Integration</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          + Add Pipeline
        </button>
      </div>

      {/* Pipeline List */}
      <div className="space-y-4">
        {pipelines.map((pipeline) => (
          <div key={pipeline.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getProviderIcon(pipeline.provider)}</span>
                <div>
                  <h3 className="font-semibold">{pipeline.name}</h3>
                  <p className="text-sm text-gray-600">{pipeline.repository}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${getStatusColor(pipeline.status)}`}>
                  {pipeline.status}
                </span>
                <span className={`text-sm ${getStatusColor(pipeline.lastRunStatus)}`}>
                  {pipeline.lastRunStatus}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm mb-4">
              <div>
                <p className="text-gray-600">Branch</p>
                <p className="font-medium">{pipeline.branch}</p>
              </div>
              <div>
                <p className="text-gray-600">Last Run</p>
                <p className="font-medium">{new Date(pipeline.lastRun).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Triggers</p>
                <p className="font-medium">{pipeline.triggerOn.join(', ')}</p>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => triggerPipeline(pipeline.id)}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
              >
                Run Now
              </button>
              <button className="px-3 py-1 bg-gray-200 rounded text-sm">
                View Logs
              </button>
              <button className="px-3 py-1 bg-gray-200 rounded text-sm">
                Configure
              </button>
              <button
                onClick={() => deletePipeline(pipeline.id)}
                className="px-3 py-1 border border-red-500 text-red-500 rounded text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Pipeline Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Add CI/CD Pipeline</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Pipeline Name</label>
                <input
                  type="text"
                  value={newPipeline.name}
                  onChange={(e) => setNewPipeline(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., Production Eval"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Provider</label>
                <select
                  value={newPipeline.provider}
                  onChange={(e) => setNewPipeline(prev => ({ ...prev, provider: e.target.value as any }))}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="github">GitHub Actions</option>
                  <option value="gitlab">GitLab CI</option>
                  <option value="jenkins">Jenkins</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Repository</label>
                <input
                  type="text"
                  value={newPipeline.repository}
                  onChange={(e) => setNewPipeline(prev => ({ ...prev, repository: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                  placeholder="owner/repo"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Branch</label>
                <input
                  type="text"
                  value={newPipeline.branch}
                  onChange={(e) => setNewPipeline(prev => ({ ...prev, branch: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                  placeholder="main"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Trigger On</label>
                <div className="space-y-2">
                  {['push', 'pull_request', 'schedule'].map((trigger) => (
                    <label key={trigger} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newPipeline.triggerOn.includes(trigger)}
                        onChange={() => toggleTrigger(trigger)}
                      />
                      <span className="text-sm capitalize">{trigger.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 rounded"
              >
                Cancel
              </button>
              <button
                onClick={createPipeline}
                disabled={!newPipeline.name || !newPipeline.repository}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
              >
                Add Pipeline
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Integration Guide */}
      <div className="border rounded-lg p-4 bg-blue-50">
        <h3 className="font-semibold text-blue-800 mb-2">Integration Guide</h3>
        <p className="text-sm text-blue-700 mb-3">
          Add this workflow to your repository to enable automated model evaluation:
        </p>
        <pre className="bg-white p-3 rounded text-xs overflow-x-auto">
          <code>{`.github/workflows/llm-eval.yml
name: LLM Evaluation
on: [push, pull_request]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          curl -X POST ${{ secrets.EVAL_API_URL }} \\
            -H "Authorization: Bearer ${{ secrets.EVAL_API_KEY }}" \\
            -d '{"commit": "${{ github.sha }}"}'`}</code>
        </pre>
      </div>
    </div>
  );
}
