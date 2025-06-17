import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class OutcomeAnalyzer:
    def __init__(self):
        try:
            # Initialize Gemini AI model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Define the analysis template
            self.template = """
            You are an OKR (Objectives and Key Results) analyst. Based on the following 5-pillar resume validation results, provide a detailed outcome analysis.

            Provide a detailed analysis with the following sections:

            Overall Achievement Score:
            - Score based on pillars present (each pillar = 20%)
            - Qualitative assessment

            Strengths Analysis:
            - Evaluation of present pillars
            - Positive implementation aspects

            Areas for Improvement:
            - Gaps from missing pillars
            - Needed improvements

            Strategic Recommendations:
            - Steps to add missing pillars
            - Ways to strengthen existing ones

            Impact Assessment:
            - Current impact evaluation
            - Potential future impact
            """
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise
    
    def analyze_outcome(self, pillars_present, pillars_missing):
        """
        Analyze the outcome of the 5-pillar based resume validation
        
        Args:
            pillars_present (list): List of pillars found in the resume
            pillars_missing (list): List of pillars missing from the resume
            
        Returns:
            str: Detailed outcome analysis
        """
        try:
            # Convert lists to comma-separated strings
            present_str = ", ".join(pillars_present) if pillars_present else "None"
            missing_str = ", ".join(pillars_missing) if pillars_missing else "None"
            
            # Format the prompt
            prompt = self.template.format(
                pillars_present=present_str,
                pillars_missing=missing_str
            )
            
            # Generate the analysis
            response = self.model.generate_content(prompt)
            
            # Return the formatted text
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating outcome analysis: {str(e)}\n"
            error_msg += "Debug info:\n"
            error_msg += f"Present pillars: {present_str}\n"
            error_msg += f"Missing pillars: {missing_str}\n"
            return error_msg

def main():
    try:
        # Test the OutcomeAnalyzer
        analyzer = OutcomeAnalyzer()
        
        # Example usage
        present_pillars = ["CLT", "CFC", "SCD"]
        missing_pillars = ["IIPC", "SRI"]
        
        analysis = analyzer.analyze_outcome(present_pillars, missing_pillars)
        print("\n=== Outcome Analysis ===")
        print(analysis)
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 