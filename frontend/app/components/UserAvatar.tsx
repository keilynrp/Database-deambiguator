"use client";

import Image from "next/image";

interface UserAvatarProps {
  username: string;
  role: string;
  avatarUrl?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const ROLE_BG: Record<string, string> = {
  super_admin: "bg-red-500",
  admin:       "bg-orange-500",
  editor:      "bg-blue-500",
  viewer:      "bg-gray-500",
};

const SIZE_CLS = {
  sm: "h-8 w-8 text-sm",
  md: "h-9 w-9 text-sm",
  lg: "h-14 w-14 text-xl",
};

export default function UserAvatar({ username, role, avatarUrl, size = "md", className = "" }: UserAvatarProps) {
  const initials = username?.[0]?.toUpperCase() ?? "?";
  const bg = ROLE_BG[role] ?? ROLE_BG.viewer;
  const sizeCls = SIZE_CLS[size];
  const imageSizes: Record<NonNullable<UserAvatarProps["size"]>, string> = {
    sm: "32px",
    md: "36px",
    lg: "56px",
  };

  if (avatarUrl) {
    return (
      <span className={`relative inline-block overflow-hidden rounded-full ${sizeCls} ${className}`}>
        <Image
          src={avatarUrl}
          alt={username}
          fill
          sizes={imageSizes[size]}
          unoptimized
          className="object-cover"
        />
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-bold text-white ${bg} ${sizeCls} ${className}`}
    >
      {initials}
    </span>
  );
}
