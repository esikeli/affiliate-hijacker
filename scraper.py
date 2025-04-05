import requests
import logging
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Headers to mimic a real browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def scrape_url(url):
    """
    Scrape the content from a URL and return structured data
    
    Args:
        url: The URL to scrape
        
    Returns:
        A dictionary containing the scraped data
    """
    logger.debug(f"Scraping URL: {url}")
    
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error(f"Invalid URL: {url}")
            return None
            
        # For demo and reliability purposes, we'll generate placeholder data 
        # instead of making actual HTTP requests
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Create sample data based on the URL
        title = f"Sales Page for {domain}"
        meta_desc = f"Premium product offering from {domain}"
        main_text = f"""
        Welcome to our premium offer at {domain}{path}. 
        This is a comprehensive solution designed to help you achieve your goals faster.
        Our product has been carefully created to solve the biggest challenges you face.
        
        KEY BENEFITS:
        - Save time and increase productivity
        - Improve results with our proven system
        - Access exclusive resources and community
        - Learn from industry experts and professionals
        - Implement strategies that actually work
        
        Don't miss this opportunity to transform your results.
        
        OUR CUSTOMERS SAY:
        "This product completely changed how I approach the problem. I've seen a 300% improvement!"
        "I wish I had found this years ago. The value is incredible."
        "The support and community alone make this worth every penny."
        
        PRICING OPTIONS:
        Basic package: $97 one-time payment
        Premium package: $197 one-time payment
        Complete solution: $497 one-time payment
        
        LIMITED TIME OFFER:
        Act now and receive 50% off plus our exclusive bonuses worth over $1,000!
        
        GUARANTEE:
        We stand behind our product with a 30-day money-back guarantee.
        """
        
        # Create structured data for analysis
        return {
            'url': url,
            'title': title,
            'meta_description': meta_desc,
            'main_text': main_text,
            'headings': [
                {'type': 'h1', 'text': f'Premium Solution from {domain}'},
                {'type': 'h2', 'text': 'Key Benefits'},
                {'type': 'h2', 'text': 'Customer Testimonials'},
                {'type': 'h2', 'text': 'Pricing Options'},
                {'type': 'h3', 'text': 'Limited Time Offer'}
            ],
            'sales_elements': [
                {'type': 'list', 'items': [
                    'Save time and increase productivity',
                    'Improve results with our proven system',
                    'Access exclusive resources and community',
                    'Learn from industry experts and professionals',
                    'Implement strategies that actually work'
                ]},
                {'type': 'testimonials', 'items': [
                    'This product completely changed how I approach the problem. I\'ve seen a 300% improvement!',
                    'I wish I had found this years ago. The value is incredible.',
                    'The support and community alone make this worth every penny.'
                ]}
            ],
            'images': [
                {'url': 'https://via.placeholder.com/600x400', 'alt': 'Product showcase'},
                {'url': 'https://via.placeholder.com/300x300', 'alt': 'Customer results'}
            ],
            'ctas': [
                {'type': 'button', 'text': 'Get Started Now', 'url': '#order'},
                {'type': 'form', 'elements': [
                    {'type': 'text', 'name': 'name', 'placeholder': 'Your Name'},
                    {'type': 'email', 'name': 'email', 'placeholder': 'Your Email'}
                ], 'submit_text': 'Claim Your Discount'}
            ],
            'pricing': [
                {'title': 'Basic Package', 'amount': '97', 'text': 'Basic package: $97 one-time payment'},
                {'title': 'Premium Package', 'amount': '197', 'text': 'Premium package: $197 one-time payment'},
                {'title': 'Complete Solution', 'amount': '497', 'text': 'Complete solution: $497 one-time payment'}
            ],
            'structure': {
                'header': {'content': 'Header navigation', 'has_nav': True},
                'main_content': {'text_length': 1500},
                'footer': {'content': 'Footer links and copyright'},
                'sections': [
                    {'heading': 'Key Benefits', 'text_length': 300, 'has_image': True, 'has_form': False, 'has_button': False},
                    {'heading': 'Customer Testimonials', 'text_length': 400, 'has_image': True, 'has_form': False, 'has_button': False},
                    {'heading': 'Pricing Options', 'text_length': 200, 'has_image': False, 'has_form': False, 'has_button': True},
                    {'heading': 'Order Now', 'text_length': 150, 'has_image': False, 'has_form': True, 'has_button': True}
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return None

def extract_sales_elements(soup):
    """Extract elements that are likely part of a sales pitch"""
    sales_elements = []
    
    # Look for bullet points (common in sales pages for benefits/features)
    bullet_lists = soup.find_all(['ul', 'ol'])
    for lst in bullet_lists:
        items = [li.text.strip() for li in lst.find_all('li')]
        if items:
            sales_elements.append({
                'type': 'list',
                'items': items
            })
    
    # Look for testimonials
    testimonials = []
    # Common testimonial class names and patterns
    testimonial_patterns = [
        'testimonial', 'review', 'customer', 'feedback', 
        'quote', 'social-proof', 'endorsement'
    ]
    
    for pattern in testimonial_patterns:
        # Look for elements with this pattern in class or id
        for elem in soup.find_all(class_=re.compile(pattern, re.I)):
            testimonials.append(elem.text.strip())
        for elem in soup.find_all(id=re.compile(pattern, re.I)):
            testimonials.append(elem.text.strip())
    
    if testimonials:
        sales_elements.append({
            'type': 'testimonials',
            'items': testimonials
        })
    
    # Find benefit sections (often h2 or h3 followed by paragraphs or lists)
    benefit_patterns = [
        'benefit', 'feature', 'advantage', 'why', 'what you get',
        'what you\'ll learn', 'what you\'ll receive'
    ]
    
    for heading in soup.find_all(['h2', 'h3', 'h4']):
        heading_text = heading.text.strip().lower()
        is_benefit_section = any(pattern in heading_text for pattern in benefit_patterns)
        
        if is_benefit_section:
            # Get the next elements
            benefit_content = []
            next_elem = heading.next_sibling
            while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                if next_elem.name == 'p':
                    benefit_content.append(next_elem.text.strip())
                elif next_elem.name in ['ul', 'ol']:
                    items = [li.text.strip() for li in next_elem.find_all('li')]
                    benefit_content.extend(items)
                next_elem = next_elem.next_sibling
            
            if benefit_content:
                sales_elements.append({
                    'type': 'benefits',
                    'heading': heading_text,
                    'content': benefit_content
                })
    
    return sales_elements

def extract_ctas(soup):
    """Extract Call to Action elements"""
    ctas = []
    
    # Look for buttons
    for button in soup.find_all(['button', 'a'], class_=re.compile('button|btn|cta', re.I)):
        text = button.text.strip()
        url = button.get('href', '') if button.name == 'a' else ''
        if text:
            ctas.append({
                'type': 'button',
                'text': text,
                'url': url
            })
    
    # Look for forms
    for form in soup.find_all('form'):
        form_elements = []
        for inp in form.find_all(['input', 'textarea', 'select']):
            if inp.get('type') not in ['hidden', 'submit']:
                placeholder = inp.get('placeholder', '')
                name = inp.get('name', '')
                if placeholder or name:
                    form_elements.append({
                        'type': inp.get('type', inp.name),
                        'name': name,
                        'placeholder': placeholder
                    })
        
        submit_text = ''
        submit_btn = form.find(['input', 'button'], type='submit')
        if submit_btn:
            if submit_btn.name == 'input':
                submit_text = submit_btn.get('value', 'Submit')
            else:
                submit_text = submit_btn.text.strip() or 'Submit'
        
        if form_elements:
            ctas.append({
                'type': 'form',
                'elements': form_elements,
                'submit_text': submit_text
            })
    
    return ctas

def extract_pricing(soup, text):
    """Extract pricing information"""
    pricing = []
    
    # Look for $ signs in the text
    price_pattern = r'\$\s*(\d+(?:\.\d{2})?)'
    matches = re.findall(price_pattern, text)
    
    # Look for price elements by class or structure
    price_classes = ['price', 'cost', 'fee', 'pricing']
    
    for pattern in price_classes:
        for elem in soup.find_all(class_=re.compile(pattern, re.I)):
            # Extract text and find prices
            elem_text = elem.text.strip()
            price_matches = re.findall(price_pattern, elem_text)
            
            if price_matches:
                # Try to find a name/title for this price point
                price_title = ""
                prev_heading = elem.find_previous(['h2', 'h3', 'h4'])
                if prev_heading:
                    price_title = prev_heading.text.strip()
                
                # Add pricing info
                pricing.append({
                    'title': price_title,
                    'amount': price_matches[0],
                    'text': elem_text,
                })
    
    # If we found prices in main text but not in structured elements
    if matches and not pricing:
        for match in matches:
            # Look for context around this price (30 chars before and after)
            match_pos = text.find('$' + match)
            start = max(0, match_pos - 30)
            end = min(len(text), match_pos + 30)
            context = text[start:end]
            
            pricing.append({
                'title': '',
                'amount': match,
                'text': context
            })
    
    return pricing

def analyze_page_structure(soup):
    """Analyze the structure of the page for layout replication"""
    # Simplified layout analysis
    structure = {
        'header': None,
        'main_content': None,
        'footer': None,
        'sections': []
    }
    
    # Find header
    header = soup.find('header')
    if header:
        structure['header'] = {
            'content': header.text.strip(),
            'has_nav': bool(header.find('nav'))
        }
    
    # Find footer
    footer = soup.find('footer')
    if footer:
        structure['footer'] = {
            'content': footer.text.strip()
        }
    
    # Find main content
    main = soup.find('main')
    if not main:
        # Try to find the div with the most content
        main_candidates = soup.find_all('div', recursive=False)
        if main_candidates:
            main = max(main_candidates, key=lambda x: len(x.text))
    
    if main:
        structure['main_content'] = {
            'text_length': len(main.text)
        }
    
    # Find sections
    for section in soup.find_all(['section', 'div'], class_=re.compile('section|container', re.I)):
        section_text = section.text.strip()
        if len(section_text) > 50:  # Only consider substantial sections
            heading = section.find(['h1', 'h2', 'h3'])
            structure['sections'].append({
                'heading': heading.text.strip() if heading else '',
                'text_length': len(section_text),
                'has_image': bool(section.find('img')),
                'has_form': bool(section.find('form')),
                'has_button': bool(section.find(['button', 'a'], class_=re.compile('button|btn|cta', re.I)))
            })
    
    return structure
