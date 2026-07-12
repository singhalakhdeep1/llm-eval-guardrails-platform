import React, { useState, useEffect } from 'react';

interface TestVariant {
  id: string;
  name: string;
  modelId: string;
  modelName: string;
  metrics: {
    accuracy: number;
    latency: number;
    userSatisfaction: number;
  };
  sampleSize: number;
}

interface ABTest {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'paused';
  createdAt: Date;
  variants: TestVariant[];
  winner?: string;
  confidence: number;
}

interface ABTestingProps {
  userId: string;
}

export function ABTesting({ userId }: ABTestingProps) {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTestName, setNewTestName] = useState('');
  const [selectedVariants, setSelectedVariants] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [availableModels] = useState([
    { id: '1', name: 'GPT-4' },
    { id: '2', name: 'Claude 3' },
    { id: '3', name: 'Llama 2' },
    { id: '4', name: 'Mistral' },
  ]);

  useEffect(() => {
    fetchTests();
  }, [userId]);

  const fetchTests = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/ab-tests`);
      if (response.ok) {
        const data = await response.json();
        setTests(data);
      }
    } catch (error) {
      console.error('Failed to fetch A/B tests:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createTest = async () => {
    if (!newTestName || selectedVariants.length < 2) return;

    const variants = selectedVariants.map((modelId, idx) => ({
      id: `variant-${idx}`,
      name: `Variant ${String.fromCharCode(65 + idx)}`,
      modelId,
      modelName: availableModels.find(m => m.id === modelId)?.name || 'Unknown',
      metrics: { accuracy: 0, latency: 0, userSatisfaction: 0 },
      sampleSize: 0,
    }));

    try {
      const response = await fetch('/api/ab-tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newTestName,
          userId,
          variants,
        }),
      });

      if (response.ok) {
        const newTest = await response.json();
        setTests(prev => [newTest, ...prev]);
        setShowCreateModal(false);
        setNewTestName('');
        setSelectedVariants([]);
      }
    } catch (error) {
      console.error('Failed to create test:', error);
    }
  };

  const pauseTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/ab-tests/${testId}/pause`, {
        method: 'POST',
      });

      if (response.ok) {
        setTests(prev =>
          prev.map(test =>
            test.id === testId ? { ...test, status: 'paused' } : test
          )
        );
      }
    } catch (error) {
      console.error('Failed to pause test:', error);
    }
  };

  const resumeTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/ab-tests/${testId}/resume`, {
        method: 'POST',
      });

      if (response.ok) {
        setTests(prev =>
          prev.map(test =>
            test.id === testId ? { ...test, status: 'running' } : test
          )
        );
      }
    } catch (error) {
      console.error('Failed to resume test:', error);
    }
  };

  const toggleVariantSelection = (modelId: string) => {
    setSelectedVariants(prev =>
      prev.includes(modelId)
        ? prev.filter(id => id !== modelId)
        : [...prev, modelId].slice(0, 4)
    );
  };

  if (isLoading) return <div>Loading A/B tests...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">A/B Testing</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          + New Test
        </button>
      </div>

      {/* Test List */}
      <div className="space-y-4">
        {tests.map((test) => (
          <div key={test.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold">{test.name}</h3>
                <p className="text-sm text-gray-600">
                  Created {new Date(test.createdAt).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  test.status === 'running' ? 'bg-green-100 text-green-700' :
                  test.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {test.status}
                </span>
                {test.status === 'running' && (
                  <button
                    onClick={() => pauseTest(test.id)}
                    className="text-sm text-gray-600 hover:text-gray-800"
                  >
                    Pause
                  </button>
                )}
                {test.status === 'paused' && (
                  <button
                    onClick={() => resumeTest(test.id)}
                    className="text-sm text-gray-600 hover:text-gray-800"
                  >
                    Resume
                  </button>
                )}
              </div>
            </div>

            {/* Variants Comparison */}
            <div className="space-y-3">
              {test.variants.map((variant) => (
                <div key={variant.id} className="bg-gray-50 rounded p-3">
                  <div className="flex justify-between items-center mb-2">
                    <p className="font-medium">{variant.name} - {variant.modelName}</p>
                    {test.winner === variant.id && (
                      <span className="text-green-600 font-semibold">🏆 Winner</span>
                    )}
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Accuracy</p>
                      <p className="font-semibold">{(variant.metrics.accuracy * 100).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Latency</p>
                      <p className="font-semibold">{variant.metrics.latency.toFixed(0)}ms</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Satisfaction</p>
                      <p className="font-semibold">{variant.metrics.userSatisfaction.toFixed(1)}/5</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Samples</p>
                      <p className="font-semibold">{variant.sampleSize}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {test.status === 'completed' && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  Statistical Confidence: {(test.confidence * 100).toFixed(1)}%
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Test Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Create A/B Test</h3>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Test Name</label>
              <input
                type="text"
                value={newTestName}
                onChange={(e) => setNewTestName(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., Model Comparison Test"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Select Models (2-4)</label>
              <div className="space-y-2">
                {availableModels.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => toggleVariantSelection(model.id)}
                    className={`w-full p-3 rounded border-2 text-left ${
                      selectedVariants.includes(model.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    {model.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 rounded"
              >
                Cancel
              </button>
              <button
                onClick={createTest}
                disabled={!newTestName || selectedVariants.length < 2}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
              >
                Create Test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
