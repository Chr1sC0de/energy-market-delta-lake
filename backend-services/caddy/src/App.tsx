import { FormEvent, useEffect, useId, useMemo, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Outlet, useLocation, useSearchParams } from "react-router";
import {
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  CircleDot,
  KeyRound,
  LockKeyhole,
  Map,
  Shield,
  ShieldCheck,
} from "lucide-react";

type RouteTone = "dashboard" | "source" | "admin";
type RouteAccess = "Public" | "Private" | "Restricted";

type WorkspaceRoute = {
  access: RouteAccess;
  action: string;
  description: string;
  href: string;
  icon: typeof BarChart3;
  label: string;
  navLabel: string;
  proof: string[];
  system: string;
  tone: RouteTone;
  title: string;
};

const workspaceRoutes: WorkspaceRoute[] = [
  {
    access: "Public",
    action: "Open public Dagster",
    description:
      "Trace records, checks, and refreshes without entering the private console.",
    href: "/dagster-webserver/guest",
    icon: Map,
    label: "Source map",
    navLabel: "Public Dagster",
    proof: ["Public view", "Asset lineage", "Run history", "Data checks"],
    system: "Dagster",
    tone: "source",
    title: "Start with the public source map.",
  },
  {
    access: "Private",
    action: "Open private Dagster",
    description:
      "Use maintainer access to inspect runs, diagnose failures, and operate protected workflows.",
    href: "/dagster-webserver/admin",
    icon: KeyRound,
    label: "Admin tools",
    navLabel: "Private Dagster",
    proof: ["Maintainers", "Run control", "Health review", "Operations"],
    system: "Dagster",
    tone: "admin",
    title: "Operate from the private console.",
  },
  {
    access: "Restricted",
    action: "Open restricted dashboards",
    description:
      "Curated market dashboards stay visible in the route list, but access is restricted for now.",
    href: "/marimo",
    icon: BarChart3,
    label: "Dashboards",
    navLabel: "Dashboards",
    proof: ["Prices", "Flows", "Storage", "Status"],
    system: "Dashboards",
    tone: "dashboard",
    title: "Dashboards are restricted for now.",
  },
];

export default function App() {
  const location = useLocation();

  return (
    <>
      <ScrollToTop />
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="app-shell-nav">
        <a className="brand-lockup" href="/" aria-label="Energy Market Delta Lake">
          <span className="brand-sigil">EM</span>
          <span>
            <strong>Energy Market Delta Lake</strong>
            <small>Australian gas market tools</small>
          </span>
        </a>
        <nav aria-label="Primary routes">
          {workspaceRoutes.map((route) => (
            <a href={route.href} key={route.href}>
              {route.navLabel}
            </a>
          ))}
        </nav>
      </header>
      <main id="main-content">
        <AnimatePresence mode="wait">
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            className="page-transition"
            exit={{ opacity: 0, y: -10 }}
            initial={{ opacity: 0, y: 12 }}
            key={location.pathname}
            transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </>
  );
}

function ScrollToTop() {
  const location = useLocation();
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: reduceMotion ? "auto" : "smooth",
    });
  }, [location.pathname, reduceMotion]);

  return null;
}

