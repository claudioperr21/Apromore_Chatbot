#!/usr/bin/env python3
"""
Test script that demonstrates how to use OpenAI with the Task Mining system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_integration():
    """Test OpenAI integration with the task mining system"""
    
    # Check if OpenAI key is set
    openai_key = os.getenv('SECRET_KEY')
    if not openai_key or openai_key.startswith('sk-proj-'):
        print("✅ OpenAI API key found in environment")
    else:
        print("❌ OpenAI API key not found or invalid")
        return False
    
    try:
        # Test OpenAI import
        import openai
        print("✅ OpenAI library available")
        
        # Set the API key
        openai.api_key = openai_key
        
        # Test a simple API call
        print("🧪 Testing OpenAI API connection...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task mining analyst assistant."},
                {"role": "user", "content": "What are the key metrics to analyze in task mining data?"}
            ],
            max_tokens=100
        )
        
        print("✅ OpenAI API connection successful")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed")
        print("Install it with: pip install openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def create_ai_enhanced_analysis():
    """Create an AI-enhanced analysis function"""
    
    ai_analysis_code = '''
# AI-Enhanced Task Mining Analysis
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('SECRET_KEY')

def get_ai_insights(analysis_data, query):
    """Get AI-powered insights for task mining analysis"""
    try:
        prompt = f"""
        As a task mining analyst, analyze this data and provide insights:
        
        Data: {analysis_data}
        Query: {query}
        
        Provide:
        1. Key findings
        2. Bottlenecks identified
        3. Recommendations for improvement
        4. Process optimization opportunities
        
        Be specific and actionable.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert task mining analyst with deep knowledge of process optimization and business analytics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AI analysis failed: {e}"

def enhance_analysis_with_ai(agent, query):
    """Enhance existing analysis with AI insights"""
    # Get the standard analysis
    result = agent.handle(query)
    
    # Add AI insights if we have text data
    if 'text' in result:
        ai_insights = get_ai_insights(result['text'], query)
        result['ai_insights'] = ai_insights
        result['text'] += f"\n\n🤖 AI-Enhanced Insights:\n{ai_insights}"
    
    return result
'''
    
    with open('ai_enhanced_analysis.py', 'w') as f:
        f.write(ai_analysis_code)
    
    print("✅ Created ai_enhanced_analysis.py with OpenAI integration")

def main():
    print("🤖 OpenAI Integration Test for Task Mining System")
    print("=" * 60)
    
    # Test OpenAI integration
    if test_openai_integration():
        print("\n✅ OpenAI integration successful!")
        
        # Create AI-enhanced analysis module
        create_ai_enhanced_analysis()
        
        print("\n📝 To use AI-enhanced analysis:")
        print("1. Install OpenAI: pip install openai")
        print("2. Import the enhanced module in your analysis")
        print("3. Use get_ai_insights() or enhance_analysis_with_ai() functions")
        
        print("\n🔧 Example usage:")
        print("""
from ai_enhanced_analysis import enhance_analysis_with_ai
from task_mining_multi_agent import SalesforceAgent

# Load your data
agent = SalesforceAgent(your_dataframe)

# Get AI-enhanced analysis
result = enhance_analysis_with_ai(agent, "summary")
print(result['ai_insights'])
        """)
        
    else:
        print("\n❌ OpenAI integration failed")
        print("Please check your API key and internet connection")

if __name__ == "__main__":
    main()
