import React, { useState, useEffect } from 'react';

interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: string[];
  category: string;
  createdAt: Date;
  usageCount: number;
}

interface PromptTemplatesProps {
  userId: string;
}

export function PromptTemplates({ userId }: PromptTemplatesProps) {
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  const categories = ['all', 'classification', 'summarization', 'extraction', 'generation', 'qa'];

  useEffect(() => {
    fetchTemplates();
  }, [userId]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`/api/users/${userId}/prompt-templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveTemplate = async (template: Partial<PromptTemplate>) => {
    try {
      const response = await fetch('/api/prompt-templates', {
        method: template.id ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...template, userId }),
      });

      if (response.ok) {
        const saved = await response.json();
        if (template.id) {
          setTemplates(prev => prev.map(t => t.id === template.id ? saved : t));
        } else {
          setTemplates(prev => [saved, ...prev]);
        }
        setShowCreateModal(false);
        setSelectedTemplate(null);
      }
    } catch (error) {
      console.error('Failed to save template:', error);
    }
  };

  const deleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`/api/prompt-templates/${templateId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== templateId));
      }
    } catch (error) {
      console.error('Failed to delete template:', error);
    }
  };

  const extractVariables = (template: string) => {
    const matches = template.match(/\{\{(\w+)\}\}/g) || [];
    return matches.map(m => m.replace(/[{}]/g, ''));
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (isLoading) return <div>Loading templates...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Prompt Templates</h2>
        <button
          onClick={() => {
            setSelectedTemplate(null);
            setShowCreateModal(true);
          }}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          + New Template
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search templates..."
          className="flex-1 border rounded px-3 py-2"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="border rounded px-3 py-2"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTemplates.map((template) => (
          <div key={template.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold">{template.name}</h3>
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                {template.category}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
            <div className="flex gap-2 mb-3">
              {template.variables.slice(0, 3).map((variable) => (
                <span key={variable} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {variable}
                </span>
              ))}
              {template.variables.length > 3 && (
                <span className="text-xs text-gray-500">+{template.variables.length - 3}</span>
              )}
            </div>
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>{template.usageCount} uses</span>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedTemplate(template);
                    setShowCreateModal(true);
                  }}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Edit
                </button>
                <button
                  onClick={() => deleteTemplate(template.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">
              {selectedTemplate ? 'Edit Template' : 'Create Template'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  defaultValue={selectedTemplate?.name}
                  id="template-name"
                  className="w-full border rounded px-3 py-2"
                  placeholder="Template name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  defaultValue={selectedTemplate?.description}
                  id="template-description"
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                  placeholder="Brief description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <select
                  defaultValue={selectedTemplate?.category || 'classification'}
                  id="template-category"
                  className="w-full border rounded px-3 py-2"
                >
                  {categories.filter(c => c !== 'all').map(cat => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Template</label>
                <textarea
                  defaultValue={selectedTemplate?.template}
                  id="template-content"
                  className="w-full border rounded px-3 py-2 font-mono text-sm"
                  rows={8}
                  placeholder="Use {{variable}} for dynamic values"
                  onChange={(e) => {
                    const vars = extractVariables(e.target.value);
                    // Could update a variables display
                  }}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use {'{{variable}}'} syntax for dynamic values
                </p>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setSelectedTemplate(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-200 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const name = (document.getElementById('template-name') as HTMLInputElement)?.value;
                  const description = (document.getElementById('template-description') as HTMLTextAreaElement)?.value;
                  const category = (document.getElementById('template-category') as HTMLSelectElement)?.value;
                  const template = (document.getElementById('template-content') as HTMLTextAreaElement)?.value;
                  
                  saveTemplate({
                    id: selectedTemplate?.id,
                    name,
                    description,
                    category,
                    template,
                    variables: extractVariables(template),
                  });
                }}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
