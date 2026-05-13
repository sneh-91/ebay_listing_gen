import { LandingHero } from "../components/LandingHero";

type LandingPageProps = {
  onCreateListing: () => void;
};

export function LandingPage({ onCreateListing }: LandingPageProps) {
  return (
    <main className="min-h-screen bg-hero px-4 py-6 text-text">
      <LandingHero onCreateListing={onCreateListing} />
    </main>
  );
}
