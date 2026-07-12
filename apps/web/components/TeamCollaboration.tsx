import React, { useState, useEffect } from 'react';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joinedAt: Date;
}

interface Evaluation {
  id: string;
  name: string;
  createdBy: string;
  createdAt: Date;
  collaborators: string[];
}

interface TeamCollaborationProps {
  userId: string;
}

export function TeamCollaboration({ userId }: TeamCollaborationProps) {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'member' | 'viewer'>('member');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTeamData();
  }, [userId]);

  const fetchTeamData = async () => {
    try {
      const [membersRes, evalsRes] = await Promise.all([
        fetch(`/api/users/${userId}/team`),
        fetch(`/api/users/${userId}/shared-evaluations`),
      ]);

      if (membersRes.ok) setMembers(await membersRes.json());
      if (evalsRes.ok) setEvaluations(await evalsRes.json());
    } catch (error) {
      console.error('Failed to fetch team data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const inviteMember = async () => {
    if (!inviteEmail) return;

    try {
      const response = await fetch('/api/team/invite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: inviteEmail,
          role: inviteRole,
          invitedBy: userId,
        }),
      });

      if (response.ok) {
        const newMember = await response.json();
        setMembers(prev => [...prev, newMember]);
        setShowInviteModal(false);
        setInviteEmail('');
      }
    } catch (error) {
      console.error('Failed to invite member:', error);
    }
  };

  const updateMemberRole = async (memberId: string, newRole: string) => {
    try {
      const response = await fetch(`/api/team/members/${memberId}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      });

      if (response.ok) {
        setMembers(prev =>
          prev.map(member =>
            member.id === memberId ? { ...member, role: newRole as any } : member
          )
        );
      }
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const removeMember = async (memberId: string) => {
    try {
      const response = await fetch(`/api/team/members/${memberId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setMembers(prev => prev.filter(member => member.id !== memberId));
      }
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  const shareEvaluation = async (evaluationId: string, memberIds: string[]) => {
    try {
      const response = await fetch(`/api/evaluations/${evaluationId}/share`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ memberIds }),
      });

      if (response.ok) {
        setEvaluations(prev =>
          prev.map(eval =>
            eval.id === evaluationId
              ? { ...eval, collaborators: memberIds }
              : eval
          )
        );
      }
    } catch (error) {
      console.error('Failed to share evaluation:', error);
    }
  };

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      owner: 'bg-purple-100 text-purple-700',
      admin: 'bg-blue-100 text-blue-700',
      member: 'bg-green-100 text-green-700',
      viewer: 'bg-gray-100 text-gray-700',
    };
    return colors[role] || colors.viewer;
  };

  if (isLoading) return <div>Loading team data...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Team Collaboration</h2>
        <button
          onClick={() => setShowInviteModal(true)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          + Invite Member
        </button>
      </div>

      {/* Team Members */}
      <div>
        <h3 className="font-semibold mb-3">Team Members ({members.length})</h3>
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Name</th>
                <th className="px-4 py-3 text-left font-semibold">Email</th>
                <th className="px-4 py-3 text-left font-semibold">Role</th>
                <th className="px-4 py-3 text-left font-semibold">Joined</th>
                <th className="px-4 py-3 text-left font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id} className="border-t">
                  <td className="px-4 py-3">{member.name}</td>
                  <td className="px-4 py-3">{member.email}</td>
                  <td className="px-4 py-3">
                    <select
                      value={member.role}
                      onChange={(e) => updateMemberRole(member.id, e.target.value)}
                      disabled={member.role === 'owner'}
                      className={`px-2 py-1 rounded text-xs ${getRoleColor(member.role)} border-0`}
                    >
                      <option value="owner">Owner</option>
                      <option value="admin">Admin</option>
                      <option value="member">Member</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {new Date(member.joinedAt).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {member.role !== 'owner' && (
                      <button
                        onClick={() => removeMember(member.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Shared Evaluations */}
      <div>
        <h3 className="font-semibold mb-3">Shared Evaluations</h3>
        <div className="space-y-3">
          {evaluations.map((evaluation) => (
            <div key={evaluation.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold">{evaluation.name}</h4>
                  <p className="text-sm text-gray-600">
                    Created by {evaluation.collaborators.length} collaborators
                  </p>
                </div>
                <button className="text-blue-600 hover:text-blue-800 text-sm">
                  Manage Access
                </button>
              </div>
              <div className="flex gap-2">
                {evaluation.collaborators.slice(0, 3).map((collabId) => {
                  const member = members.find(m => m.id === collabId);
                  return member ? (
                    <span key={collabId} className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {member.name}
                    </span>
                  ) : null;
                })}
                {evaluation.collaborators.length > 3 && (
                  <span className="text-xs text-gray-500">
                    +{evaluation.collaborators.length - 3} more
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Invite Team Member</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  placeholder="colleague@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as any)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="member">Member</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 rounded"
              >
                Cancel
              </button>
              <button
                onClick={inviteMember}
                disabled={!inviteEmail}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
              >
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
