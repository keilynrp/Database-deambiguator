"use client";

import { useCallback, useEffect, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { Badge, type ToastVariant } from "../components/ui";
import { apiFetch } from "@/lib/api";
import { ROLE_LABEL_KEYS, ROLE_VARIANTS, type UserRecord, type UserRole } from "./userManagementTypes";

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function UsersTab({
    currentUserId,
    toast,
}: {
    currentUserId: number;
    toast: (msg: string, v?: ToastVariant) => void;
}) {
    const { t } = useLanguage();
    const [users, setUsers] = useState<UserRecord[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [saving, setSaving] = useState(false);
    const [actionId, setActionId] = useState<number | null>(null);

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        role: "viewer" as UserRole,
    });

    const fetchUsers = useCallback(async () => {
        try {
            const res = await apiFetch("/users");
            if (!res.ok) {
                throw new Error(t("settings.users.toast.load_failed"));
            }
            setUsers(await res.json());
        } catch (error: unknown) {
            toast(getErrorMessage(error, t("settings.users.toast.load_failed")), "error");
        } finally {
            setLoading(false);
        }
    }, [t, toast]);

    useEffect(() => {
        void fetchUsers();
    }, [fetchUsers]);

    async function handleCreate(event: React.FormEvent) {
        event.preventDefault();
        if (form.password.length < 8) {
            toast(t("settings.users.toast.password_too_short"), "error");
            return;
        }
        setSaving(true);
        try {
            const res = await apiFetch("/users", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: t("settings.users.toast.create_failed") })) as { detail?: string };
                throw new Error(err.detail || t("settings.users.toast.create_failed"));
            }
            toast(t("settings.users.toast.created", { username: form.username }), "success");
            setForm({ username: "", email: "", password: "", role: "viewer" });
            setShowForm(false);
            await fetchUsers();
        } catch (error: unknown) {
            toast(getErrorMessage(error, t("settings.users.toast.create_error")), "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleRoleChange(userId: number, newRole: UserRole) {
        setActionId(userId);
        try {
            const res = await apiFetch(`/users/${userId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role: newRole }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: t("settings.users.toast.update_role_failed") })) as { detail?: string };
                throw new Error(err.detail || t("settings.users.toast.update_role_failed"));
            }
            setUsers(prev => prev.map(user => (user.id === userId ? { ...user, role: newRole } : user)));
            toast(t("settings.users.toast.role_updated"), "success");
        } catch (error: unknown) {
            toast(getErrorMessage(error, t("settings.users.toast.update_role_error")), "error");
        } finally {
            setActionId(null);
        }
    }

    async function handleDeactivate(userId: number, username: string) {
        if (!confirm(t("settings.users.deactivate_confirm", { username }))) return;
        setActionId(userId);
        try {
            const res = await apiFetch(`/users/${userId}`, { method: "DELETE" });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: t("settings.users.toast.deactivate_failed") })) as { detail?: string };
                throw new Error(err.detail || t("settings.users.toast.deactivate_failed"));
            }
            setUsers(prev => prev.map(user => (user.id === userId ? { ...user, is_active: false } : user)));
            toast(t("settings.users.toast.deactivated", { username }), "warning");
        } catch (error: unknown) {
            toast(getErrorMessage(error, t("settings.users.toast.deactivate_error")), "error");
        } finally {
            setActionId(null);
        }
    }

    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t("settings.users.count_summary", {
                        active: users.filter(user => user.is_active).length,
                        inactive: users.filter(user => !user.is_active).length,
                    })}
                </p>
                <button
                    onClick={() => setShowForm(value => !value)}
                    className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
                >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showForm ? "M6 18L18 6M6 6l12 12" : "M12 4v16m8-8H4"} />
                    </svg>
                    {showForm ? t("common.cancel") : t("settings.users.new_user")}
                </button>
            </div>

            {showForm && (
                <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-6 shadow-sm dark:border-blue-500/20 dark:bg-blue-500/5 toast-enter">
                    <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">{t("settings.users.create_title")}</h3>
                    <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{t("settings.account.username")} *</label>
                            <input
                                className={inputClass}
                                value={form.username}
                                onChange={event => setForm(prev => ({ ...prev, username: event.target.value }))}
                                required
                                minLength={1}
                                maxLength={50}
                                placeholder="johndoe"
                            />
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{t("settings.account.email")}</label>
                            <input
                                type="email"
                                className={inputClass}
                                value={form.email}
                                onChange={event => setForm(prev => ({ ...prev, email: event.target.value }))}
                                placeholder="john@example.com"
                            />
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{t("settings.users.password")} * <span className="font-normal text-gray-400">({t("settings.users.password_help")})</span></label>
                            <input
                                type="password"
                                className={inputClass}
                                value={form.password}
                                onChange={event => setForm(prev => ({ ...prev, password: event.target.value }))}
                                required
                                minLength={8}
                                autoComplete="new-password"
                            />
                        </div>
                        <div>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{t("settings.account.role")} *</label>
                            <select
                                className={inputClass}
                                value={form.role}
                                onChange={event => setForm(prev => ({ ...prev, role: event.target.value as UserRole }))}
                            >
                                <option value="viewer">{t("users.role.viewer")}</option>
                                <option value="editor">{t("users.role.editor")}</option>
                                <option value="admin">{t("users.role.admin")}</option>
                                <option value="super_admin">{t("users.role.super_admin")}</option>
                            </select>
                        </div>
                        <div className="flex justify-end gap-2 pt-1 sm:col-span-2">
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                            >
                                {t("common.cancel")}
                            </button>
                            <button
                                type="submit"
                                disabled={saving}
                                className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                            >
                                {saving && (
                                    <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                )}
                                {t("settings.users.create_button")}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <svg className="h-6 w-6 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                    </div>
                ) : (
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-800">
                                {["User", "Email", "Role", "Status", "Actions"].map(header => (
                                    <th key={header} className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                                        {header === "User" ? t("settings.users.header_user")
                                            : header === "Email" ? t("settings.users.header_email")
                                            : header === "Role" ? t("settings.users.header_role")
                                            : header === "Status" ? t("common.status")
                                            : t("common.actions")}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                            {users.map(user => (
                                <tr key={user.id} className={`${!user.is_active ? "opacity-50" : ""} hover:bg-gray-50 dark:hover:bg-gray-800/50`}>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2.5">
                                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                                                {user.username.slice(0, 2).toUpperCase()}
                                            </span>
                                            <div>
                                                <p className="font-medium text-gray-900 dark:text-white">{user.username}</p>
                                                {user.id === currentUserId && (
                                                    <p className="text-[10px] text-blue-500">{t("settings.users.you")}</p>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-500 dark:text-gray-400">{user.email || "—"}</td>
                                    <td className="px-5 py-3.5">
                                        {user.id === currentUserId ? (
                                            <Badge variant={ROLE_VARIANTS[user.role] ?? "default"}>
                                                {t(ROLE_LABEL_KEYS[user.role])}
                                            </Badge>
                                        ) : (
                                            <select
                                                value={user.role}
                                                onChange={event => handleRoleChange(user.id, event.target.value as UserRole)}
                                                disabled={actionId === user.id || !user.is_active}
                                                className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-xs font-medium text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                                            >
                                                <option value="viewer">{t("users.role.viewer")}</option>
                                                <option value="editor">{t("users.role.editor")}</option>
                                                <option value="admin">{t("users.role.admin")}</option>
                                                <option value="super_admin">{t("users.role.super_admin")}</option>
                                            </select>
                                        )}
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <Badge variant={user.is_active ? "success" : "default"} dot>
                                            {user.is_active ? t("common.active") : t("common.inactive")}
                                        </Badge>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        {user.id !== currentUserId && user.is_active && (
                                            <button
                                                onClick={() => handleDeactivate(user.id, user.username)}
                                                disabled={actionId === user.id}
                                                className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-40 dark:hover:bg-red-500/10 dark:hover:text-red-400"
                                                title={t("users.deactivate")}
                                            >
                                                {actionId === user.id ? (
                                                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                    </svg>
                                                ) : (
                                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                                    </svg>
                                                )}
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
