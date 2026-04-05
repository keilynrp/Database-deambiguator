"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Badge } from "../components/ui";
import { apiFetch } from "@/lib/api";
import AvatarUpload from "../components/AvatarUpload";
import PasswordStrength from "../components/PasswordStrength";
import { ROLE_LABELS, ROLE_VARIANTS, type UserRole } from "./userManagementTypes";

type ToastVariant = "success" | "error" | "warning" | "info" | "default";

type AccountUser = {
    id: number;
    username: string;
    role: string;
    email: string | null;
    is_active: boolean;
    avatar_url?: string | null;
    display_name?: string | null;
    bio?: string | null;
    created_at?: string | null;
};

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function AccountTab({
    user,
    updateAvatarUrl,
    toast,
}: {
    user: AccountUser | null;
    updateAvatarUrl: (url: string | null) => void;
    toast: (msg: string, v?: ToastVariant) => void;
}) {
    const { refreshUser } = useAuth();
    const [displayName, setDisplayName] = useState(user?.display_name ?? "");
    const [email, setEmail] = useState(user?.email ?? "");
    const [bio, setBio] = useState(user?.bio ?? "");
    const [profileSaving, setProfileSaving] = useState(false);

    const [currentPw, setCurrentPw] = useState("");
    const [newPw, setNewPw] = useState("");
    const [confirmPw, setConfirmPw] = useState("");
    const [pwSaving, setPwSaving] = useState(false);

    useEffect(() => {
        setDisplayName(user?.display_name ?? "");
        setEmail(user?.email ?? "");
        setBio(user?.bio ?? "");
    }, [user?.bio, user?.display_name, user?.email]);

    async function handleSaveProfile(event: React.FormEvent) {
        event.preventDefault();
        setProfileSaving(true);
        try {
            const body: Record<string, string> = {};
            if (displayName !== (user?.display_name ?? "")) body.display_name = displayName;
            if (email !== (user?.email ?? "")) body.email = email;
            if (bio !== (user?.bio ?? "")) body.bio = bio;
            if (Object.keys(body).length === 0) {
                toast("No changes to save", "info");
                return;
            }

            const response = await apiFetch("/users/me/profile", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({ detail: "Failed to save profile" })) as { detail?: string };
                throw new Error(errorBody.detail || "Failed to save profile");
            }

            await refreshUser();
            toast("Profile updated successfully", "success");
        } catch (error: unknown) {
            toast(getErrorMessage(error, "Error saving profile"), "error");
        } finally {
            setProfileSaving(false);
        }
    }

    async function handleChangePassword(event: React.FormEvent) {
        event.preventDefault();
        if (newPw.length < 8) {
            toast("New password must be at least 8 characters", "error");
            return;
        }
        if (newPw !== confirmPw) {
            toast("Passwords do not match", "error");
            return;
        }

        setPwSaving(true);
        try {
            const response = await apiFetch("/users/me/password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
            });
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({ detail: "Failed to change password" })) as { detail?: string };
                throw new Error(errorBody.detail || "Failed to change password");
            }

            toast("Password updated successfully", "success");
            setCurrentPw("");
            setNewPw("");
            setConfirmPw("");
        } catch (error: unknown) {
            toast(getErrorMessage(error, "Error changing password"), "error");
        } finally {
            setPwSaving(false);
        }
    }

    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Profile Picture</h3>
                <AvatarUpload
                    username={user?.username ?? ""}
                    role={user?.role ?? "viewer"}
                    currentAvatarUrl={user?.avatar_url}
                    onUpdated={updateAvatarUrl}
                    toast={toast}
                />
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-1 text-base font-semibold text-gray-900 dark:text-white">Profile</h3>
                <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">Update your display name, email address, and bio.</p>

                <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="flex flex-col gap-1 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/50">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Username</span>
                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{user?.username}</span>
                    </div>
                    <div className="flex flex-col gap-1 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/50">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Role</span>
                        <Badge variant={ROLE_VARIANTS[user?.role as UserRole] ?? "default"}>
                            {ROLE_LABELS[user?.role as UserRole] ?? user?.role}
                        </Badge>
                    </div>
                </div>

                <form onSubmit={handleSaveProfile} className="max-w-lg space-y-4">
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Display name <span className="font-normal text-gray-400">(optional)</span>
                        </label>
                        <input
                            type="text"
                            className={inputClass}
                            value={displayName}
                            onChange={event => setDisplayName(event.target.value)}
                            maxLength={100}
                            placeholder="Your full name or nickname"
                            autoComplete="name"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Email address
                        </label>
                        <input
                            type="email"
                            className={inputClass}
                            value={email}
                            onChange={event => setEmail(event.target.value)}
                            maxLength={255}
                            placeholder="you@example.com"
                            autoComplete="email"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Bio <span className="font-normal text-gray-400">(max 500 chars)</span>
                        </label>
                        <textarea
                            className="w-full resize-none rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                            rows={3}
                            value={bio}
                            onChange={event => setBio(event.target.value)}
                            maxLength={500}
                            placeholder="A short description about yourself..."
                        />
                        <p className="mt-1 text-right text-xs text-gray-400">{bio.length}/500</p>
                    </div>
                    <button
                        type="submit"
                        disabled={profileSaving}
                        className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                        {profileSaving && (
                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        )}
                        {profileSaving ? "Saving..." : "Save Profile"}
                    </button>
                </form>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Change Password</h3>
                <form onSubmit={handleChangePassword} className="max-w-sm space-y-4">
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Current password
                        </label>
                        <input
                            type="password"
                            className={inputClass}
                            value={currentPw}
                            onChange={event => setCurrentPw(event.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            New password
                        </label>
                        <input
                            type="password"
                            className={inputClass}
                            value={newPw}
                            onChange={event => setNewPw(event.target.value)}
                            required
                            minLength={8}
                            autoComplete="new-password"
                        />
                        <PasswordStrength password={newPw} />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Confirm new password
                        </label>
                        <input
                            type="password"
                            className={`${inputClass} ${confirmPw && confirmPw !== newPw ? "border-red-400 focus:border-red-500 focus:ring-red-400" : ""}`}
                            value={confirmPw}
                            onChange={event => setConfirmPw(event.target.value)}
                            required
                            autoComplete="new-password"
                        />
                        {confirmPw && confirmPw !== newPw && (
                            <p className="mt-1 text-xs text-red-500">Passwords do not match</p>
                        )}
                    </div>
                    <button
                        type="submit"
                        disabled={pwSaving || !currentPw || !newPw || newPw !== confirmPw}
                        className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                        {pwSaving && (
                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        )}
                        {pwSaving ? "Saving..." : "Update Password"}
                    </button>
                </form>
            </div>
        </div>
    );
}
