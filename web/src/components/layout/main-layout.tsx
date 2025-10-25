import { useState } from 'react';
import { cn } from '@/lib/utils';
import Header from './header';
import Sidebar from './sidebar';
import Footer from './footer';
import Container from './container';

interface MainLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
  showFooter?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  showSidebar = true,
  showFooter = true,
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />

      <div className="flex flex-1">
        {showSidebar && (
          <Sidebar
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          />
        )}

        <main
          className={cn(
            'flex-1 overflow-auto pt-16',
            showSidebar && 'transition-all duration-300'
          )}
        >
          <Container className="py-6">
            {children}
          </Container>
        </main>
      </div>

      {showFooter && <Footer />}
    </div>
  );
};

export default MainLayout;
