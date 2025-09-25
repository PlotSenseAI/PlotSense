import { env } from '@/config/env';
import { cn } from '@/lib/utils';
import Container from './container';

interface FooterProps {
  className?: string;
}

const Footer: React.FC<FooterProps> = ({ className }) => {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className={cn(
        'border-t bg-background',
        className
      )}
    >
      <Container>
        <div className="flex flex-col items-center justify-between py-6 md:flex-row">
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span>© {currentYear} {env.app.name}</span>
            <span>•</span>
            <span>v{env.app.version}</span>
          </div>
          
          <div className="mt-4 flex items-center space-x-4 text-sm text-muted-foreground md:mt-0">
            <a
              href="https://github.com/christianchimezie/PlotSenseAI"
              className="hover:text-foreground transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              github
            </a>
            <span>•</span>
            <a
              href="/docs"
              className="hover:text-foreground transition-colors"
            >
              documentation
            </a>
            <span>•</span>
            <a
              href="/support"
              className="hover:text-foreground transition-colors"
            >
              support
            </a>
          </div>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;