import { Button } from '@/components/ui';
import Container from '@/components/layout/container';
import { EXTERNAL_LINKS } from '@/constants';
import { motion } from 'framer-motion';

interface Step {
  number: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const steps: Step[] = [
  {
    number: '01',
    title: 'load your dataframe',
    description: 'import plotsense and load your pandas dataframe. works with any dataset loaded via pandas from csv, json, xlsx, or database connections.',
    color: 'from-blue-500 to-blue-600',
    icon: (
      <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    number: '02',
    title: 'get ai recommendations',
    description: 'call ps.recommender(df) to analyze your dataframe using ensemble ai models. returns ranked suggestions with ensemble scores and model agreement metrics.',
    color: 'from-purple-500 to-purple-600',
    icon: (
      <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    number: '03',
    title: 'generate matplotlib plots',
    description: 'use ps.plotgen(df, suggestions) to create professional matplotlib figures. supports customization and returns figure objects for further modification.',
    color: 'from-green-500 to-green-600',
    icon: (
      <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    number: '04',
    title: 'get ai explanations',
    description: 'call ps.explainer(fig) to receive detailed markdown explanations. ai analyzes your plot and provides insights, patterns, and statistical interpretations.',
    color: 'from-orange-500 to-orange-600',
    icon: (
      <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
  },
];

const HowItWorksSection: React.FC = () => {
  return (
    <section className="py-20 bg-white dark:bg-gray-800">
      <Container>
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -50, rotateX: 45 }}
          whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 1.2, type: "spring", stiffness: 60 }}
          viewport={{ once: true }}
        >
          <motion.div
            className="inline-flex items-center px-4 py-2 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-medium mb-4"
            initial={{ scale: 0, rotate: 360 }}
            whileInView={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, delay: 0.2, type: "spring", stiffness: 150 }}
            viewport={{ once: true }}
          >
            how it works
          </motion.div>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            from dataframe to insights in
            <span className="block text-blue-600 dark:text-blue-400">4 simple steps</span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            plotsense integrates seamlessly with your existing python data science workflow,
            making ai-powered visualization accessible to all skill levels.
          </p>
        </motion.div>

        {/* workflow steps with connecting lines */}
        <div className="relative mb-16">
          {/* desktop horizontal flow */}
          <div className="hidden lg:block">
            <div className="grid lg:grid-cols-4 gap-8 relative">
              {/* connecting line background */}
              <div className="absolute top-24 left-16 right-16 h-0.5 bg-gray-200 dark:bg-gray-700 z-0"></div>

              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  className="relative"
                  initial={{
                    opacity: 0,
                    y: 100,
                    scale: 0.5,
                    rotateX: 90
                  }}
                  whileInView={{
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    rotateX: 0
                  }}
                  transition={{
                    duration: 0.8,
                    delay: index * 0.3,
                    type: "spring",
                    stiffness: 80,
                    damping: 15
                  }}
                  viewport={{ once: true }}
                >
                  {/* step node */}
                  <div className="relative z-10 flex flex-col items-center">
                    <motion.div
                      className={`w-16 h-16 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center text-white font-bold text-lg shadow-lg mb-4`}
                      whileHover={{
                        scale: 1.2,
                        rotate: 10,
                        boxShadow: "0 20px 40px rgba(0,0,0,0.3)",
                        transition: { duration: 0.3 }
                      }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {step.number}
                    </motion.div>

                    <motion.div
                      className={`w-10 h-10 rounded-lg bg-gradient-to-r ${step.color} flex items-center justify-center text-white mb-4 shadow-md`}
                      whileHover={{
                        scale: 1.1,
                        rotate: -5,
                        transition: { duration: 0.2 }
                      }}
                    >
                      {step.icon}
                    </motion.div>

                    <div className="text-center space-y-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 capitalize">
                        {step.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed max-w-xs">
                        {step.description}
                      </p>
                    </div>

                    {/* arrow connector */}
                    {index < steps.length - 1 && (
                      <motion.div
                        className="absolute top-8 -right-4 z-20"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.6, delay: index * 0.3 + 0.5 }}
                        viewport={{ once: true }}
                      >
                        <svg className="w-8 h-8 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* mobile vertical flow */}
          <div className="lg:hidden space-y-8">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className="relative"
                initial={{
                  opacity: 0,
                  x: index % 2 === 0 ? -50 : 50,
                  rotateZ: index % 2 === 0 ? -10 : 10
                }}
                whileInView={{
                  opacity: 1,
                  x: 0,
                  rotateZ: 0
                }}
                transition={{
                  duration: 0.7,
                  delay: index * 0.2,
                  type: "spring",
                  stiffness: 100
                }}
                viewport={{ once: true }}
              >
                <div className="flex items-start space-x-4">
                  <div className="flex flex-col items-center">
                    <motion.div
                      className={`w-12 h-12 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center text-white font-bold shadow-lg`}
                      whileHover={{ scale: 1.15, rotate: 5 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      {step.number}
                    </motion.div>
                    {index < steps.length - 1 && (
                      <motion.div
                        className="w-0.5 h-16 bg-gray-200 dark:bg-gray-700 mt-4"
                        initial={{ height: 0 }}
                        whileInView={{ height: "4rem" }}
                        transition={{ duration: 0.8, delay: index * 0.2 + 0.5 }}
                        viewport={{ once: true }}
                      ></motion.div>
                    )}
                  </div>

                  <div className="flex-1 pt-2">
                    <motion.div
                      className={`w-8 h-8 rounded-lg bg-gradient-to-r ${step.color} flex items-center justify-center text-white mb-3 shadow-md`}
                      whileHover={{ scale: 1.1, rotate: -5 }}
                    >
                      {step.icon}
                    </motion.div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 capitalize mb-2">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* demo section */}
        <motion.div
          className="bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-3xl p-8 lg:p-12 text-center"
          initial={{
            opacity: 0,
            scale: 0.8,
            rotateX: -20,
            y: 100
          }}
          whileInView={{
            opacity: 1,
            scale: 1,
            rotateX: 0,
            y: 0
          }}
          transition={{
            duration: 1,
            type: "spring",
            stiffness: 70,
            damping: 15
          }}
          viewport={{ once: true }}
        >
          <div className="max-w-2xl mx-auto space-y-6">
            <motion.div
              className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 text-sm font-medium"
              initial={{ scale: 0, rotate: -180 }}
              whileInView={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.8, delay: 0.3, type: "spring", stiffness: 120 }}
              viewport={{ once: true }}
            >
              see it in action
            </motion.div>

            <motion.h3
              className="text-3xl font-bold text-gray-900 dark:text-gray-100"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              viewport={{ once: true }}
            >
              ready to enhance your data analysis?
            </motion.h3>

            <motion.p
              className="text-lg text-gray-600 dark:text-gray-300"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
              viewport={{ once: true }}
            >
              join data scientists and researchers who use plotsense to accelerate
              their exploratory data analysis with ai-powered insights.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center pt-4"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.9, type: "spring", stiffness: 100 }}
              viewport={{ once: true }}
            >
              <motion.div
                whileHover={{ scale: 1.05, rotate: 1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  size="lg"
                  className="px-8 py-4 text-lg font-semibold"
                  onClick={() => window.open(EXTERNAL_LINKS.BINDER_DEMO + '?utm_source=website&utm_medium=how_it_works&utm_campaign=try_now', '_blank')}
                >
                  try it now
                  <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-2M7 17l3-3m0 0l3-3m-3 3h12" />
                  </svg>
                </Button>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.05, rotate: -1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant="outline"
                  size="lg"
                  className="px-8 py-4 text-lg font-semibold"
                  onClick={() => window.open(EXTERNAL_LINKS.GITHUB_REPO + '?utm_source=website&utm_medium=how_it_works&utm_campaign=view_examples', '_blank')}
                >
                  view examples
                  <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
};

export default HowItWorksSection;
