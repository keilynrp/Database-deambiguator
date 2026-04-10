"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "@/lib/api";

interface Organization {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  plan: string;
  benchmark_profile_id: string | null;
  owner_id: number;
  is_active: boolean;
  member_count: number;
  created_at: string;
}

interface BenchmarkProfile {
  id: string;
  name: string;
  description: string;
  region: string;
  rules_count: number;
  is_default: boolean;
}

interface Member {
  user_id: number;
  org_id: number;
  role: string;
  username: string;
  display_name: string;
  joined_at: string;
}

function PlanBadge({ plan }: { plan: string }) {
  const colors: Record<string, string> = {
    free: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
    pro: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400",
    enterprise: "bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-400",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${colors[plan] ?? colors.free}`}>
      {plan}
    </span>
  );
}

export default function OrganizationsPage() {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showInvite, setShowInvite] = useState(false);
  const [form, setForm] = useState({ name: "", slug: "", description: "", plan: "free" });
  const [inviteForm, setInviteForm] = useState({ username: "", role: "member" });
  const [benchmarkProfiles, setBenchmarkProfiles] = useState<BenchmarkProfile[]>([]);
  const [savingBenchmark, setSavingBenchmark] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadOrgs = useCallback(async () => {
    setLoading(true);
    const r = await apiFetch("/organizations");
    if (r.ok) setOrgs(await r.json());
    setLoading(false);
  }, []);

  const loadMembers = useCallback(async (orgId: number) => {
    const r = await apiFetch(`/organizations/${orgId}/members`);
    if (r.ok) setMembers(await r.json());
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      const r = await apiFetch("/organizations");
      if (!active) {
        return;
      }
      if (r.ok) {
        setOrgs(await r.json());
      }
      setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      const r = await apiFetch("/analytics/benchmarks/profiles");
      if (active && r.ok) {
        setBenchmarkProfiles(await r.json());
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedOrg) {
      return;
    }

    let active = true;
    (async () => {
      const r = await apiFetch(`/organizations/${selectedOrg.id}/members`);
      if (active && r.ok) {
        setMembers(await r.json());
      }
    })();

    return () => {
      active = false;
    };
  }, [selectedOrg]);

  async function createOrg() {
    setSaving(true);
    setError(null);
    const r = await apiFetch("/organizations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    if (r.ok) {
      setShowCreate(false);
      setForm({ name: "", slug: "", description: "", plan: "free" });
      loadOrgs();
    } else {
      const d = await r.json().catch(() => ({}));
      setError(d.detail ?? "Failed to create organization");
    }
    setSaving(false);
  }

  async function inviteMember() {
    if (!selectedOrg) return;
    setSaving(true);
    setError(null);
    const r = await apiFetch(`/organizations/${selectedOrg.id}/members`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inviteForm),
    });
    if (r.ok) {
      setShowInvite(false);
      setInviteForm({ username: "", role: "member" });
      loadMembers(selectedOrg.id);
    } else {
      const d = await r.json().catch(() => ({}));
      setError(d.detail ?? "Failed to invite member");
    }
    setSaving(false);
  }

  async function removeMember(userId: number) {
    if (!selectedOrg || !confirm("Remove this member?")) return;
    await apiFetch(`/organizations/${selectedOrg.id}/members/${userId}`, { method: "DELETE" });
    loadMembers(selectedOrg.id);
  }

  async function switchOrg(orgId: number) {
    await apiFetch(`/organizations/${orgId}/switch`, { method: "POST" });
    window.location.reload();
  }

  async function deleteOrg(orgId: number) {
    if (!confirm("Delete this organization? This cannot be undone.")) return;
    await apiFetch(`/organizations/${orgId}`, { method: "DELETE" });
    setSelectedOrg(null);
    loadOrgs();
  }

  async function saveBenchmarkProfile(benchmarkProfileId: string) {
    if (!selectedOrg) return;
    setSavingBenchmark(true);
    setError(null);
    const r = await apiFetch(`/organizations/${selectedOrg.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ benchmark_profile_id: benchmarkProfileId }),
    });
    if (r.ok) {
      const updated = await r.json();
      setSelectedOrg(updated);
      setOrgs((prev) => prev.map((org) => (org.id === updated.id ? updated : org)));
      const profilesResponse = await apiFetch("/analytics/benchmarks/profiles");
      if (profilesResponse.ok) {
        setBenchmarkProfiles(await profilesResponse.json());
      }
    } else {
      const d = await r.json().catch(() => ({}));
      setError(d.detail ?? "Failed to save benchmark profile");
    }
    setSavingBenchmark(false);
  }

  const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Organizations</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Manage multi-tenant workspaces and member access</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
        >
          <span>+</span> New Organization
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/30 dark:bg-red-900/10 dark:text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Org list */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Your Organizations</h2>
          {loading ? (
            <div className="animate-pulse space-y-2">
              {[1, 2].map(i => <div key={i} className="h-20 rounded-xl bg-gray-100 dark:bg-gray-800" />)}
            </div>
          ) : orgs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-gray-200 p-8 text-center dark:border-gray-700">
              <p className="text-sm text-gray-500">No organizations yet.</p>
            </div>
          ) : (
            orgs.map(org => (
              <div
                key={org.id}
                onClick={() => setSelectedOrg(org)}
                className={`cursor-pointer rounded-xl border p-4 transition-all ${
                  selectedOrg?.id === org.id
                    ? "border-blue-300 bg-blue-50 shadow-sm dark:border-blue-700 dark:bg-blue-950/20"
                    : "border-gray-200 bg-white hover:border-gray-300 dark:border-gray-800 dark:bg-gray-900"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900 dark:text-white">{org.name}</span>
                      <PlanBadge plan={org.plan} />
                    </div>
                    <div className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">/{org.slug} · {org.member_count} member{org.member_count !== 1 ? "s" : ""}</div>
                  </div>
                </div>
                {org.description && (
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{org.description}</p>
                )}
              </div>
            ))
          )}
        </div>

        {/* Org detail */}
        <div className="lg:col-span-2">
          {!selectedOrg ? (
            <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-400">Select an organization to manage it</p>
            </div>
          ) : (
            <div className="space-y-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{selectedOrg.name}</h3>
                  <div className="mt-1 flex items-center gap-3">
                    <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">/{selectedOrg.slug}</code>
                    <PlanBadge plan={selectedOrg.plan} />
                  </div>
                  {selectedOrg.description && (
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{selectedOrg.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => switchOrg(selectedOrg.id)}
                    className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100 dark:border-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
                  >
                    Switch to this org
                  </button>
                  <button
                    onClick={() => deleteOrg(selectedOrg.id)}
                    className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 dark:border-red-900/30 dark:bg-red-900/10 dark:text-red-400"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {/* Members */}
              <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Benchmark Profile</h4>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Choose the default institutional benchmark profile for this tenant.
                    </p>
                  </div>
                  <div className="min-w-[260px]">
                    <select
                      value={selectedOrg.benchmark_profile_id ?? ""}
                      onChange={(e) => saveBenchmarkProfile(e.target.value)}
                      disabled={savingBenchmark}
                      className={inputClass}
                    >
                      {benchmarkProfiles.map((profile) => (
                        <option key={profile.id} value={profile.id}>
                          {profile.name}
                        </option>
                      ))}
                    </select>
                    {selectedOrg.benchmark_profile_id && (
                      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {benchmarkProfiles.find((profile) => profile.id === selectedOrg.benchmark_profile_id)?.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Members */}
              <div>
                <div className="mb-3 flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Members ({members.length})</h4>
                  <button
                    onClick={() => setShowInvite(true)}
                    className="rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  >
                    + Invite
                  </button>
                </div>
                <div className="divide-y divide-gray-100 overflow-hidden rounded-xl border border-gray-100 dark:divide-gray-800 dark:border-gray-800">
                  {members.map(m => (
                    <div key={m.user_id} className="flex items-center justify-between px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                          {m.username.slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">{m.display_name}</div>
                          <div className="text-xs text-gray-500">@{m.username}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
                          m.role === "owner" ? "bg-amber-100 text-amber-700" :
                          m.role === "admin" ? "bg-blue-100 text-blue-700" :
                          "bg-gray-100 text-gray-600"
                        }`}>{m.role}</span>
                        {m.role !== "owner" && (
                          <button
                            onClick={() => removeMember(m.user_id)}
                            className="rounded p-1 text-gray-400 hover:text-red-500"
                            title="Remove"
                          >
                            <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create org modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-900">
            <h3 className="mb-4 text-lg font-bold text-gray-900 dark:text-white">New Organization</h3>
            <div className="space-y-3">
              <input placeholder="Organization name" value={form.name} onChange={e => setForm({...form, name: e.target.value, slug: e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")})} className={inputClass} />
              <input placeholder="Slug (e.g. my-org)" value={form.slug} onChange={e => setForm({...form, slug: e.target.value})} className={inputClass} />
              <textarea placeholder="Description (optional)" value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={2} className="w-full resize-none rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white" />
              <select value={form.plan} onChange={e => setForm({...form, plan: e.target.value})} className={inputClass}>
                <option value="free">Free</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
            <div className="mt-4 flex gap-2">
              <button onClick={createOrg} disabled={saving || !form.name || !form.slug} className="flex-1 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50 hover:bg-blue-700">
                {saving ? "Creating…" : "Create"}
              </button>
              <button onClick={() => { setShowCreate(false); setError(null); }} className="flex-1 rounded-xl border border-gray-200 py-2.5 text-sm font-semibold text-gray-700 dark:border-gray-700 dark:text-gray-300">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite modal */}
      {showInvite && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-900">
            <h3 className="mb-4 text-lg font-bold text-gray-900 dark:text-white">Invite Member</h3>
            <div className="space-y-3">
              <input placeholder="Username" value={inviteForm.username} onChange={e => setInviteForm({...inviteForm, username: e.target.value})} className={inputClass} />
              <select value={inviteForm.role} onChange={e => setInviteForm({...inviteForm, role: e.target.value})} className={inputClass}>
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
            <div className="mt-4 flex gap-2">
              <button onClick={inviteMember} disabled={saving || !inviteForm.username} className="flex-1 rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
                {saving ? "Inviting…" : "Invite"}
              </button>
              <button onClick={() => { setShowInvite(false); setError(null); }} className="flex-1 rounded-xl border border-gray-200 py-2.5 text-sm font-semibold dark:border-gray-700">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
