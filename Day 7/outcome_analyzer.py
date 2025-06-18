import google.generativeai as genai
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
import os
import traceback

# Load environment variables
load_dotenv()

class OutcomeAnalyzer:
    def __init__(self):
        try:
            print("🔧 Initializing OutcomeAnalyzer...")
            
            # Configure Google Generative AI
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            
            # Initialize the language model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ LLM initialized successfully")
            
            # Add Tavily search tool if API key is available
            self.search_tool = None
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if tavily_api_key:
                try:
                    self.search_tool = TavilySearchResults(
                        api_key=tavily_api_key,
                        max_results=3
                    )
                    print("✅ Tavily search tool initialized successfully")
                except Exception as e:
                    print(f"⚠️ Warning: Could not initialize Tavily search tool: {e}")
            else:
                print("⚠️ Warning: TAVILY_API_KEY not found. Web search functionality will be disabled.")
            
            print("✅ OutcomeAnalyzer initialization completed")
            
        except Exception as e:
            print(f"❌ Error during OutcomeAnalyzer initialization: {str(e)}")
            traceback.print_exc()
            raise
    
    def _analyze_content(self, content: str) -> str:
        """Analyzes the content to identify key outcomes and deliverables."""
        try:
            print(f"📊 Analyzing content (length: {len(content)})...")
            prompt = f"""Analyze the following content and identify the key outcomes and deliverables:

            {content}

            Focus on:
            1. What was actually accomplished
            2. Quality of deliverables
            3. Alignment with stated goals
            """
            response = self.model.generate_content(prompt)
            print("✅ Content analysis completed")
            return response.text
        except Exception as e:
            error_msg = f"Error analyzing content: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return error_msg
    
    def _extract_metrics(self, content: str) -> str:
        """Extracts measurable outcomes and metrics from the content."""
        try:
            print(f"📈 Extracting metrics (length: {len(content)})...")
            prompt = f"""Extract measurable outcomes and metrics from the following content:

            {content}

            Look for:
            1. Quantifiable results
            2. Specific achievements
            3. Performance indicators
            """
            response = self.model.generate_content(prompt)
            print("✅ Metrics extraction completed")
            return response.text
        except Exception as e:
            error_msg = f"Error extracting metrics: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return error_msg
    
    def _identify_learnings(self, content: str) -> str:
        """Identifies key learnings and insights from the content."""
        try:
            print(f"🧠 Identifying learnings (length: {len(content)})...")
            prompt = f"""Identify key learnings and insights from the following content:

            {content}

            Focus on:
            1. New skills acquired
            2. Knowledge gained
            3. Personal growth
            4. Challenges overcome
            """
            response = self.model.generate_content(prompt)
            print("✅ Learnings identification completed")
            return response.text
        except Exception as e:
            error_msg = f"Error identifying learnings: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return error_msg
    
    def _search_web(self, query: str) -> str:
        """Searches the web for additional context."""
        if self.search_tool:
            try:
                print(f"🌐 Searching web for: {query}")
                results = self.search_tool.run(query)
                print("✅ Web search completed")
                return f"Web search results for '{query}': {results}"
            except Exception as e:
                error_msg = f"Error searching web: {str(e)}"
                print(f"❌ {error_msg}")
                return error_msg
        else:
            return "Web search not available (TAVILY_API_KEY not configured)"
    
    def analyze_outcome(self, content: str) -> str:
        """
        Analyzes the outcome of a submission or reflection using a structured approach.
        
        Args:
            content (str): The content to analyze (submission or reflection)
            
        Returns:
            str: Detailed outcome analysis
        """
        try:
            print("🔍 Starting comprehensive outcome analysis...")
            print(f"📄 Content length: {len(content)} characters")
            
            # Step 1: Analyze content
            content_analysis = self._analyze_content(content)
            
            # Step 2: Extract metrics
            metrics_analysis = self._extract_metrics(content)
            
            # Step 3: Identify learnings
            learnings_analysis = self._identify_learnings(content)
            
            # Step 4: Search for additional context (if available)
            web_context = ""
            if self.search_tool:
                # Extract key terms for search
                search_query = f"OKR analysis best practices student outcomes"
                web_context = self._search_web(search_query)
            
            # Step 5: Generate comprehensive analysis
            print("📝 Generating final analysis...")
            comprehensive_prompt = f"""Based on the following analyses, provide a comprehensive outcome analysis:

            CONTENT ANALYSIS:
            {content_analysis}

            METRICS ANALYSIS:
            {metrics_analysis}

            LEARNINGS ANALYSIS:
            {learnings_analysis}

            WEB CONTEXT:
            {web_context}

            Please provide your analysis in the following structured format:

            ## Overall Assessment
            [Overall evaluation of the content and outcomes]

            ## Key Deliverables
            [What was actually accomplished based on the content analysis]

            ## Measurable Outcomes
            [Quantifiable results and metrics identified]

            ## Key Learnings
            [Insights and knowledge gained]

            ## Areas for Improvement
            [Suggestions for enhancement based on gaps identified]

            ## Strategic Recommendations
            [Next steps and recommendations for future development]

            ## Impact Assessment
            [Evaluation of current and potential future impact]
            """
            
            print("🤖 Sending final prompt to LLM...")
            final_response = self.model.generate_content(comprehensive_prompt)
            print("✅ Analysis completed successfully!")
            return final_response.text
            
        except Exception as e:
            error_msg = f"Error generating outcome analysis: {str(e)}\n"
            error_msg += "Debug info:\n"
            error_msg += f"Content length: {len(content)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Full traceback:\n{traceback.format_exc()}"
            print(f"❌ {error_msg}")
            return error_msg

def main():
    try:
        # Test the OutcomeAnalyzer
        analyzer = OutcomeAnalyzer()
        
        # Example content
        test_content = """
        Project: Building a Web Application
        
        Deliverables:
        - Created a responsive frontend using React
        - Implemented user authentication
        - Built RESTful API endpoints
        - Deployed to AWS
        
        Learnings:
        - Gained experience with React hooks
        - Learned about JWT authentication
        - Improved understanding of AWS services
        
        Challenges:
        - Initially struggled with state management
        - Had to learn about CORS configuration
        """
        
        analysis = analyzer.analyze_outcome(test_content)
        print("\n=== Outcome Analysis ===")
        print(analysis)
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 