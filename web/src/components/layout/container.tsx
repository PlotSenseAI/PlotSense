import { cn } from '@/lib/utils';

interface ContainerProps {
  children?: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  center?: boolean;
}

const Container: React.FC<ContainerProps> = ({
  children,
  className,
  size = 'lg',
  center = true,
}) => {
  const sizeClasses = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-5xl',
    xl: 'max-w-6xl',
    full: 'max-w-full',
  };

  return (
    <div
      className={cn(
        'w-full px-6 sm:px-8 md:px-6',
        sizeClasses[size],
        center && 'mx-auto',
        className
      )}
    >
      {children}
    </div>
  );
};

export default Container;
