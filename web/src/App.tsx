import { HomepageLayout } from '@/components/layout';
import { 
  HeroSection, 
  SimulationSection, 
  StatsSection 
} from '@/components/sections';

function App() {
  return (
    <HomepageLayout>
      {/* hero section */}
      <HeroSection />
      
      {/* simulation section with real examples */}
      <SimulationSection />
      
      {/* stats and testimonials section */}
      <StatsSection />
    </HomepageLayout>
  );
}

export default App;