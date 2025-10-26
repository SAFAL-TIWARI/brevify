"""
Gemini AI Summarizer - Flask Backend
Author: Safal Tiwari
Description: Flask API server that integrates with Google Gemini API for text summarization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize Gemini client with API key from environment variable
# IMPORTANT: Set GEMINI_API_KEY in your .env file or system environment
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def construct_prompt(text, mode, length):
    """
    Constructs a high-quality, mode-specific prompt for Gemini API
    
    Args:
        text (str): The input text to summarize
        mode (str): The summarization mode (paragraph, bullets, eli5, questions, seo)
        length (str): The desired summary length (short, medium, long)
    
    Returns:
        str: A carefully engineered prompt for optimal Gemini performance
    """
    
    # Length specifications
    length_specs = {
        'short': '2-3 sentences (50-75 words)',
        'medium': '4-6 sentences (100-150 words)',
        'long': '7-10 sentences (200-250 words)'
    }
    
    length_instruction = length_specs.get(length, length_specs['medium'])
    
    # Mode-specific prompt engineering
    # Each mode uses the PTCF (Persona, Task, Context, Format) framework for optimal results
    
    if mode == 'paragraph':
        """
        PARAGRAPH MODE: Generates a cohesive, flowing summary in paragraph form
        Persona: Professional summarizer
        Task: Condense while maintaining coherence
        Context: Academic/professional use case
        Format: Single paragraph, natural flow
        """
        prompt = f"""You are a professional text summarizer with expertise in condensing complex information.

Task: Summarize the following text into a single, coherent paragraph.

Length requirement: {length_instruction}

Guidelines:
- Maintain the core message and key points
- Use clear, professional language
- Ensure logical flow and coherence
- Do NOT use bullet points or lists
- Write in complete sentences with smooth transitions

Text to summarize:
\"\"\"
{text}
\"\"\"

Provide only the summary paragraph, nothing else."""

    elif mode == 'bullets':
        """
        BULLET POINTS MODE: Extracts key takeaways in structured list format
        Persona: Information architect
        Task: Extract and organize main points
        Context: Quick-reference format
        Format: Bullet list with parallel structure
        """
        prompt = f"""You are an expert at extracting and organizing key information from text.

Task: Extract the main points from the following text and present them as a clear bullet-point list.

Length requirement: {length_instruction} (distributed across bullet points)

Guidelines:
- Start each bullet with a dash (-)
- Each point should be concise and self-contained
- Use parallel grammatical structure
- Focus on actionable insights and key facts
- Order points by importance (most important first)

Text to analyze:
\"\"\"
{text}
\"\"\"

Provide only the bullet-point list, nothing else."""

    elif mode == 'eli5':
        """
        ELI5 MODE: Explains complex concepts in extremely simple language
        Persona: Patient teacher for young learners
        Task: Simplify without losing meaning
        Context: Educational, accessible to children
        Format: Simple sentences, everyday analogies
        """
        prompt = f"""You are a patient teacher who explains complex topics to 5-year-old children using simple language and relatable examples.

Task: Explain the following text as if you're talking to a 5-year-old child.

Length requirement: {length_instruction}

Guidelines:
- Use VERY simple words (avoid jargon completely)
- Use everyday analogies and examples
- Break down complex ideas into small, digestible pieces
- Be warm and encouraging in tone
- Avoid technical terms unless absolutely necessary (and explain them simply)

Text to explain:
\"\"\"
{text}
\"\"\"

Provide only the ELI5 explanation, nothing else."""

    elif mode == 'questions':
        """
        KEY QUESTIONS MODE: Identifies the main questions answered by the text
        Persona: Critical analyst
        Task: Extract implicit and explicit questions
        Context: Research/study guide preparation
        Format: Numbered question list
        """
        prompt = f"""You are a critical analyst who identifies the core questions that a piece of text addresses.

Task: Analyze the following text and generate 3-5 key questions that this text answers or addresses.

Guidelines:
- Each question should be clear, specific, and insightful
- Questions should capture the main themes and arguments
- Use proper question format (Who/What/Where/When/Why/How)
- Number each question (1., 2., 3., etc.)
- Questions should be standalone (understandable without reading the text)
- Prioritize questions by importance

Text to analyze:
\"\"\"
{text}
\"\"\"

Provide only the numbered list of questions, nothing else."""

    elif mode == 'seo':
        """
        SEO META DESCRIPTION MODE: Creates search-engine optimized summaries
        Persona: SEO copywriter
        Task: Craft compelling, keyword-rich meta description
        Context: Web content optimization for search visibility
        Format: Single paragraph, 150-155 characters max
        """
        prompt = f"""You are an expert SEO copywriter specializing in meta descriptions for web content.

Task: Create a compelling SEO meta description for the following text.

CRITICAL Requirements:
- Maximum length: 155 characters (STRICT LIMIT)
- Include relevant keywords naturally
- Make it engaging and click-worthy
- Accurately represent the content
- Use active voice
- End with a call-to-action or value proposition when possible

Text to summarize:
\"\"\"
{text}
\"\"\"

Provide ONLY the meta description (150-155 characters max), nothing else. No explanations or additional text."""

    else:
        # Fallback to paragraph mode if mode is unrecognized
        return construct_prompt(text, 'paragraph', length)
    
    return prompt


@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Main API endpoint for text summarization
    
    Expected JSON payload:
    {
        "text": "The text to summarize...",
        "mode": "paragraph|bullets|eli5|questions|seo",
        "length": "short|medium|long"
    }
    
    Returns:
    {
        "summary": "The generated summary...",
        "mode": "paragraph",
        "length": "medium"
    }
    
    Error response:
    {
        "error": "Error message description"
    }
    """
    try:
        # Parse incoming JSON data
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text = data.get('text', '').strip()
        mode = data.get('mode', 'paragraph').lower()
        length = data.get('length', 'medium').lower()
        
        # Input validation
        if not text:
            return jsonify({'error': 'Text field is required'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text must be at least 50 characters long'}), 400
        
        if mode not in ['paragraph', 'bullets', 'eli5', 'questions', 'seo']:
            return jsonify({'error': 'Invalid mode specified'}), 400
        
        if length not in ['short', 'medium', 'long']:
            return jsonify({'error': 'Invalid length specified'}), 400
        
        # Construct the specialized prompt based on mode and length
        prompt = construct_prompt(text, mode, length)
        
        # Call Gemini API using the free-tier model (gemini-2.0-flash-lite for best free-tier performance)
        # Alternative free models: 'gemini-1.5-flash', 'gemini-1.5-flash-8b'
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',  # Fast, free-tier model
            contents=prompt,
            config={
                'temperature': 0.3,  # Lower temperature for more focused, consistent summaries
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )
        
        # Extract the generated summary text
        summary = response.text.strip()
        
        # Return successful response
        return jsonify({
            'summary': summary,
            'mode': mode,
            'length': length
        }), 200
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error in /summarize endpoint: {str(e)}")
        
        # Return error response
        return jsonify({
            'error': f'An error occurred while generating the summary: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'Gemini AI Summarizer',
        'version': '1.0.0'
    }), 200


if __name__ == '__main__':
    # Run the Flask development server
    # For production, use a proper WSGI server like Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
