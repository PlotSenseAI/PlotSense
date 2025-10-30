import textwrap


class PromptBuilder:
    def __init__(self, n_to_request: int):
        self.n_to_request = n_to_request

    def build_prompt(self, df_description: str) -> str:
        return textwrap.dedent(f"""
            You are a data visualization expert analyzing this dataset:

            {df_description}

            Recommend {self.n_to_request} insightful visualizations using matplotlib's plotting functions.
            For each suggestion, follow this exact format:

            Plot Type: <matplotlib function name - exact, like bar, scatter, hist, boxplot, pie, contour, quiver, etc.>
            Variables: <comma-separated list of variables WITH NUMERICAL VARIABLES FIRST>
            Rationale: <1-2 sentences explaining why this visualization is useful>
            ---

            CRITICAL VARIABLE ORDERING RULES:
            1. If a suggestion includes both numerical and categorical variables, NUMERICAL VARIABLES MUST COME FIRST.
            - Correct: "income, gender"  
            - Incorrect: "gender, income"
            2. For plots requiring two numerical variables (e.g., scatter), order by analysis priority (dependent variable first).
            3. For single-variable plots, use natural order (e.g., "age" for a histogram).

            GENERAL RULES FOR ALL PLOT TYPES:
            1. Ensure the plot type is a valid matplotlib function
            2. The plot type must be appropriate for the variables' data types
            3. The number of variables must match what the plot type requires
            4. Variables must exist in the dataset
            5. Never combine incompatible variables
            6. Always specify complete variable sets
            7. Ensure plot type names are in lowercase and match matplotlib's naming conventions eg hist for histogram, bar for barplot
            8. Ensure the common plot types requirements are met including the data types

            COMMON PLOT TYPE REQUIREMENTS (non-exhaustive):
            1. bar: 1 categorical (x) + 1 numerical (y)  → Variables: [numerical], [categorical]
            2. scatter: Exactly 2 numerical → Variables: [independent], [dependent]
            3. hist: Exactly 1 numerical → Variables: [numerical]
            4. boxplot: 1 numerical OR 1 numerical + 1 categorical → Variables: [numerical], [categorical] (if grouped)
            5. pie: Exactly 1 categorical → Variables: [categorical]
            6. line: 1 numerical (y) OR 1 numerical (y) + 1 datetime (x) → Variables: [y], [x] (if applicable)
            7. heatmap: 2 categorical + 1 numerical OR correlation matrix → Variables: [numerical], [categorical], [categorical]
            8. violinplot: Same as boxplot
            9. hexbin: Exactly 2 numerical variables
            10. pairplot: 2+ numerical variables
            11. jointplot: Exactly 2 numerical variables
            12. contour: 2 numerical variables for grid + 1 for values
            13. quiver: 2 numerical variables for grid + 2 for vectors
            14. imshow: 2D array of numerical values
            15. errorbar: 1 numerical (x) + 1 numerical (y) + error values
            16. stackplot: 1 numerical (x) + multiple numerical (y)
            17. stem: 1 numerical (x) + 1 numerical (y)
            18. fill_between: 1 numerical (x) + 2 numerical (y)
            19. pcolormesh: 2D grid of numerical values
            20. polar: Angular and radial coordinates

            If suggesting a plot not listed above, ensure:
            - The function exists in matplotlib
            - Variable types and counts are explicitly compatible
            - The rationale clearly explains the insight provided

            Additional Requirements:
            1. For specialized plots (like quiver, contour), ensure all required components are specified
            2. Consider the statistical properties and relationships of the variables
            3. Suggest plots that would reveal meaningful insights about the data
            4. Include both common and advanced plots when appropriate

            Example CORRECT suggestions (NUMERICAL FIRST):
            Plot Type: boxplot
            Variables: income, gender  
            Rationale: Compares income distribution across genders
            ---
            Plot Type: scatter
            Variables: age, income  
            Rationale: Shows relationship between age and income
            ---
            Plot Type: bar
            Variables: revenue, product_category  
            Rationale: Compares revenue across product categories

            Example INCORRECT suggestions (REJECT THESE):
            Plot Type: boxplot
            Variables: gender, income  # WRONG - categorical listed first
            ---
            Plot Type: scatter
            Variables: price, weight  # WRONG - no clear priority order
            Rationale: Should specify independent/dependent variable order
        """)

