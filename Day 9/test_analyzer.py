#!/usr/bin/env python3
"""
Simple test script for OutcomeAnalyzer
"""

from outcome_analyzer import OutcomeAnalyzer

def test_analyzer():
    """Test the OutcomeAnalyzer with sample content"""
    try:
        print("🧪 Testing OutcomeAnalyzer...")
        
        # Initialize analyzer
        analyzer = OutcomeAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Test content
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
        
        print("📝 Running analysis...")
        result = analyzer.analyze_outcome(test_content)
        
        print("\n" + "="*50)
        print("ANALYSIS RESULT:")
        print("="*50)
        print(result)
        print("="*50)
        
        print("✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_analyzer() 