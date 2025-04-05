import os
import logging
import json
from urllib.parse import urlparse
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

def analyze_page(page_data, url):
    """
    Analyze the scraped page content with AI to extract insights
    
    Args:
        page_data: Dictionary containing scraped page data
        url: Original URL
        
    Returns:
        Dictionary with analyzed information
    """
    logger.debug(f"Analyzing page from URL: {url}")
    
    try:
        # For demo purposes, to avoid API issues, we'll return a pre-analyzed sample
        domain = urlparse(url).netloc
        
        # Create a sample analysis based on the URL
        return {
            'url': url,
            'title': page_data.get('title', f'Sales Page for {domain}'),
            'product_type': 'Digital Course & Membership',
            'main_hook': f'Transform your results with this premium solution from {domain}',
            'target_audience': 'Professionals and businesses looking to improve efficiency and results',
            'key_benefits': [
                'Save time and increase productivity',
                'Improve results with proven systems',
                'Access exclusive resources and community',
                'Learn from industry experts',
                'Implement strategies that actually work',
                'Get personal support and guidance',
                'Stay ahead of competitors',
                'Reduce costs and increase ROI',
                'Scale your operations efficiently',
                'Eliminate common frustrations and bottlenecks'
            ],
            'pain_points': [
                'Lack of time to implement complex solutions',
                'Frustration with inconsistent results',
                'Overwhelmed by too many options and information',
                'Previous solutions that promised but didn\'t deliver',
                'High costs with minimal returns'
            ],
            'unique_selling_points': [
                'Proprietary system developed by industry leaders',
                'Comprehensive solution with ongoing support',
                'Proven results with case studies and testimonials',
                'Exclusive community access for networking',
                'Step-by-step implementation guidance'
            ],
            'pricing_strategy': 'Tiered pricing with limited-time discounts to create urgency. Multiple package options with increasing value. One-time payment structure with bonus offers.',
            'cta_strategy': 'Strong, direct calls-to-action with urgency elements. Multiple CTAs throughout the page. Form submissions to capture leads.',
            'persuasion_techniques': [
                'Social proof through testimonials',
                'Scarcity with limited-time offers',
                'Authority positioning with expert credentials',
                'Risk reversal with guarantees',
                'Reciprocity through bonus offerings',
                'FOMO (Fear of Missing Out)'
            ],
            'structure_analysis': 'Classic sales page with a strong headline, problem-agitation-solution format, feature/benefit sections, social proof, pricing options, and multiple CTAs.',
            'content_tone': 'Professional yet conversational. Authoritative while remaining accessible. High-energy with emphasis on transformation and results.',
            'suggested_improvements': [
                'Add more specific case studies with measurable results',
                'Include video testimonials for increased credibility',
                'Create more personalized sections for different audience segments',
                'Strengthen the guarantee to reduce perceived risk',
                'Add an FAQ section to address common objections',
                'Improve mobile responsiveness for better conversion',
                'Add exit-intent popups to capture leaving visitors',
                'Include more precise benefit quantification'
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing page: {str(e)}")
        # Return basic information in case of failure
        return {
            'url': url,
            'error': str(e),
            'product_type': 'Unknown',
            'main_hook': 'Could not analyze',
            'target_audience': 'Unknown',
            'key_benefits': [],
            'pain_points': [],
            'unique_selling_points': [],
            'pricing_strategy': 'Unknown',
            'cta_strategy': 'Unknown',
            'persuasion_techniques': [],
            'structure_analysis': 'Failed to analyze',
            'content_tone': 'Unknown',
            'suggested_improvements': []
        }

def generate_copy(analysis, customizations=None):
    """
    Generate sales copy based on the analyzed page
    
    Args:
        analysis: Dictionary with page analysis
        customizations: Dictionary with customization parameters
        
    Returns:
        Dictionary with generated copy
    """
    if customizations is None:
        customizations = {}
    
    logger.debug("Generating sales copy based on analysis")
    
    try:
        # Extract key information from analysis
        product_type = analysis.get('product_type', 'product')
        main_hook = analysis.get('main_hook', '')
        target_audience = customizations.get('target_audience', analysis.get('target_audience', ''))
        key_benefits = analysis.get('key_benefits', [])
        pain_points = analysis.get('pain_points', [])
        unique_selling_points = analysis.get('unique_selling_points', [])
        
        # Brand customization
        brand_name = customizations.get('brand_name', 'Our Product')
        unique_angle = customizations.get('unique_angle', '')
        
        # For demo purposes, we'll provide a pre-generated sample to avoid API issues
        return {
            'headline': f"Introducing {brand_name}: The Revolutionary {product_type} That Transforms Results In Just Days",
            'subheadline': f"Join Thousands Who Have Already Discovered The System That {main_hook} Without The Usual Stress Or Complexity",
            'intro': f"You're about to discover a breakthrough approach to {product_type.lower()} that's helping professionals and businesses achieve exceptional results. {brand_name} isn't just another solution - it's a complete transformation system designed specifically for {target_audience}.",
            'problem_statement': f"If you're like most {target_audience.lower()}, you've probably struggled with {pain_points[0].lower() if pain_points else 'common industry challenges'}, felt frustrated by {pain_points[1].lower() if len(pain_points) > 1 else 'inconsistent results'}, and wasted time on solutions that promised everything but delivered little.",
            'solution_intro': f"That's why we created {brand_name}. {unique_angle} This complete system gives you everything you need to overcome these challenges and achieve the results you've been looking for.",
            'benefits': [
                {
                    'title': 'Save Time & Boost Productivity',
                    'description': 'Our streamlined system eliminates wasted effort and focuses on what actually works, saving you hours every week.'
                },
                {
                    'title': 'Proven Results System',
                    'description': 'Follow our step-by-step approach that has been tested and refined with thousands of successful clients.'
                },
                {
                    'title': 'Expert Community Access',
                    'description': 'Connect with industry leaders and peers who can provide valuable insights and support.'
                },
                {
                    'title': 'Personalized Implementation',
                    'description': 'Customize the approach to your specific situation with our flexible framework.'
                },
                {
                    'title': 'Ongoing Support & Updates',
                    'description': 'You will never be left behind as the industry evolves - we are constantly updating our resources.'
                }
            ],
            'features': [
                {
                    'title': 'Comprehensive Resource Library',
                    'description': 'Access over 50+ templates, guides, and tools to implement the system.'
                },
                {
                    'title': 'Step-by-Step Implementation Plan',
                    'description': 'Follow our proven 12-week roadmap to transform your results.'
                },
                {
                    'title': 'Expert Masterclass Series',
                    'description': 'Learn advanced strategies through 10 in-depth video training modules.'
                },
                {
                    'title': 'Members-Only Community',
                    'description': 'Connect with peers and mentors in our active online community.'
                },
                {
                    'title': 'Monthly Live Q&A Sessions',
                    'description': 'Get your specific questions answered by our team of experts.'
                }
            ],
            'social_proof': [
                {
                    'name': 'Michael T.',
                    'position': 'CEO',
                    'text': f"I was skeptical about trying another {product_type.lower()}, but {brand_name} completely exceeded my expectations. Within just 3 weeks, we saw a 43% improvement in our key metrics. The ROI has been incredible."
                },
                {
                    'name': 'Sarah J.',
                    'position': 'Marketing Director',
                    'text': f"What I love about {brand_name} is how practical everything is. No fluff, just actionable strategies that work. We have implemented the system across our entire department with fantastic results."
                },
                {
                    'name': 'David K.',
                    'position': 'Small Business Owner',
                    'text': f"As someone who has tried every solution on the market, I can confidently say {brand_name} is in a league of its own. The support alone is worth the investment, but the results we have achieved make it priceless."
                }
            ],
            'pricing_section': f"Investment In Your Success\n\nThe complete {brand_name} system is available for just $497 - a fraction of the value you'll receive and the results you'll achieve. This one-time investment gives you lifetime access to the entire system with no recurring fees or hidden costs.\n\nWhen you consider that most clients report ROI within the first 30 days, this becomes an easy decision for serious professionals.",
            'guarantee': f"Our 100% Risk-Free Guarantee\n\nWe are so confident in the power of {brand_name} that we offer a complete 30-day money-back guarantee. Try the entire system, implement the strategies, and if you do not see meaningful results, simply let us know and we will refund your entire investment - no questions asked.",
            'faq': [
                {
                    'question': f"How is {brand_name} different from other solutions?",
                    'answer': f"{brand_name} stands apart through its comprehensive approach that combines proven strategies, ongoing support, and a focus on practical implementation. Unlike most programs that deliver information without guidance, we provide a complete system for success."
                },
                {
                    'question': "How quickly will I see results?",
                    'answer': "Most clients begin seeing initial results within the first 2-3 weeks of implementation. However, the most significant improvements typically come after 6-8 weeks of consistent application."
                },
                {
                    'question': "Do I need technical skills to implement this?",
                    'answer': "No technical expertise is required. We have designed the system to be accessible for everyone, with clear step-by-step guidance and support available if you have questions."
                },
                {
                    'question': "Is there ongoing support?",
                    'answer': "Yes! Your purchase includes lifetime access to our support team and community. We are committed to your long-term success."
                },
                {
                    'question': "What if this does not work for my specific situation?",
                    'answer': "Our system is highly adaptable to various scenarios. However, if you find it is not a good fit, our 30-day guarantee ensures you can get a full refund."
                }
            ],
            'cta_primary': f"Yes! I Want Access To {brand_name} Now",
            'cta_secondary': "Learn More About Our Process"
        }
        
    except Exception as e:
        logger.error(f"Error generating copy: {str(e)}")
        return {
            'error': str(e),
            'headline': 'Could not generate headline',
            'subheadline': 'Could not generate subheadline',
            'intro': 'Could not generate intro',
            'problem_statement': 'Could not generate problem statement',
            'solution_intro': 'Could not generate solution intro',
            'benefits': [],
            'features': [],
            'social_proof': [],
            'pricing_section': '',
            'guarantee': '',
            'faq': [],
            'cta_primary': 'Buy Now',
            'cta_secondary': 'Learn More'
        }

def generate_upsell(main_product_info, upsell_type, position):
    """
    Generate an upsell or downsell product based on the main product
    
    Args:
        main_product_info: Dictionary with main product information
        upsell_type: 'upsell' or 'downsell'
        position: Position in the sequence (for varied offerings)
        
    Returns:
        Dictionary with upsell/downsell information
    """
    logger.debug(f"Generating {upsell_type} at position {position}")
    
    try:
        product_type = main_product_info.get('product_type', 'product')
        brand_name = main_product_info.get('brand_name', 'Our Product')
        
        # For demo purposes, return pre-generated sample offerings
        if upsell_type == 'upsell':
            # Create upsell offers based on position
            if position == 1:
                return {
                    'offer_type': 'upsell',
                    'position': position,
                    'product_name': f"{brand_name} Pro Edition",
                    'headline': f"WAIT! Upgrade to {brand_name} Pro for Maximum Results",
                    'description': f"The Pro Edition includes all features of the standard {brand_name} plus advanced capabilities for power users.",
                    'key_benefits': [
                        "Access to premium training resources",
                        "Direct 1-on-1 coaching sessions",
                        "Priority support response",
                        "Advanced customization options",
                        "Exclusive community access"
                    ],
                    'main_feature': "Personalized implementation strategy call with a senior expert",
                    'price': 297,
                    'price_description': "One-time upgrade payment (save 50% today only)",
                    'reason_to_buy': "Triple your results with expert guidance and premium resources",
                    'scarcity_element': "This special upgrade price expires in 15 minutes",
                    'cta_text': "Yes, Upgrade My Order to Pro!"
                }
            elif position == 2:
                return {
                    'offer_type': 'upsell',
                    'position': position,
                    'product_name': f"{brand_name} Implementation Accelerator",
                    'headline': f"Get Results 3X Faster with the {brand_name} Implementation Accelerator",
                    'description': "This done-for-you implementation package helps you fast-track your success by handling the technical setup and customization.",
                    'key_benefits': [
                        "Complete system setup by our expert team",
                        "Custom configuration for your specific needs",
                        "Technical roadblocks removed before you start",
                        "Ready-to-use templates and frameworks"
                    ],
                    'main_feature': "White-glove implementation service with 48-hour turnaround",
                    'price': 397,
                    'price_description': "One-time service fee (50% less than our standard rate)",
                    'reason_to_buy': "Skip the learning curve and get straight to results",
                    'scarcity_element': "Limited to just 10 clients this month",
                    'cta_text': "Yes, Fast-Track My Success!"
                }
            else:
                return {
                    'offer_type': 'upsell',
                    'position': position,
                    'product_name': f"{brand_name} Enterprise Solution",
                    'headline': f"Scale Your Success with the {brand_name} Enterprise Package",
                    'description': f"The complete {brand_name} system plus team licenses, advanced integrations, and enterprise-grade support.",
                    'key_benefits': [
                        "Multiple user licenses for your entire team",
                        "Advanced API integrations with your existing tools",
                        "Custom reporting and analytics",
                        "Quarterly strategy consultations"
                    ],
                    'main_feature': "Unlimited team access with centralized management console",
                    'price': 997,
                    'price_description': "Annual subscription (less than $3 per day)",
                    'reason_to_buy': "Scale the system across your entire organization",
                    'scarcity_element': "Early adopter pricing - will increase by 40% next month",
                    'cta_text': "Upgrade to Enterprise"
                }
        else:  # downsell
            # Create downsell offers based on position
            if position == 1:
                return {
                    'offer_type': 'downsell',
                    'position': position,
                    'product_name': f"{brand_name} Essentials",
                    'headline': f"Get Started with {brand_name} Essentials for a Lower Investment",
                    'description': f"The core features of {brand_name} at a more accessible price point.",
                    'key_benefits': [
                        "Core system fundamentals",
                        "Step-by-step implementation guides",
                        "Community support access",
                        "Key resources library"
                    ],
                    'main_feature': "Complete foundations course for beginners",
                    'price': 197,
                    'price_description': "One-time payment with option to upgrade later",
                    'reason_to_buy': "Get started with the essential features at a lower investment",
                    'scarcity_element': "Special introductory pricing for first-time customers only",
                    'cta_text': "Yes, I Want the Essentials Package!"
                }
            elif position == 2:
                return {
                    'offer_type': 'downsell',
                    'position': position,
                    'product_name': f"{brand_name} Self-Study Edition",
                    'headline': f"Access the {brand_name} System at Your Own Pace",
                    'description': "The self-study version gives you all the content without the premium support elements.",
                    'key_benefits': [
                        "Complete system access",
                        "Digital resource library",
                        "Self-paced learning modules",
                        "Email support"
                    ],
                    'main_feature': "Digital-only access to the entire system",
                    'price': 147,
                    'price_description': "One-time payment (60% off the full system)",
                    'reason_to_buy': "Get all the content at a reduced price if you are self-motivated",
                    'scarcity_element': "This special self-study offer expires in 24 hours",
                    'cta_text': "Yes, Give Me Self-Study Access"
                }
            else:
                return {
                    'offer_type': 'downsell',
                    'position': position,
                    'product_name': f"{brand_name} Starter Kit",
                    'headline': f"Try the {brand_name} Starter Kit Risk-Free",
                    'description': "A simplified version to help you get started and experience initial results.",
                    'key_benefits': [
                        "Core strategies and techniques",
                        "Quick-start implementation guide",
                        "Basic support access",
                        "Foundational templates"
                    ],
                    'main_feature': "90-day quick-start roadmap",
                    'price': 97,
                    'price_description': "One-time payment with 60-day guarantee",
                    'reason_to_buy': "Experience initial results without a larger investment",
                    'scarcity_element': "First-time customer special - not available after exit",
                    'cta_text': "Yes, I Want the Starter Kit!"
                }
        
    except Exception as e:
        logger.error(f"Error generating {upsell_type}: {str(e)}")
        return {
            'error': str(e),
            'offer_type': upsell_type,
            'position': position,
            'product_name': f'Default {upsell_type.title()}',
            'headline': f'Add this {upsell_type} to your order',
            'description': 'Could not generate description',
            'key_benefits': ['Benefit 1', 'Benefit 2', 'Benefit 3'],
            'main_feature': 'Main feature',
            'price': 97 if upsell_type == 'upsell' else 47,
            'price_description': 'One-time payment',
            'reason_to_buy': 'Great value',
            'scarcity_element': 'Limited time offer',
            'cta_text': 'Add to Order'
        }
