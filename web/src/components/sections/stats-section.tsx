import Container from '@/components/layout/container';
import { motion } from 'framer-motion';

interface Stat {
  number: string;
  label: string;
  description: string;
  icon: React.ReactNode;
}

const stats: Stat[] = [
  {
    number: '8',
    label: 'plot types supported',
    description: 'scatter, bar, histogram, boxplot, violin, pie, hexbin plots',
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    number: '3',
    label: 'core ai models',
    description: 'llama-3.3-70b and llama-3.1-8b via groq api ensemble',
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    number: 'python 3.8+',
    label: 'compatible versions',
    description: 'works with modern python data science stack',
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
  },
  {
    number: 'open source',
    label: 'apache 2.0 license',
    description: 'free to use for research and commercial projects',
    icon: (
      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
  },
];

const testimonials = [
  {
    quote: "plotsense accelerates our exploratory data analysis. the ensemble ai recommendations help us discover visualization patterns we might have missed.",
    author: "dr. james ademoye",
    role: "data scientist & researcher",
    avatar: "JA",
  },
  {
    quote: "the natural language explanations are perfect for communicating insights to stakeholders. saves hours of documentation work.",
    author: "chike isaac",
    role: "machine learning engineer",
    avatar: "CI",
  },
  {
    quote: "integrates seamlessly with our jupyter notebook workflow. the matplotlib figure output makes customization easy.",
    author: "laura durk",
    role: "data analyst",
    avatar: "LD",
  },
];

const StatsSection: React.FC = () => {
  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white relative overflow-hidden">
      {/* background decorative elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 dark:bg-blue-400/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-500/5 dark:bg-purple-400/5 rounded-full blur-2xl"></div>
      </div>

      <Container className="relative z-10">
        {/* stats grid */}
        <div className="mb-20">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, clipPath: "circle(0% at 50% 50%)" }}
            whileInView={{ opacity: 1, clipPath: "circle(150% at 50% 50%)" }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 backdrop-blur-sm border border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300 text-sm font-medium mb-4">
              trusted by professionals
            </div>
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              join the data visualization
              <span className="block text-blue-600 dark:text-blue-400">
                revolution
              </span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {stats.map((stat, index) => (
              <motion.div 
                key={index} 
                className="text-center group"
                initial={{ 
                  opacity: 0, 
                  scale: 0,
                  rotate: 180
                }}
                whileInView={{ 
                  opacity: 1, 
                  scale: 1,
                  rotate: 0
                }}
                transition={{ 
                  duration: 0.8, 
                  delay: index * 0.15,
                  type: "spring",
                  stiffness: 100,
                  damping: 10
                }}
                viewport={{ once: true }}
                whileHover={{ 
                  scale: 1.1, 
                  rotate: 5,
                  transition: { duration: 0.2 }
                }}
              >
                <div className="space-y-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-2xl text-white group-hover:scale-110 transition-transform duration-300">
                    {stat.icon}
                  </div>
                  <div className="space-y-2">
                    <div className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-blue-600 dark:text-blue-400">
                      {stat.number}
                    </div>
                    <div className="text-base sm:text-lg md:text-xl font-semibold capitalize text-gray-900 dark:text-gray-100">{stat.label}</div>
                    <div className="text-gray-600 dark:text-gray-300 text-xs sm:text-sm">{stat.description}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* testimonials */}
        <motion.div
          initial={{ opacity: 0, rotateX: 30, scale: 0.9 }}
          whileInView={{ opacity: 1, rotateX: 0, scale: 1 }}
          transition={{ duration: 1, type: "spring", stiffness: 80 }}
          viewport={{ once: true }}
        >
          <motion.div 
            className="text-center mb-12"
            initial={{ opacity: 0, z: -100 }}
            whileInView={{ opacity: 1, z: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <h3 className="text-3xl font-bold mb-4 text-gray-900 dark:text-gray-100">what data professionals say</h3>
            <p className="text-gray-600 dark:text-gray-300 text-lg">experiences from researchers and data scientists using plotsense</p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div 
                key={index} 
                className="bg-white dark:bg-gray-800 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 dark:border-gray-700 group hover:shadow-lg transition-all duration-300"
                initial={{ 
                  opacity: 0, 
                  rotateY: index % 2 === 0 ? -30 : 30,
                  scale: 0.7,
                  z: -50
                }}
                whileInView={{ 
                  opacity: 1, 
                  rotateY: 0,
                  scale: 1,
                  z: 0
                }}
                transition={{ 
                  duration: 0.9, 
                  delay: index * 0.2,
                  type: "spring",
                  stiffness: 70,
                  damping: 12
                }}
                viewport={{ once: true }}
                whileHover={{ 
                  y: -8,
                  rotateY: 5,
                  scale: 1.02,
                  transition: { duration: 0.3 }
                }}
              >
                <div className="space-y-6">
                  <div className="text-lg italic text-gray-700 dark:text-gray-300 leading-relaxed">
                    "{testimonial.quote}"
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-semibold capitalize text-gray-900 dark:text-gray-100">{testimonial.author}</div>
                      <div className="text-gray-600 dark:text-gray-400 text-sm capitalize">{testimonial.role}</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

      </Container>
    </section>
  );
};

export default StatsSection;