export function HomePage() {
  const reduceMotion = useReducedMotion();
  const [activeHref, setActiveHref] = useState(workspaceRoutes[0].href);
  const activeRoute = useMemo(
    () =>
      workspaceRoutes.find((route) => route.href === activeHref) ??
      workspaceRoutes[0],
    [activeHref],
  );

  return (
    <section
      className={`workspace-page workspace-page--${activeRoute.tone}`}
      aria-labelledby="workspace-title"
      onPointerMove={(event) => {
        if (reduceMotion) {
          return;
        }

        const rect = event.currentTarget.getBoundingClientRect();
        event.currentTarget.style.setProperty(
          "--pointer-x",
          `${((event.clientX - rect.left) / rect.width) * 100}%`,
        );
        event.currentTarget.style.setProperty(
          "--pointer-y",
          `${((event.clientY - rect.top) / rect.height) * 100}%`,
        );
      }}
    >
      <div className="workspace-atmosphere" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <div className="workspace-grid">
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="workspace-copy"
          initial={{ opacity: 0, y: 18 }}
          transition={{ duration: reduceMotion ? 0 : 0.45 }}
        >
          <p className="eyebrow">Australian gas market workspace</p>
          <h1 id="workspace-title">Choose the right market door.</h1>
          <p className="workspace-lede">
            Public Dagster comes first. Private Dagster is for maintainers.
            Dashboards are listed last while access stays restricted.
          </p>
        </motion.div>

        <RoutePreview activeRoute={activeRoute} reduceMotion={reduceMotion} />

        <div className="route-stack" aria-label="Workspace routes">
          {workspaceRoutes.map((route, index) => (
            <RouteCard
              index={index}
              isActive={route.href === activeRoute.href}
              key={route.href}
              onActivate={() => setActiveHref(route.href)}
              reduceMotion={reduceMotion}
              route={route}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

const genericLoginFailure = "Sign in failed. Check your details and try again.";

function apiRedirectPath(value: unknown) {
  if (typeof value !== "string") {
    return null;
  }

  if (!value.startsWith("/") || value.startsWith("//")) {
    return null;
  }

  return value;
}

export function LoginPage() {
  const reduceMotion = useReducedMotion();
  const [searchParams] = useSearchParams();
  const identifierId = useId();
  const passwordId = useId();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [failure, setFailure] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const requestedNext = searchParams.get("next") ?? "/";

  async function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFailure("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/auth/login", {
        body: JSON.stringify({
          identifier,
          next: requestedNext,
          password,
        }),
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
      });

      if (!response.ok) {
        setFailure(genericLoginFailure);
        return;
      }

      const payload: unknown = await response.json();
      const redirectTo = apiRedirectPath(
        payload && typeof payload === "object" && "redirect_to" in payload
          ? payload.redirect_to
          : null,
      );

      if (!redirectTo) {
        setFailure(genericLoginFailure);
        return;
      }

      window.location.assign(redirectTo);
    } catch {
      setFailure(genericLoginFailure);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section
      className="workspace-page workspace-page--login"
      aria-labelledby="login-title"
    >
      <div className="workspace-atmosphere" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <div className="login-layout">
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="login-copy"
          initial={{ opacity: 0, y: 18 }}
          transition={{ duration: reduceMotion ? 0 : 0.42 }}
        >
          <p className="eyebrow">Maintainer access</p>
          <h1 id="login-title">Sign in to continue.</h1>
          <p className="workspace-lede">
            Use your Energy Market Delta Lake account to open protected market
            tooling.
          </p>
        </motion.div>

        <motion.form
          animate={{ opacity: 1, y: 0 }}
          aria-describedby={failure ? "login-error" : undefined}
          className="login-panel"
          initial={{ opacity: 0, y: 20 }}
          onSubmit={submitLogin}
          transition={{ delay: reduceMotion ? 0 : 0.08, duration: 0.38 }}
        >
          <div className="login-panel-topline">
            <span className="preview-icon">
              <Shield aria-hidden="true" />
            </span>
            <span>Protected workspace</span>
          </div>
          <div className="login-field">
            <label htmlFor={identifierId}>Email or username</label>
            <input
              autoComplete="username"
              id={identifierId}
              name="identifier"
              onChange={(event) => setIdentifier(event.target.value)}
              required
              type="text"
              value={identifier}
            />
          </div>
          <div className="login-field">
            <label htmlFor={passwordId}>Password</label>
            <input
              autoComplete="current-password"
              id={passwordId}
              name="password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </div>
          {failure ? (
            <p className="login-error" id="login-error" role="alert">
              {failure}
            </p>
          ) : null}
          <button className="preview-action login-submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in" : "Sign in"}
            <ArrowUpRight aria-hidden="true" />
          </button>
        </motion.form>
      </div>
    </section>
  );
}

function RouteCard({
  index,
  isActive,
  onActivate,
  reduceMotion,
  route,
}: {
  index: number;
  isActive: boolean;
  onActivate: () => void;
  reduceMotion: boolean | null;
  route: WorkspaceRoute;
}) {
  const Icon = route.icon;

  return (
    <motion.a
      animate={{ opacity: 1, y: 0 }}
      className={`route-card route-card--${route.tone}`}
      data-active={isActive}
      href={route.href}
      initial={{ opacity: 0, y: 20 }}
      onFocus={onActivate}
      onMouseEnter={onActivate}
      transition={{ delay: reduceMotion ? 0 : index * 0.07, duration: 0.34 }}
      whileHover={reduceMotion ? undefined : { y: -6 }}
    >
      <span className="route-card-index">0{index + 1}</span>
      <span className="route-card-icon">
        <Icon aria-hidden="true" />
      </span>
      <span>
        <small className="route-card-kicker">
          {route.access} / {route.system}
        </small>
        <strong>{route.label}</strong>
        <small>{route.description}</small>
      </span>
      <ArrowUpRight aria-hidden="true" />
    </motion.a>
  );
}

function RoutePreview({
  activeRoute,
  reduceMotion,
}: {
  activeRoute: WorkspaceRoute;
  reduceMotion: boolean | null;
}) {
  const Icon = activeRoute.icon;

  return (
    <aside className="route-preview" aria-label={`${activeRoute.label} preview`}>
      <motion.div
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        className="route-preview-content"
        initial={
          reduceMotion ? false : { opacity: 0, y: 14, filter: "blur(8px)" }
        }
        key={activeRoute.href}
        transition={{
          duration: reduceMotion ? 0 : 0.28,
          ease: [0.2, 0.8, 0.2, 1],
        }}
      >
        <div className="preview-topline">
          <span className="preview-icon">
            <Icon aria-hidden="true" />
          </span>
          <span>
            {activeRoute.access} access / {activeRoute.system}
          </span>
        </div>
        <h2>{activeRoute.title}</h2>
        <p>{activeRoute.description}</p>
        <div className="proof-grid" aria-label={`${activeRoute.label} coverage`}>
          {activeRoute.proof.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
        <a className="preview-action" href={activeRoute.href}>
          {activeRoute.action}
          <ArrowUpRight aria-hidden="true" />
        </a>
      </motion.div>
      <div className="preview-meter" aria-hidden="true">
        <CircleDot />
        <CheckCircle2 />
        <ShieldCheck />
        <LockKeyhole />
      </div>
    </aside>
  );
}
