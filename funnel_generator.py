import os
import logging
import json
import zipfile
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import io
import re
import shutil
from pathlib import Path

from ai_engine import generate_copy, generate_upsell

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

def generate_funnel(analysis, customizations):
    """
    Generate a complete funnel based on the page analysis
    
    Args:
        analysis: Dictionary with page analysis
        customizations: Dictionary with customization parameters
        
    Returns:
        Dictionary with complete funnel data
    """
    logger.debug("Generating funnel")
    
    # Create main page copy
    main_page = generate_copy(analysis, customizations)
    
    # Add brand name to main product info for upsells
    main_product_info = {
        'product_type': analysis.get('product_type', 'product'),
        'brand_name': customizations.get('brand_name', 'Our Product')
    }
    
    # Generate upsells
    upsells = []
    num_upsells = customizations.get('num_upsells', 10)
    for i in range(num_upsells):
        upsell = generate_upsell(main_product_info, 'upsell', i + 1)
        upsells.append(upsell)
    
    # Generate downsells
    downsells = []
    num_downsells = customizations.get('num_downsells', 10)
    for i in range(num_downsells):
        downsell = generate_upsell(main_product_info, 'downsell', i + 1)
        downsells.append(downsell)
    
    # Create funnel flow
    funnel_flow = design_funnel_flow(main_page, upsells, downsells)
    
    # Return complete funnel data
    return {
        'main_page': main_page,
        'upsells': upsells,
        'downsells': downsells,
        'funnel_flow': funnel_flow,
        'customizations': customizations,
        'base_analysis': analysis
    }

def design_funnel_flow(main_page, upsells, downsells):
    """
    Design the flow of the funnel (which page leads to which)
    
    Args:
        main_page: Dictionary with main page data
        upsells: List of upsell dictionaries
        downsells: List of downsell dictionaries
        
    Returns:
        Dictionary with funnel flow information
    """
    flow = []
    
    # Start with main page
    flow.append({
        'id': 'main',
        'type': 'main',
        'name': 'Main Sales Page',
        'accept_action': 'to_upsell_1',
        'decline_action': 'exit'
    })
    
    # Add upsells
    for i, upsell in enumerate(upsells):
        flow_item = {
            'id': f'upsell_{i+1}',
            'type': 'upsell',
            'name': upsell.get('product_name', f'Upsell {i+1}'),
            'accept_action': f'to_upsell_{i+2}' if i < len(upsells) - 1 else 'to_thank_you',
            'decline_action': f'to_downsell_{i+1}'
        }
        flow.append(flow_item)
    
    # Add downsells
    for i, downsell in enumerate(downsells):
        next_action = f'to_upsell_{i+2}' if i < len(upsells) - 1 else 'to_thank_you'
        flow_item = {
            'id': f'downsell_{i+1}',
            'type': 'downsell',
            'name': downsell.get('product_name', f'Downsell {i+1}'),
            'accept_action': next_action,
            'decline_action': next_action
        }
        flow.append(flow_item)
    
    # Add thank you page
    flow.append({
        'id': 'thank_you',
        'type': 'thank_you',
        'name': 'Thank You Page',
        'accept_action': 'exit',
        'decline_action': 'exit'
    })
    
    return flow

