"use client";

import { useEffect, useRef } from "react";

const FOCUSABLE = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");

/**
 * Traps keyboard focus inside the referenced container while `active` is true.
 * Returns focus to the previously focused element when deactivated.
 *
 * Usage:
 *   const trapRef = useFocusTrap(isOpen);
 *   <div ref={trapRef} role="dialog" aria-modal="true"> … </div>
 */
export function useFocusTrap<T extends HTMLElement>(active: boolean) {
  const ref = useRef<T>(null);
  const previousFocus = useRef<Element | null>(null);

  useEffect(() => {
    if (!active) return;

    // Remember what had focus before we opened
    previousFocus.current = document.activeElement;

    // Move focus into the dialog — first focusable child, or the container itself
    const container = ref.current;
    if (!container) return;
    const first = container.querySelectorAll<HTMLElement>(FOCUSABLE)[0];
    (first ?? container).focus();

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== "Tab") return;
      const focusable = Array.from(
        container!.querySelectorAll<HTMLElement>(FOCUSABLE)
      );
      if (focusable.length === 0) { e.preventDefault(); return; }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      // Restore focus to the element that had it before
      if (previousFocus.current && "focus" in previousFocus.current) {
        (previousFocus.current as HTMLElement).focus();
      }
    };
  }, [active]);

  return ref;
}
