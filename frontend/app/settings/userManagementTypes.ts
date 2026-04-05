export type UserRole = "super_admin" | "admin" | "editor" | "viewer";

export interface UserRecord {
    id: number;
    username: string;
    email: string | null;
    role: UserRole;
    is_active: boolean;
    created_at: string | null;
}

export const ROLE_VARIANTS: Record<UserRole, "error" | "warning" | "info" | "default"> = {
    super_admin: "error",
    admin: "warning",
    editor: "info",
    viewer: "default",
};

export const ROLE_LABELS: Record<UserRole, string> = {
    super_admin: "Super Admin",
    admin: "Admin",
    editor: "Editor",
    viewer: "Viewer",
};
