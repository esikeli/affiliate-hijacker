import os
import logging
import json
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

def generate_email_sequence(funnel_data, params=None):
    """
    Generate a sequence of emails for a sales funnel
    
    Args:
        funnel_data: Dictionary with funnel data
        params: Parameters for email generation
        
    Returns:
        Dictionary with email sequence
    """
    if params is None:
        params = {}
    
    logger.debug("Generating email sequence")
    
    try:
        # Extract key information from funnel data
        main_page = funnel_data.get('main_page', {})
        upsells = funnel_data.get('upsells', [])
        customizations = funnel_data.get('customizations', {})
        
        # Extract parameters for email generation
        num_emails = min(params.get('num_emails', 10), 20)  # Max 20 emails
        sequence_type = params.get('sequence_type', 'sales')
        email_style = params.get('email_style', 'conversational')
        
        # Extract product information
        brand_name = customizations.get('brand_name', 'Our Product')
        product_headline = main_page.get('headline', 'Our Amazing Product')
        product_benefits = main_page.get('benefits', [])
        if isinstance(product_benefits, dict):
            product_benefits = list(product_benefits.values())
        
        # Create prompt for email sequence generation
        prompt = f"""
        Generate a complete email sequence for this product:
        
        Brand Name: {brand_name}
        Product Headline: {product_headline}
        
        Key Benefits:
        {", ".join(product_benefits[:5]) if isinstance(product_benefits, list) else ""}
        
        Sequence Type: {sequence_type} (Options: sales, nurture, onboarding, abandoned cart)
        Email Style: {email_style} (Options: conversational, formal, story-based, direct)
        Number of Emails: {num_emails}
        
        Please generate a complete email sequence with these details in JSON format:
        1. sequence_name: A name for this email sequence
        2. sequence_type: The type of sequence (sales, nurture, etc.)
        3. purpose: The overall purpose of this sequence
        4. timing: When each email should be sent (e.g., "Day 1", "Day 3", etc.)
        5. emails: An array of email objects, each containing:
            a. subject: Email subject line
            b. body: Complete email body
            c. purpose: The specific purpose of this email
            d. call_to_action: The main call to action in this email
        
        Return your response in valid JSON format.
        """
        
        # Add information about upsells if available
        if upsells:
            upsell_descriptions = []
            for i, upsell in enumerate(upsells[:3]):  # Include up to 3 upsells
                upsell_descriptions.append(f"{upsell.get('product_name', f'Upsell {i+1}')} - {upsell.get('description', '')}")
            
            if upsell_descriptions:
                prompt += f"""
                Upsell Products to Include in Some Emails:
                {chr(10).join(upsell_descriptions)}
                """
        
        # Make the API call to generate email sequence
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert email copywriter specializing in high-converting email sequences for sales funnels."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the JSON response
        email_sequence = json.loads(response.choices[0].message.content)
        
        # Add metadata
        email_sequence['num_emails'] = len(email_sequence.get('emails', []))
        email_sequence['brand_name'] = brand_name
        
        return email_sequence
        
    except Exception as e:
        logger.error(f"Error generating email sequence: {str(e)}")
        # Return a basic email sequence in case of failure
        return {
            'error': str(e),
            'sequence_name': 'Basic Sales Sequence',
            'sequence_type': 'sales',
            'purpose': 'To nurture leads and drive sales',
            'num_emails': 3,
            'brand_name': customizations.get('brand_name', 'Our Product'),
            'timing': {
                '1': 'Day 0 (Immediately)',
                '2': 'Day 2',
                '3': 'Day 4'
            },
            'emails': [
                {
                    'subject': 'Welcome to [Brand Name]',
                    'body': 'Welcome email content goes here...',
                    'purpose': 'Introduction',
                    'call_to_action': 'Visit our website'
                },
                {
                    'subject': 'Benefits of [Product Name]',
                    'body': 'Benefits email content goes here...',
                    'purpose': 'Highlight benefits',
                    'call_to_action': 'Learn more'
                },
                {
                    'subject': 'Special Offer Inside',
                    'body': 'Promotional email content goes here...',
                    'purpose': 'Drive sales',
                    'call_to_action': 'Buy now'
                }
            ]
        }
