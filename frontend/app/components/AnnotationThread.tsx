"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "../contexts/AuthContext";
import { useLanguage } from "../contexts/LanguageContext";

interface Annotation {
  id: number;
  entity_id: number | null;
  authority_id: number | null;
  parent_id: number | null;
  author_id: number;
  author_name: string;
  content: string;
  created_at: string;
  updated_at: string;
  is_resolved: boolean;
  resolved_at: string | null;
  resolved_by_id: number | null;
  emoji_reactions: Record<string, number[]>;
}

function timeAgo(iso: string, locale: "en" | "es"): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
  if (diff < 60) return rtf.format(0, "second");
  if (diff < 3600) return rtf.format(-Math.floor(diff / 60), "minute");
  if (diff < 86400) return rtf.format(-Math.floor(diff / 3600), "hour");
  return rtf.format(-Math.floor(diff / 86400), "day");
}

const REACTIONS = ["👍", "❤️", "🚀", "👀", "✅", "😄", "🎉"] as const;

interface AnnotationThreadProps {
  entityId?: number;
  authorityId?: number;
}

export default function AnnotationThread({ entityId, authorityId }: AnnotationThreadProps) {
  const { user } = useAuth();
  const { language, t } = useLanguage();
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [newContent, setNewContent] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState("");
  const [editId, setEditId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (entityId !== undefined) params.set("entity_id", String(entityId));
    if (authorityId !== undefined) params.set("authority_id", String(authorityId));
    try {
      const r = await apiFetch(`/annotations?${params}`);
      if (r.ok) setAnnotations(await r.json());
    } catch { /* non-critical */ }
  }, [entityId, authorityId]);

  useEffect(() => { load(); }, [load]);

  const post = async (content: string, parentId?: number) => {
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      await apiFetch("/annotations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_id: entityId ?? null,
          authority_id: authorityId ?? null,
          parent_id: parentId ?? null,
          content,
        }),
      });
      setNewContent("");
      setReplyContent("");
      setReplyTo(null);
      load();
    } finally { setSubmitting(false); }
  };

  const save = async (id: number, content: string) => {
    await apiFetch(`/annotations/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    setEditId(null);
    load();
  };

  const remove = async (id: number) => {
    await apiFetch(`/annotations/${id}`, { method: "DELETE" });
    load();
  };

  const resolve = async (id: number) => {
    await apiFetch(`/annotations/${id}/resolve`, { method: "POST" });
    load();
  };

  const react = async (id: number, emoji: string) => {
    await apiFetch(`/annotations/${id}/react?emoji=${encodeURIComponent(emoji)}`, { method: "POST" });
    load();
  };

  const topLevel = annotations.filter(a => a.parent_id === null);
  const replies = (parentId: number) => annotations.filter(a => a.parent_id === parentId);

  const isEditorOrAbove = user && ["editor", "admin", "super_admin"].includes(user.role);

  return (
    <div className="space-y-3">
      {/* New comment form */}
      {isEditorOrAbove && (
        <div className="flex gap-2">
          <textarea
            value={newContent}
            onChange={e => setNewContent(e.target.value)}
            placeholder={t("page.authority.add_comment_placeholder")}
            rows={2}
            className="flex-1 resize-none rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
          <button
            onClick={() => post(newContent)}
            disabled={!newContent.trim() || submitting}
            className="self-end rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {t("page.authority.post_comment")}
          </button>
        </div>
      )}

      {/* Thread */}
      <div className="space-y-2">
        {topLevel.length === 0 && (
          <p className="text-xs text-gray-400 dark:text-gray-500">{t("page.authority.no_comments")}</p>
        )}
        {topLevel.map(ann => (
          <div key={ann.id} className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/40">
            {/* Top annotation */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-[10px] font-bold text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
                  {ann.author_name.slice(0, 2).toUpperCase()}
                </span>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{ann.author_name}</span>
                <span className="text-xs text-gray-400">{timeAgo(ann.created_at, language)}</span>
                {ann.is_resolved && (
                  <span className="rounded-full bg-emerald-100 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                    {t("page.authority.resolved")}
                  </span>
                )}
              </div>
              {user && (user.username === ann.author_name || ["admin", "super_admin"].includes(user.role)) && (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => { setEditId(ann.id); setEditContent(ann.content); }}
                    className="rounded p-1 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                    title={t("common.edit")}
                  >
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => remove(ann.id)}
                    className="rounded p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                    title={t("common.delete")}
                  >
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}
            </div>

            {editId === ann.id ? (
              <div className="mt-2 flex gap-2">
                <textarea
                  value={editContent}
                  onChange={e => setEditContent(e.target.value)}
                  rows={2}
                  className="flex-1 resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                />
                <div className="flex flex-col gap-1">
                  <button onClick={() => save(ann.id, editContent)} className="rounded bg-indigo-600 px-3 py-1 text-xs text-white">{t("common.save")}</button>
                  <button onClick={() => setEditId(null)} className="rounded border border-gray-300 px-3 py-1 text-xs text-gray-600 dark:border-gray-600 dark:text-gray-400">{t("common.cancel")}</button>
                </div>
              </div>
            ) : (
              <p className="mt-1.5 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{ann.content}</p>
            )}

            {/* Resolve button + reactions */}
            <div className="mt-2 flex items-center gap-3 flex-wrap">
              {isEditorOrAbove && ann.parent_id === null && (
                <button
                  onClick={() => resolve(ann.id)}
                  className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                    ann.is_resolved
                  ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400"
                  }`}
                >
                  {ann.is_resolved ? `✅ ${t("page.authority.resolved")}` : t("page.authority.mark_resolved")}
                </button>
              )}
              {/* Emoji reactions */}
              <div className="flex items-center gap-1 flex-wrap">
                {REACTIONS.map(emoji => {
                  const users = ann.emoji_reactions?.[emoji] ?? [];
                  const hasReacted = user && users.includes(user.id);
                  return (
                    <button
                      key={emoji}
                      onClick={() => react(ann.id, emoji)}
                      title={`${users.length} ${t("page.authority.reactions")}`}
                      className={`inline-flex items-center gap-0.5 rounded-full border px-1.5 py-0.5 text-xs transition-colors ${
                        hasReacted
                          ? "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-950/30 dark:text-blue-300"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
                      }`}
                    >
                      {emoji}{users.length > 0 && <span className="font-semibold">{users.length}</span>}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Replies */}
            <div className="mt-2 space-y-2 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
              {replies(ann.id).map(rep => (
                <div key={rep.id} className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-semibold text-gray-600 dark:text-gray-400">{rep.author_name}</span>
                      <span className="text-[10px] text-gray-400">{timeAgo(rep.created_at, language)}</span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{rep.content}</p>
                  </div>
                  {user && (user.username === rep.author_name || ["admin", "super_admin"].includes(user.role)) && (
                    <button onClick={() => remove(rep.id)} className="shrink-0 rounded p-1 text-gray-300 hover:text-red-500">
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}

              {/* Reply form */}
              {isEditorOrAbove && replyTo === ann.id ? (
                <div className="flex gap-2 pt-1">
                  <input
                    value={replyContent}
                    onChange={e => setReplyContent(e.target.value)}
                    placeholder={t("page.authority.write_reply")}
                    className="flex-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                    onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); post(replyContent, ann.id); } }}
                  />
                  <button onClick={() => post(replyContent, ann.id)} disabled={!replyContent.trim() || submitting} className="rounded bg-indigo-600 px-3 py-1 text-xs text-white disabled:opacity-50">{t("page.authority.reply")}</button>
                  <button onClick={() => setReplyTo(null)} className="rounded border border-gray-200 px-2 py-1 text-xs text-gray-500 dark:border-gray-700">{t("common.cancel")}</button>
                </div>
              ) : isEditorOrAbove ? (
                <button onClick={() => setReplyTo(ann.id)} className="text-[10px] text-indigo-500 hover:underline">{t("page.authority.reply")}</button>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
