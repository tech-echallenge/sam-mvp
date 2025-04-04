"""
Text processor module for AI-based analysis of document structure and content.

This module processes document paragraphs to identify structural elements,
argument roles, and generate concise gists using OpenAI's API.
"""
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import time
from dotenv import load_dotenv
from openai import OpenAI

from src.models.document import Document, Paragraph, StructuralTag, ArgumentRole

# Load environment variables from .env file
load_dotenv()


class TextProcessor:
    """
    Processes document text to extract structure, roles, and gists using OpenAI API.
    
    This class provides methods to analyze paragraphs within a document,
    determining their structural role (thesis, point, example, conclusion),
    argument role (supporting, counterpoint, elaboration), and creating
    concise summaries (gists) of the content.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the text processor with API key.
        
        Args:
            api_key: Optional API key for OpenAI service, defaults to env variable
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it or set OPENAI_API_KEY env variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
    
    def process_document(self, document: Document) -> Document:
        """
        Process an entire document, analyzing all paragraphs.
        
        This method goes through each paragraph in the document, identifying
        structural tags, argument roles, and generating gists for each.
        
        Args:
            document: The document to process
            
        Returns:
            Document: The processed document with enhanced paragraph metadata
        """
        # Process each paragraph in the document
        for i, paragraph in enumerate(document.paragraphs):
            # Skip very short paragraphs or titles
            if len(paragraph.text.split()) < 3:
                continue
                
            # Add context about position in document
            position_context = self._get_position_context(i, len(document.paragraphs))
            
            # Get AI analysis for the paragraph
            structural_tag, argument_role, gist = self._analyze_paragraph(
                paragraph.text, 
                position_context,
                document.metadata.get('title', '')
            )
            
            # Update the paragraph with the analysis
            paragraph.structural_tag = structural_tag
            paragraph.argument_role = argument_role
            paragraph.gist = gist
            
            # Add a small delay to avoid rate limits with the API
            time.sleep(0.5)
        
        return document
    
    def _analyze_paragraph(self, 
                          text: str, 
                          position_context: str,
                          document_title: str) -> Tuple[StructuralTag, ArgumentRole, str]:
        """
        Analyze a single paragraph using OpenAI to identify its characteristics.
        
        Args:
            text: The paragraph text
            position_context: Information about paragraph's position in document
            document_title: Title of the document for context
            
        Returns:
            Tuple containing:
                - StructuralTag: The structural role of the paragraph
                - ArgumentRole: The argument role of the paragraph
                - str: A concise gist of the paragraph's content
        """
        # Construct a prompt for the AI
        prompt = f"""
        Analyze the following paragraph from a document titled "{document_title}".
        This paragraph appears at the {position_context} of the document.
        
        Paragraph:
        {text}
        
        1. Identify the structural role of this paragraph:
           - THESIS: Main argument or claim of the document
           - POINT: Key supporting evidence or claim
           - EXAMPLE: Illustrative instance or detailed evidence
           - CONCLUSION: Final synthesis, summary, or implication
        
        2. Identify the argument role of this paragraph:
           - SUPPORTING: Directly supports the main thesis
           - COUNTERPOINT: Presents an opposing view or limitation
           - ELABORATION: Explains or adds detail to a previous point
        
        3. Create a concise 1-2 sentence gist of this paragraph that captures its core meaning.
        
        Respond in JSON format:
        {{
            "structural_tag": "THESIS|POINT|EXAMPLE|CONCLUSION",
            "argument_role": "SUPPORTING|COUNTERPOINT|ELABORATION",
            "gist": "Concise summary here"
        }}
        """
        
        try:
            # Make OpenAI API call using the newer Client interface
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use appropriate model for your needs
                messages=[
                    {"role": "system", "content": "You are a document analysis assistant that identifies the structural elements of text and creates concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1  # Keep temperature low for more deterministic outputs
            )
            
            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            
            # The result might have markdown formatting, so we need to extract just the JSON part
            # Find JSON content between backticks or braces
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```|```\s*(.*?)\s*```|(\{.*\})', result_text, re.DOTALL)
            
            if json_match:
                # Use the first non-None group
                json_str = next(group for group in json_match.groups() if group is not None)
                result = json.loads(json_str)
            else:
                # If we can't find JSON with regex, try to parse the whole response
                result = json.loads(result_text)
            
            # Convert string values to enum types
            structural_tag = StructuralTag[result["structural_tag"]]
            argument_role = ArgumentRole[result["argument_role"]]
            gist = result["gist"]
            
            return structural_tag, argument_role, gist
            
        except Exception as e:
            # In case of error, return defaults with error message
            print(f"Error processing paragraph: {str(e)}")
            return StructuralTag.UNKNOWN, ArgumentRole.UNKNOWN, f"Error: {str(e)}"
    
    def _get_position_context(self, index: int, total_paragraphs: int) -> str:
        """
        Determine the position context of a paragraph within the document.
        
        Args:
            index: The index of the paragraph
            total_paragraphs: The total number of paragraphs in the document
            
        Returns:
            str: A description of the paragraph's position ("beginning", "middle", "end")
        """
        if index < 2:
            return "beginning"
        elif index >= total_paragraphs - 2:
            return "end"
        else:
            return "middle"