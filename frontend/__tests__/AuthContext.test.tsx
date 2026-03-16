import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthProvider, useAuth } from "../app/contexts/AuthContext";

// ── Helpers ────────────────────────────────────────────────────────────────

function TestConsumer() {
  const { token, user, isAuthenticated, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="auth">{isAuthenticated ? "yes" : "no"}</span>
      <span data-testid="user">{user?.username ?? "none"}</span>
      <span data-testid="token">{token ? "has-token" : "no-token"}</span>
      <button onClick={() => login("admin", "pass")}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

function renderWithAuth() {
  return render(
    <AuthProvider>
      <TestConsumer />
    </AuthProvider>
  );
}

// ── Mock fetch ─────────────────────────────────────────────────────────────

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

const mockLocalStorage: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (k: string) => mockLocalStorage[k] ?? null,
  setItem: (k: string, v: string) => { mockLocalStorage[k] = v; },
  removeItem: (k: string) => { delete mockLocalStorage[k]; },
  clear: () => { Object.keys(mockLocalStorage).forEach(k => delete mockLocalStorage[k]); },
});

// ── Tests ──────────────────────────────────────────────────────────────────

beforeEach(() => {
  mockFetch.mockReset();
  localStorage.clear();
});

describe("AuthContext", () => {
  it("starts unauthenticated when no stored token", async () => {
    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId("auth").textContent).toBe("no");
    });
  });

  it("login sets token and fetches user profile", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: "tok123" }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, username: "admin", role: "super_admin", email: null, is_active: true }),
      });

    renderWithAuth();
    await act(async () => {
      await userEvent.click(screen.getByRole("button", { name: "Login" }));
    });

    await waitFor(() => {
      expect(screen.getByTestId("auth").textContent).toBe("yes");
      expect(screen.getByTestId("user").textContent).toBe("admin");
      expect(screen.getByTestId("token").textContent).toBe("has-token");
    });
    expect(localStorage.getItem("ukip_token")).toBe("tok123");
  });

  it("login throws on bad credentials (non-ok response)", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });

    let caughtError: Error | null = null;

    function ThrowConsumer() {
      const { login } = useAuth();
      return (
        <button onClick={async () => {
          try { await login("admin", "bad"); }
          catch (e) { caughtError = e as Error; }
        }}>
          TryLogin
        </button>
      );
    }

    render(<AuthProvider><ThrowConsumer /></AuthProvider>);
    await act(async () => {
      await userEvent.click(screen.getByRole("button", { name: "TryLogin" }));
    });

    expect(caughtError).not.toBeNull();
    expect((caughtError as Error).message).toBe("Invalid credentials");
  });

  it("logout clears token and user", async () => {
    // Seed a token
    mockFetch
      .mockResolvedValueOnce({ ok: true, json: async () => ({ access_token: "tok" }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 1, username: "u", role: "admin", email: null, is_active: true }) });

    renderWithAuth();
    await act(async () => {
      await userEvent.click(screen.getByRole("button", { name: "Login" }));
    });
    await waitFor(() => expect(screen.getByTestId("auth").textContent).toBe("yes"));

    await act(async () => {
      await userEvent.click(screen.getByRole("button", { name: "Logout" }));
    });

    await waitFor(() => {
      expect(screen.getByTestId("auth").textContent).toBe("no");
      expect(screen.getByTestId("user").textContent).toBe("none");
    });
    expect(localStorage.getItem("ukip_token")).toBeNull();
  });

  it("hydrates from stored token on mount", async () => {
    localStorage.setItem("ukip_token", "stored-tok");
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 2, username: "stored", role: "viewer", email: null, is_active: true }),
    });

    renderWithAuth();

    await waitFor(() => {
      expect(screen.getByTestId("user").textContent).toBe("stored");
      expect(screen.getByTestId("auth").textContent).toBe("yes");
    });
  });

  it("shows no user profile if stored token is rejected by server", async () => {
    // isAuthenticated is token-based (not server-verified), but user profile won't be set
    localStorage.setItem("ukip_token", "expired-tok");
    mockFetch.mockResolvedValueOnce({ ok: false });

    renderWithAuth();

    await waitFor(() => {
      // Token exists so isAuthenticated=true, but user profile is not populated
      expect(screen.getByTestId("user").textContent).toBe("none");
    });
  });
});
