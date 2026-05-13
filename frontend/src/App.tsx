import { useEffect, useState } from "react";
import { LandingPage } from "./pages/LandingPage";
import { CreatePage } from "./pages/CreatePage";

type RoutePath = "/" | "/create";

function normalizePath(pathname: string): RoutePath {
  return pathname === "/create" ? "/create" : "/";
}

export default function App() {
  const [route, setRoute] = useState<RoutePath>(() =>
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

  const navigate = (path: RoutePath) => {
    if (window.location.pathname === path) {
      return;
    }

    window.history.pushState({}, "", path);
    setRoute(path);
  };

  if (route === "/create") {
    return <CreatePage onNavigateHome={() => navigate("/")} />;
  }

  return <LandingPage onCreateListing={() => navigate("/create")} />;
}
