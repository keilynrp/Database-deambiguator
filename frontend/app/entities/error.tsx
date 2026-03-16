"use client";

import { useEffect } from "react";
import RouteError from "../components/RouteError";

interface Props { error: Error & { digest?: string }; reset: () => void; }

export default function Error({ error, reset }: Props) {
  useEffect(() => { console.error("[UKIP] entities error:", error); }, [error]);
  return <RouteError title="Failed to load Entities" error={error} reset={reset} />;
}
