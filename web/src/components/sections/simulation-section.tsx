import Container from '@/components/layout/container';
import { Button } from '@/components/ui';
import { EXTERNAL_LINKS } from '@/constants';
import { motion } from 'framer-motion';

interface SimulationStep {
  step: number;
  title: string;
  description: string;
  plotType: string;
  plotImage: string;
  code: string;
}

const simulationSteps: SimulationStep[] = [
  {
    step: 1,
    title: 'load your dataframe',
    description: 'import plotsense and load your pandas dataframe from any source - csv, json, database, or api.',
    plotType: 'Data Loading',
    plotImage: '/plots/scatter_plot.png',
    code: `import plotsense as ps
import pandas as pd

# load your dataset
df = pd.read_csv('your_data.csv')
print(f"Dataset shape: {df.shape}")`
  },
  {
    step: 2,
    title: 'get ai recommendations',
    description: 'plotsense analyzes your data using ensemble ai models and provides ranked visualization suggestions.',
    plotType: 'AI Analysis',
    plotImage: '/plots/histogram_plot.png',
    code: `# get top 5 recommendations
recommendations = ps.recommender(df, n=5)

# view recommendations with scores
print(recommendations)`
  },
  {
    step: 3,
    title: 'generate professional plots',
    description: 'create professional matplotlib figures with one function call. supports customization and returns figure objects.',
    plotType: 'Plot Generation',
    plotImage: '/plots/bar_plot.png',
    code: `# generate recommended plot
fig = ps.plotgen(df, recommendations.iloc[0])

# save or customize further
fig.savefig('my_plot.png', dpi=300)`
  },
  {
    step: 4,
    title: 'get ai explanations',
    description: 'receive detailed natural language explanations that help you understand patterns and insights in your visualizations.',
    plotType: 'AI Insights',
    plotImage: '/plots/boxplot.png',
    code: `# get ai explanation
explanation = ps.explainer(fig)

print(explanation)
# "This bar chart reveals significant patterns..."`
  }
];

const SimulationSection: React.FC = () => {
  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-900 overflow-hidden">
      <Container className="overflow-hidden">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, type: "spring", stiffness: 80 }}
          viewport={{ once: true }}
        >
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm font-medium mb-4">
            live simulation
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6 leading-tight">
            see plotsense in action
            <span className="block text-green-600 dark:text-green-400">with real examples</span>
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            explore how plotsense transforms raw data into insights through ai-powered visualization recommendations and explanations.
          </p>
        </motion.div>

        {/* simulation steps */}
        <div className="space-y-16">
          {simulationSteps.map((item, index) => (
            <motion.div
              key={index}
              className={`flex flex-col lg:flex-row items-start lg:items-center gap-8 lg:gap-12 ${
                index % 2 === 1 ? 'lg:flex-row-reverse' : ''
              }`}
              initial={{
                opacity: 0,
                x: index % 2 === 0 ? -100 : 100,
                rotateZ: index % 2 === 0 ? -3 : 3
              }}
              whileInView={{
                opacity: 1,
                x: 0,
                rotateZ: 0
              }}
              transition={{
                duration: 0.8,
                delay: index * 0.2,
                type: "spring",
                stiffness: 60
              }}
              viewport={{ once: true, margin: "-100px" }}
            >
              {/* content */}
              <div className="flex-1 w-full lg:w-auto space-y-6 min-w-0">
                <div className="flex items-center space-x-3 sm:space-x-4">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white font-bold text-base sm:text-lg shadow-lg flex-shrink-0">
                    {item.step}
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100 capitalize leading-tight">
                      {item.title}
                    </h3>
                    <p className="text-sm sm:text-base text-green-600 dark:text-green-400 font-medium">
                      {item.plotType}
                    </p>
                  </div>
                </div>

                <p className="text-sm sm:text-base md:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                  {item.description}
                </p>

                {/* code block */}
                <div className="bg-gray-900 dark:bg-gray-800 rounded-lg p-3 sm:p-4 border border-gray-700 w-full max-w-full overflow-hidden">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs sm:text-sm text-gray-400">Python</span>
                    <div className="flex space-x-1 sm:space-x-2">
                      <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-red-400"></div>
                      <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-yellow-400"></div>
                      <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-green-400"></div>
                    </div>
                  </div>
                  <div className="overflow-x-auto max-w-full">
                    <pre className="text-xs sm:text-sm text-gray-300 font-mono leading-relaxed whitespace-pre-wrap break-words min-w-0">
                      <code className="break-words">{item.code}</code>
                    </pre>
                  </div>
                </div>
              </div>

              {/* plot visualization */}
              <div className="flex-1 w-full max-w-lg mx-auto">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 sm:p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                  <div className="text-center mb-4">
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      PlotSense Output
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {item.plotType} Result
                    </p>
                  </div>

                  <div className="rounded-lg overflow-hidden bg-white w-full">
                    <img
                      src={item.plotImage}
                      alt={`PlotSense ${item.plotType} example`}
                      className="w-full h-auto max-w-full object-contain"
                    />
                  </div>

                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* bottom cta */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0, y: 100, rotateX: 20 }}
          whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 1, type: "spring", stiffness: 50 }}
          viewport={{ once: true }}
        >
          <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-gray-800 dark:to-green-900/20 rounded-3xl p-8 lg:p-12 border border-green-100 dark:border-gray-700">
            <div className="max-w-3xl mx-auto space-y-6">
              <h3 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100">
                ready to experience plotsense?
              </h3>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                try the interactive demo and see how ai can transform your data visualization workflow
              </p>
              <div className="pt-4">
                <Button
                  size="lg"
                  className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 text-lg font-semibold"
                  onClick={() => window.open(EXTERNAL_LINKS.BINDER_DEMO + '?utm_source=website&utm_medium=simulation_section&utm_campaign=try_demo', '_blank')}
                >
                  try interactive demo
                  <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2M7 17l3-3m0 0l3-3m-3 3h12" />
                  </svg>
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
};

export default SimulationSection;
