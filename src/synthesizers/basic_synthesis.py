"""
Basic synthesis module for generating readable summaries from document structure.

This module creates a programmatic summary from a processed document and then
refines it with AI to improve readability and cohesion.
"""
from typing import List

from src.models.document import Document, Paragraph


def generate_transcript(document: Document) -> str:
    """
    Generate a programmatic transcript from the document structure.
    
    This function creates a structured summary using only the gists of paragraphs
    and their structural/argument roles.
    
    Args:
        document: The processed document with gists and tags
        
    Returns:
        str: A structured transcript of the document
    """
    if not document.paragraphs:
        return "No content to summarize."
    
    transcript_parts = []
    
    # Add document title/metadata
    title = document.metadata.get('title', 'Untitled Document')
    transcript_parts.append(f"# {title}\n")
    
    # Find thesis (abstract/introduction) paragraphs
    thesis_paragraphs = []
    for p in document.paragraphs:
        # Skip very short paragraphs and titles
        if len(p.text.split()) < 5:
            continue
            
        # Check for thesis paragraphs (by tag or keywords)
        if (p.structural_tag.name == "THESIS" or
            "abstract" in p.text.lower() or
            "introduction" in p.text.lower()):
            thesis_paragraphs.append(p)
    
    # If we found thesis paragraphs, add them
    if thesis_paragraphs:
        transcript_parts.append("## Main Thesis")
        for p in thesis_paragraphs[:2]:  # Limit to first two thesis paragraphs
            transcript_parts.append(p.gist)
        transcript_parts.append("")
    
    # Add main points
    main_points = []
    for p in document.paragraphs:
        # Skip very short paragraphs and already used thesis paragraphs
        if len(p.text.split()) < 5 or p in thesis_paragraphs:
            continue
            
        # Check for point paragraphs
        if p.structural_tag.name == "POINT" and p.argument_role.name != "UNKNOWN":
            main_points.append(p)
    
    if main_points:
        transcript_parts.append("## Key Points")
        for i, p in enumerate(main_points, 1):
            if p.argument_role.name == "COUNTERPOINT":
                transcript_parts.append(f"* 🔄 Counterpoint: {p.gist}")
            elif p.argument_role.name == "SUPPORTING":
                transcript_parts.append(f"* ✓ {p.gist}")
            else:
                transcript_parts.append(f"* {p.gist}")
        transcript_parts.append("")
    
    # Add examples and evidence
    examples = []
    for p in document.paragraphs:
        if p.structural_tag.name == "EXAMPLE" or "example" in p.text.lower():
            examples.append(p)
    
    if examples:
        transcript_parts.append("## Supporting Evidence")
        for p in examples:
            transcript_parts.append(f"* {p.gist}")
        transcript_parts.append("")
    
    # Add conclusion
    conclusions = []
    for p in document.paragraphs:
        if (p.structural_tag.name == "CONCLUSION" or 
            "conclusion" in p.text.lower() or
            "in summary" in p.text.lower()):
            conclusions.append(p)
    
    if conclusions:
        transcript_parts.append("## Conclusion")
        for p in conclusions:
            transcript_parts.append(p.gist)
    
    return "\n".join(transcript_parts)


def refine_transcript(transcript: str, api_client=None) -> str:
    """
    Refine the transcript using AI to improve readability.
    
    If no API client is provided, returns the transcript as-is.
    
    Args:
        transcript: The programmatically generated transcript
        api_client: An optional OpenAI client for refinement
        
    Returns:
        str: A more readable and cohesive summary
    """
    if not api_client:
        return transcript
    
    try:
        # Create a prompt for coherent summary
        prompt = f"""
        Below is a structured transcript of a document:
        
        {transcript}
        
        Please transform this into a cohesive, readable summary that flows naturally. 
        Maintain all the key points, supporting evidence, and conclusions, but make 
        it read like a fluid document rather than a structured outline.
        
        Use plain language, connect ideas with appropriate transitions, and ensure 
        the overall narrative is compelling and clear. Keep the same information and 
        organization, just make it more readable.
        
        Keep your summary concise but complete.
        """
        
        response = api_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at creating coherent summaries while preserving key information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        refined_summary = response.choices[0].message.content.strip()
        return refined_summary
        
    except Exception as e:
        print(f"Error refining transcript: {str(e)}")
        # Fall back to the original transcript
        return transcript