def create_html_page(page_data, page_type):
    """
    Create HTML content for a funnel page
    
    Args:
        page_data: Dictionary with page data
        page_type: Type of page (main, upsell, downsell, thank_you)
        
    Returns:
        HTML content as string
    """
    try:
        # Load the appropriate template based on page type
        template = jinja_env.get_template(f'{page_type}.html')
        
        # Render the template with the page data
        html_content = template.render(page=page_data)
        
        return html_content
        
    except Exception as e:
        logger.error(f"Error creating HTML for {page_type} page: {str(e)}")
        # Return a basic HTML page in case of error
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{page_data.get('headline', 'Funnel Page')}</title>
            <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        </head>
        <body>
            <div class="container py-5">
                <h1>{page_data.get('headline', 'Funnel Page')}</h1>
                <p>{page_data.get('description', '')}</p>
                <button class="btn btn-primary">{page_data.get('cta_text', 'Continue')}</button>
            </div>
        </body>
        </html>
        """

def create_zip_export(project):
    """
    Create a ZIP file with all the funnel pages
    
    Args:
        project: Project database model instance
        
    Returns:
        Path to the created ZIP file
    """
    logger.debug(f"Creating ZIP export for project {project.id}")
    
    try:
        # Create a timestamp for the export
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create a directory for exports if it doesn't exist
        exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Set the zip filename
        zip_filename = os.path.join(exports_dir, f"{project.id}.zip")
        
        # Parse funnel data
        funnel_data = json.loads(project.funnel_data) if project.funnel_data else None
        email_sequence = json.loads(project.email_sequence) if project.email_sequence else None
        
        if not funnel_data:
            raise ValueError("No funnel data available for export")
        
        # Create the ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add main page
            main_page = funnel_data.get('main_page', {})
            main_html = create_html_page(main_page, 'main')
            zipf.writestr('index.html', main_html)
            
            # Add CSS file
            zipf.writestr('style.css', generate_css())
            
            # Add JavaScript
            zipf.writestr('funnel.js', generate_js(funnel_data))
            
            # Add upsells
            for i, upsell in enumerate(funnel_data.get('upsells', [])):
                upsell_html = create_html_page(upsell, 'upsell')
                zipf.writestr(f'upsell_{i+1}.html', upsell_html)
            
            # Add downsells
            for i, downsell in enumerate(funnel_data.get('downsells', [])):
                downsell_html = create_html_page(downsell, 'downsell')
                zipf.writestr(f'downsell_{i+1}.html', downsell_html)
            
            # Add thank you page
            thank_you_html = create_thank_you_page(funnel_data)
            zipf.writestr('thank_you.html', thank_you_html)
            
            # Add email sequence if available
            if email_sequence:
                # Create a subdirectory for emails
                for i, email in enumerate(email_sequence.get('emails', [])):
                    email_content = f"""
Subject: {email.get('subject', f'Email {i+1}')}

{email.get('body', 'Email content')}
                    """
                    zipf.writestr(f'emails/email_{i+1}.txt', email_content)
                
                # Add email sequence documentation
                email_docs = f"""
Email Sequence Documentation
===========================

Sequence Name: {email_sequence.get('sequence_name', 'Email Sequence')}
Number of Emails: {len(email_sequence.get('emails', []))}
Sequence Type: {email_sequence.get('sequence_type', 'sales')}

Timing:
- Email 1: Immediately after signup
{chr(10).join([f'- Email {i+2}: {email_sequence.get("timing", {}).get(str(i+2), "Day " + str(i+1))}' for i in range(len(email_sequence.get('emails', [])) - 1)])}

Purpose:
{email_sequence.get('purpose', 'Nurture leads and promote products')}

