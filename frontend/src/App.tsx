import { useEffect, useState } from "react";
import { LandingPage } from "./pages/LandingPage";
import { CreatePage } from "./pages/CreatePage";
import { ReviewPage } from "./pages/ReviewPage";

type RouteState =
  | { path: "/" }
  | { path: "/create" }
  | { path: "/review"; draftId: string };

function normalizePath(pathname: string): RouteState {
  if (pathname === "/create") {
    return { path: "/create" };
  }

  if (pathname.startsWith("/review/")) {
    const draftId = pathname.replace("/review/", "").trim();
    if (draftId) {
      return { path: "/review", draftId };
    }
  }

  return { path: "/" };
}

export default function App() {
  const [route, setRoute] = useState<RouteState>(() =>
    normalizePath(window.location.pathname),
  );

  useEffect(() => {
    const syncRoute = () => {
      setRoute(normalizePath(window.location.pathname));
    };

    window.addEventListener("popstate", syncRoute);

    return () => {
      window.removeEventListener("popstate", syncRoute);
    };
  }, []);

  const navigate = (path: string) => {
    if (window.location.pathname === path) {
      return;
    }

    window.history.pushState({}, "", path);
    setRoute(normalizePath(path));
  };

  if (route.path === "/create") {
    return <CreatePage onNavigateHome={() => navigate("/")} />;
  }

  if (route.path === "/review") {
    return (
      <ReviewPage
        draftId={route.draftId}
        onBackToCreate={() => navigate("/create")}
        onNavigateHome={() => navigate("/")}
      />
    );
  }

  return <LandingPage onCreateListing={() => navigate("/create")} />;
}
