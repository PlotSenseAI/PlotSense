import { Button } from '@/components/ui';
import Container from '@/components/layout/container';
import { EXTERNAL_LINKS } from '@/constants';
import { motion } from 'framer-motion';

const HeroSection: React.FC = () => {
  return (
    <section className="relative min-h-[85vh] flex items-center bg-white dark:bg-gray-900 overflow-hidden pt-20">
      {/* background decorative elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 dark:bg-blue-400/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-purple-400/10 dark:bg-purple-400/10 rounded-full blur-2xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 right-1/3 w-32 h-32 bg-cyan-300/10 dark:bg-cyan-400/10 rounded-full blur-xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <Container className="relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* hero content */}
          <motion.div 
            className="text-gray-900 dark:text-white space-y-8"
            initial={{ opacity: 0, rotateX: -15 }}
            animate={{ opacity: 1, rotateX: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
          >
            <div className="space-y-4">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 backdrop-blur-sm border border-blue-200 dark:border-blue-700">
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">ai-powered data visualization</span>
              </div>
              
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold leading-tight">
                intelligent
                <span className="block text-blue-600 dark:text-blue-400">
                  data visualization
                </span>
                for python
              </h1>
              
              <p className="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-2xl leading-relaxed">
                ai-powered python package that analyzes your pandas dataframes and provides smart visualization recommendations, one-click plot generation, and natural language explanations.
              </p>
            </div>

            {/* cta buttons */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Button 
                size="lg" 
                className="bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 font-semibold px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg shadow-xl"
                onClick={() => window.open(EXTERNAL_LINKS.BINDER_DEMO + '?utm_source=website&utm_medium=hero_button&utm_campaign=try_demo', '_blank')}
              >
                try interactive demo
                <svg className="ml-2 h-4 w-4 sm:h-5 sm:w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2M7 17l3-3m0 0l3-3m-3 3h12" />
                </svg>
              </Button>
              
              <Button 
                variant="outline" 
                size="lg"
                className="border-gray-300 dark:border-gray-600 bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-semibold px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg"
                onClick={() => window.open(EXTERNAL_LINKS.GITHUB_REPO + '?utm_source=website&utm_medium=hero_button&utm_campaign=view_docs', '_blank')}
              >
                view on github
                <svg className="ml-2 h-4 w-4 sm:h-5 sm:w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </Button>
            </div>

          </motion.div>

          {/* hero visual */}
          <motion.div 
            className="relative"
            initial={{ opacity: 0, scale: 0.8, rotateY: 15 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
          >
            <div className="relative z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg rounded-2xl border border-gray-200 dark:border-gray-700 p-8 shadow-2xl">
              {/* mock dashboard */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="h-3 w-3 rounded-full bg-red-400"></div>
                  <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                  <div className="h-3 w-3 rounded-full bg-green-400"></div>
                </div>
                
                <div className="bg-white dark:bg-gray-800 rounded-lg p-4 space-y-3 border border-gray-200 dark:border-gray-600">
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Sample PlotSense Output</div>
                  <div className="rounded-lg overflow-hidden w-full">
                    <img 
                      src="/plots/bar_plot.png" 
                      alt="PlotSense generated bar chart" 
                      className="w-full h-auto max-w-full max-h-48 object-contain bg-white rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            {/* floating elements */}
            <div className="absolute -top-8 -right-8 w-16 h-16 bg-yellow-300/80 rounded-full flex items-center justify-center shadow-lg animate-float">
              <svg className="h-8 w-8 text-yellow-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="absolute -bottom-4 -left-4 w-12 h-12 bg-green-300/80 rounded-full flex items-center justify-center shadow-lg animate-float" style={{ animationDelay: '0.5s' }}>
              <svg className="h-6 w-6 text-green-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  );
};

export default HeroSection;