Instructions:
1. Import these emails into your email marketing platform
2. Set up the automation sequence with the timing above
3. Customize sender name and contact information before sending
                """
                zipf.writestr('emails/README.txt', email_docs)
            
            # Add documentation
            zipf.writestr('README.txt', generate_documentation(project, funnel_data))
        
        return zip_filename
        
    except Exception as e:
        logger.error(f"Error creating ZIP export: {str(e)}")
        raise

def generate_css():
    """Generate CSS for the funnel pages"""
    return """
    /* Custom styles for funnel pages */
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f8f9fa;
    }
    
    .hero-section {
        background-color: #f5f5f5;
        padding: 3rem 0;
        margin-bottom: 2rem;
    }
    
    .headline {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .subheadline {
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    .benefits-box {
        background-color: #f8f8f8;
        border-left: 5px solid #4CAF50;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .testimonial {
        background-color: #fff;
        border-left: 3px solid #007bff;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .cta-button {
        display: inline-block;
        padding: 1rem 2rem;
        font-size: 1.25rem;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        background-color: #FF5722;
        color: white;
        border-radius: 5px;
        margin: 1.5rem 0;
        transition: background-color 0.3s ease;
    }
    
    .cta-button:hover {
        background-color: #E64A19;
    }
    
    .price-tag {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4CAF50;
        margin: 1rem 0;
    }
    
    .guarantee-box {
        background-color: #FFFDE7;
        border: 1px solid #FFC107;
        padding: 1.5rem;
        margin: 2rem 0;
        text-align: center;
    }
    
    .faq-item {
        margin-bottom: 1.5rem;
    }
    
    .faq-question {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .faq-answer {
        color: #555;
    }
    
    .upsell-box {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
    }
    
    .downsell-box {
        background-color: #E8F5E9;
        border: 1px solid #4CAF50;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
    }
    
    .thank-you-box {
        background-color: #E8F5E9;
        text-align: center;
        padding: 3rem;
        margin: 3rem 0;
    }
    """

def generate_js(funnel_data):
    """Generate JavaScript for the funnel flow"""
    funnel_flow_str = json.dumps(funnel_data.get('funnel_flow', []))
    
    return f"""
    // Funnel flow data
    const funnelFlow = {funnel_flow_str};
    
    // Function to handle button clicks
    function handleButtonClick(action) {{
        // Find the next page based on the action
        let nextPage = '';
        
        switch(action) {{
            case 'to_thank_you':
                nextPage = 'thank_you.html';
                break;
            case 'exit':
                // Handle exit action (e.g., redirect to external page)
                return;
            default:
                // Extract page ID from action string (e.g., 'to_upsell_1' -> 'upsell_1')
                const pageId = action.replace('to_', '');
                nextPage = pageId + '.html';
        }}
        
        // Navigate to the next page
        window.location.href = nextPage;
    }}
    
    // Initialize the page
    document.addEventListener('DOMContentLoaded', function() {{
        // Add event listeners to accept/decline buttons
        const acceptButtons = document.querySelectorAll('.accept-button');
        const declineButtons = document.querySelectorAll('.decline-button');
        
        acceptButtons.forEach(button => {{
            button.addEventListener('click', function() {{
                const action = this.getAttribute('data-action');
                handleButtonClick(action);
            }});
        }});
        
        declineButtons.forEach(button => {{
            button.addEventListener('click', function() {{
                const action = this.getAttribute('data-action');
                handleButtonClick(action);
            }});
        }});
    }});
    """

def generate_documentation(project, funnel_data):
    """Generate documentation for the funnel"""
    customizations = funnel_data.get('customizations', {})
    
    return f"""
Affiliate Hijacker Funnel - Documentation
========================================

Project Name: {project.name}
Original URL: {project.url}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Product Information:
------------------
Brand Name: {customizations.get('brand_name', 'Our Product')}
Target Audience: {customizations.get('target_audience', 'General audience')}
Unique Angle: {customizations.get('unique_angle', '')}

Funnel Structure:
---------------
1. Main Sales Page (index.html)
2. Upsells: {len(funnel_data.get('upsells', []))} pages
3. Downsells: {len(funnel_data.get('downsells', []))} pages
4. Thank You Page (thank_you.html)

Files Included:
-------------
- index.html: Main sales page
- upsell_*.html: Upsell pages
- downsell_*.html: Downsell pages
- thank_you.html: Thank you page
- style.css: CSS styles for all pages
- funnel.js: JavaScript for funnel flow control
- emails/: Directory containing email sequence (if generated)
- README.txt: This documentation file

How to Use:
---------
1. Upload all files to your web hosting
2. Link your payment processor to the buttons
3. Set up email sequence in your email marketing platform
4. Test the complete funnel flow before driving traffic

Customization:
------------
- Edit HTML files to customize design and content
- Modify CSS in style.css to change appearance
- Update funnel.js if you need to change the flow

Notes:
-----
This funnel was generated by Affiliate Hijacker based on analysis of the original URL.
The design, copy, and flow are optimized for maximum conversions.
    """

def create_thank_you_page(funnel_data):
    """Create a thank you page for the funnel"""
    customizations = funnel_data.get('customizations', {})
    brand_name = customizations.get('brand_name', 'Our Product')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You for Your Purchase | {brand_name}</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div class="container py-5">
            <div class="thank-you-box">
                <h1>Thank You for Your Purchase!</h1>
                <p>Your order has been successfully processed and is on its way to you.</p>
                <div class="my-4">
                    <h3>What's Next?</h3>
                    <p>Check your email for your order confirmation and access instructions.</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
                <div class="mt-5">
                    <h3>Recommended Next Steps</h3>
                    <ul class="list-group my-3">
                        <li class="list-group-item">Check your email for your order confirmation</li>
                        <li class="list-group-item">Bookmark this page for future reference</li>
                        <li class="list-group-item">Follow us on social media for updates and tips</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script src="funnel.js"></script>
    </body>
    </html>
    """
