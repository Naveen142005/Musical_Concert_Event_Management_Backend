from fastapi import APIRouter, HTTPException, File, Form, UploadFile, status
from typing import Optional, Union
from app.services.content import content_service
from app.schemas.content import AboutUsResponse, BandsResponse, FAQResponse, FooterResponse, HeroSectionResponse, VenueCarouselResponse
from fastapi.datastructures import UploadFile as StarletteUploadFile

from app.utils.common import raise_exception

router = APIRouter()

@router.get("/hero", response_model=HeroSectionResponse, status_code=status.HTTP_200_OK)
async def get_hero_content():
    """Public endpoint to fetch current hero section content"""
    hero_content = await content_service.get_hero_content()
    
    if not hero_content:
        raise_exception(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero section content not found"
        )
    
    return hero_content

@router.put("/hero", response_model=HeroSectionResponse, status_code=status.HTTP_200_OK)
async def update_hero_content(
    heading: Optional[str] = Form(None),
    subheading: Optional[str] = Form(None),
    cta_text: Optional[str] = Form(None),
    cta_link: Optional[str] = Form(None),
    total_events: Optional[str] = Form(None),
    satisfied_clients: Optional[str] = Form(None),
    customer_rating: Optional[str] = Form(None),
    tickets_sold: Optional[str] = Form(None),
    image: Union[UploadFile, str, None] = File(None) 
):
    
    
    """Admin endpoint to update hero section with optional image"""
    return await content_service.update_hero_content(
        heading, subheading, cta_text, cta_link,
        total_events, satisfied_clients, customer_rating, tickets_sold,
        image
    )

@router.post("/hero/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_hero_section():
    """Admin endpoint to initialize hero section with default content"""
    initial_data = {
        "section": "hero_section",
        "heading": "INDIA'S LEADING CONCERT BOOKING APP",
        "subheading": "Experience world-class concerts with premium seating, exclusive access, and unforgettable moments.",
        "cta_text": "Go to Booking",
        "cta_link": "/booking",
        "stats": {
            "total_events": 375,
            "satisfied_clients": "9.5K",
            "customer_rating": "4.5/5",
            "tickets_sold": "93K"
        }
    }
    
    result = await content_service.initialize_hero_content(initial_data)
    return {"message": "Hero section initialized successfully", "data": result}



# ==================== VENUE CAROUSEL ROUTES ====================

@router.get("/venue-carousel", response_model=VenueCarouselResponse, status_code=status.HTTP_200_OK)
async def get_venue_carousel():
    """Public endpoint to fetch venue carousel slides"""
    carousel = await content_service.get_venue_carousel()
    
    if not carousel:
        raise_exception(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue carousel not found"
        )
    
    return carousel

@router.post("/venue-carousel/slide", status_code=status.HTTP_201_CREATED)
async def add_venue_slide(
    title: str = Form(...),
    description: str = Form(...),
    cta_text: str = Form(...),
    image: Union[UploadFile, str, None] = File(...)
):
    """Admin endpoint to add a new venue slide"""
    
    
    result = await content_service.add_venue_slide(title, description, cta_text, image=image)
    return {"message": "Slide added successfully", "data": result}

@router.put("/venue-carousel/slide/{slide_index}", status_code=status.HTTP_200_OK)
async def update_venue_slide(
    slide_index: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    cta_text: Optional[str] = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """Admin endpoint to update a venue slide"""
    
    
    result = await content_service.update_venue_slide(slide_index, title, description, cta_text, image=image)
    return {"message": "Slide updated successfully", "data": result}

@router.delete("/venue-carousel/slide/{slide_index}", status_code=status.HTTP_200_OK)
async def delete_venue_slide(slide_index: int):
    """Admin endpoint to delete a venue slide"""
    result = await content_service.delete_venue_slide(slide_index)
    return {"message": "Slide deleted successfully", "data": result}

@router.post("/venue-carousel/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_venue_carousel():
    """Admin endpoint to initialize venue carousel with default slides"""
    initial_data = {
        "section": "venue_carousel",
        "slides": [
            {
                "title": "LOS ANGELES",
                "description": "In Los Angeles, every strum feels cinematic. The city of stars turns concerts into stories, where lights, dreams, and songs blend into unforgettable scenes.",
                "cta_text": "Explore More",
                "image_path": ""
            },
            {
                "title": "NEW YORK",
                "description": "The city that never sleeps brings energy to every performance. Experience world-class venues and unforgettable nights.",
                "cta_text": "Discover NYC",
                "image_path": ""
            },
            {
                "title": "LONDON",
                "description": "Historic venues meet modern sounds. London's music scene offers a perfect blend of tradition and innovation.",
                "cta_text": "Explore London",
                "image_path": ""
            }
        ]
    }
    
    result = await content_service.initialize_venue_carousel(initial_data)
    return {"message": "Venue carousel initialized successfully", "data": result}


# ==================== BANDS SECTION ROUTES ====================

@router.get("/bands", response_model=BandsResponse, status_code=status.HTTP_200_OK)
async def get_bands_section():
    """Public endpoint to fetch bands section"""
    bands_section = await content_service.get_bands_section()
    
    if not bands_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bands section not found"
        )
    
    return bands_section

@router.put("/bands/header", status_code=status.HTTP_200_OK)
async def update_bands_header(
    heading: Optional[str] = Form(None),
    subheading: Optional[str] = Form(None)
):
    """Admin endpoint to update bands section heading and subheading"""
    result = await content_service.update_bands_section_header(heading, subheading)
    return {"message": "Bands section header updated successfully", "data": result}

@router.post("/bands/band", status_code=status.HTTP_201_CREATED)
async def add_band(
    title: str = Form(...),
    description: str = Form(...),
    cta_text: str = Form(...),
    image: Union[UploadFile, str, None] = File(None)
):
    """Admin endpoint to add a new band"""
    
    
    result = await content_service.add_band(title, description, cta_text, image=image)
    return {"message": "Band added successfully", "data": result}

@router.put("/bands/band/{band_index}", status_code=status.HTTP_200_OK)
async def update_band(
    band_index: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    cta_text: Optional[str] = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """Admin endpoint to update a band"""
    
    
    result = await content_service.update_band(band_index, title, description, cta_text, image=image)
    return {"message": "Band updated successfully", "data": result}

@router.delete("/bands/band/{band_index}", status_code=status.HTTP_200_OK)
async def delete_band(band_index: int):
    """Admin endpoint to delete a band"""
    result = await content_service.delete_band(band_index)
    return {"message": "Band deleted successfully", "data": result}

@router.post("/bands/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_bands_section():
    """Admin endpoint to initialize bands section with default content"""
    initial_data = {
        "section": "bands_section",
        "heading": "OUR BANDS",
        "subheading": "Thigalzhi® provides professional music bands, live performers, and festivals, and private events—spanning rock, jazz, classical, fusion, Bollywood, and more.",
        "bands": [
            {
                "title": "Rock & Roll Legends",
                "description": "Experience electrifying performances from the biggest names in rock music history.",
                "cta_text": "Explore"
            },
            {
                "title": "Jazz Masters",
                "description": "Smooth jazz performances that captivate audiences with soulful melodies.",
                "cta_text": "Explore"
            },
            {
                "title": "Royal Philharmonic Experience",
                "description": "Feel the grandeur of orchestral music as world-renowned performers take the stage.",
                "cta_text": "Explore"
            }
        ]
    }
    
    result = await content_service.initialize_bands_section(initial_data)
    return {"message": "Bands section initialized successfully", "data": result}



# ==================== FAQ SECTION ROUTES ====================

@router.get("/faq", response_model=FAQResponse, status_code=status.HTTP_200_OK)
async def get_faq_section():
    """Public endpoint to fetch FAQ section"""
    faq_section = await content_service.get_faq_section()
    
    if not faq_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ section not found"
        )
    
    return faq_section

@router.put("/faq/header", status_code=status.HTTP_200_OK)
async def update_faq_header(
    heading: Optional[str] = Form(None),
    subheading: Optional[str] = Form(None)
):
    """Admin endpoint to update FAQ section header"""
    result = await content_service.update_faq_header(heading, subheading)
    return {"message": "FAQ header updated successfully", "data": result}

@router.post("/faq/item", status_code=status.HTTP_201_CREATED)
async def add_faq(
    question: str = Form(...),
    answer: str = Form(...)
):
    """Admin endpoint to add new FAQ"""
    result = await content_service.add_faq(question, answer)
    return {"message": "FAQ added successfully", "data": result}

@router.put("/faq/item/{faq_index}", status_code=status.HTTP_200_OK)
async def update_faq(
    faq_index: int,
    question: Optional[str] = Form(None),
    answer: Optional[str] = Form(None)
):
    """Admin endpoint to update FAQ"""
    result = await content_service.update_faq(faq_index, question, answer)
    return {"message": "FAQ updated successfully", "data": result}

@router.delete("/faq/item/{faq_index}", status_code=status.HTTP_200_OK)
async def delete_faq(faq_index: int):
    """Admin endpoint to delete FAQ"""
    result = await content_service.delete_faq(faq_index)
    return {"message": "FAQ deleted successfully", "data": result}

@router.post("/faq/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_faq_section():
    """Admin endpoint to initialize FAQ section"""
    initial_data = {
        "section": "faq_section",
        "heading": "Frequently Asked Questions",
        "subheading": "DO YOU HAVE ANY OTHER QUESTIONS?",
        "faqs": [
            {
                "question": "How do I book a venue through Thigalzhi®?",
                "answer": "You can book a venue by browsing our venue catalog, selecting your preferred location, and completing the booking form with your event details."
            },
            {
                "question": "Can I schedule multiple concerts at once?",
                "answer": "Yes, our platform allows you to schedule multiple concerts simultaneously through our bulk booking feature."
            },
            {
                "question": "How do I modify or cancel a concert?",
                "answer": "You can modify or cancel concerts from your dashboard. Go to 'My Events' and select the event you wish to change."
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept credit cards, debit cards, UPI, net banking, and digital wallets for secure payments."
            },
            {
                "question": "Are there notifications for upcoming concerts?",
                "answer": "Yes, Thigalzhi® sends timely reminders and updates about your upcoming concerts. Notifications are available via email, SMS, or directly through the dashboard."
            },
            {
                "question": "How secure is my concert data on Thigalzhi®?",
                "answer": "We use industry-standard encryption and security protocols to protect your data. All transactions are secure and your information is never shared."
            },
            {
                "question": "Can I get refunds for canceled events?",
                "answer": "Refund policies vary based on the timing of cancellation. Please check our refund policy page or contact support for specific cases."
            },
            {
                "question": "Do you provide technical support for events?",
                "answer": "Yes, we offer 24/7 technical support for all events booked through Thigalzhi®. Contact our support team anytime for assistance."
            }
        ]
    }
    
    result = await content_service.initialize_faq_section(initial_data)
    return {"message": "FAQ section initialized successfully", "data": result}

# ==================== ABOUT US SECTION ROUTES ====================

@router.get("/about-us", response_model=AboutUsResponse, status_code=status.HTTP_200_OK)
async def get_about_us_section():
    """Public endpoint to fetch About Us section"""
    about_section = await content_service.get_about_us_section()
    
    if not about_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="About Us section not found"
        )
    
    return about_section

@router.put("/about-us/header", status_code=status.HTTP_200_OK)
async def update_about_us_header(
    badge: Optional[str] = Form(None),
    heading: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Admin endpoint to update About Us header"""
    result = await content_service.update_about_us_header(badge, heading, description)
    return {"message": "About Us header updated successfully", "data": result}

@router.post("/about-us/gallery", status_code=status.HTTP_201_CREATED)
async def add_gallery_image(
    image: Union[UploadFile, str, None] = File(...)
):
    """Admin endpoint to add gallery image"""
   
    
    
    result = await content_service.add_gallery_image(image=image)
    return {"message": "Gallery image added successfully", "data": result}

@router.delete("/about-us/gallery/{image_index}", status_code=status.HTTP_200_OK)
async def delete_gallery_image(image_index: int):
    """Admin endpoint to delete gallery image"""
    result = await content_service.delete_gallery_image(image_index)
    return {"message": "Gallery image deleted successfully", "data": result}

@router.post("/about-us/info-card", status_code=status.HTTP_201_CREATED)
async def add_info_card(
    icon: str = Form(...),
    title: str = Form(...),
    description: str = Form(...)
):
    """Admin endpoint to add info card"""
    result = await content_service.add_info_card(icon, title, description)
    return {"message": "Info card added successfully", "data": result}

@router.put("/about-us/info-card/{card_index}", status_code=status.HTTP_200_OK)
async def update_info_card(
    card_index: int,
    icon: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Admin endpoint to update info card"""
    result = await content_service.update_info_card(card_index, icon, title, description)
    return {"message": "Info card updated successfully", "data": result}

@router.delete("/about-us/info-card/{card_index}", status_code=status.HTTP_200_OK)
async def delete_info_card(card_index: int):
    """Admin endpoint to delete info card"""
    result = await content_service.delete_info_card(card_index)
    return {"message": "Info card deleted successfully", "data": result}

@router.post("/about-us/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_about_us_section():
    """Admin endpoint to initialize About Us section"""
    initial_data = {
        "section": "about_us_section",
        "badge": "Trusted Organization",
        "heading": "About Us",
        "description": "At Thigalzhi®, we revolutionize concert management by bridging performers, venues, and fans to create seamless, unforgettable musical experiences.",
        "gallery_images": [],
        "info_cards": [
            {
                "icon": "book",
                "title": "Our Story",
                "description": "Born from music passion and event planning innovation, we collaborate with venues, bands, and organizers worldwide."
            },
            {
                "icon": "eye",
                "title": "Our Vision",
                "description": "To become the world's most trusted platform for live event management, making concerts more accessible globally."
            },
            {
                "icon": "zap",
                "title": "Our Mission",
                "description": "Empowering organizers with tools that eliminate complexity while performers focus on incredible shows."
            },
            {
                "icon": "users",
                "title": "Our Team",
                "description": "Music enthusiasts and tech innovators transforming live music through creativity and cutting-edge solutions."
            }
        ]
    }
    
    result = await content_service.initialize_about_us_section(initial_data)
    return {"message": "About Us section initialized successfully", "data": result}


# ==================== FOOTER SECTION ROUTES ====================

@router.get("/footer", response_model=FooterResponse, status_code=status.HTTP_200_OK)
async def get_footer_section():
    """Public endpoint to fetch footer section"""
    footer = await content_service.get_footer_section()
    
    if not footer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Footer section not found"
        )
    
    return footer

@router.put("/footer/header", status_code=status.HTTP_200_OK)
async def update_footer_header(
    logo_text: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    copyright_text: Optional[str] = Form(None),
    image: Union[UploadFile, str, None] = File(None)
):
    """Admin endpoint to update footer header and background image"""
    
    
    result = await content_service.update_footer_header(logo_text, description, copyright_text, image=image)
    return {"message": "Footer header updated successfully", "data": result}

@router.put("/footer/contact", status_code=status.HTTP_200_OK)
async def update_contact_info(
    location: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None)
):
    """Admin endpoint to update contact information"""
    result = await content_service.update_contact_info(location, phone, email)
    return {"message": "Contact info updated successfully", "data": result}

@router.post("/footer/quick-link", status_code=status.HTTP_201_CREATED)
async def add_quick_link(
    name: str = Form(...),
    url: str = Form(...)
):
    """Admin endpoint to add quick link"""
    result = await content_service.add_quick_link(name, url)
    return {"message": "Quick link added successfully", "data": result}

@router.put("/footer/quick-link/{link_index}", status_code=status.HTTP_200_OK)
async def update_quick_link(
    link_index: int,
    name: Optional[str] = Form(None),
    url: Optional[str] = Form(None)
):
    """Admin endpoint to update quick link"""
    result = await content_service.update_quick_link(link_index, name, url)
    return {"message": "Quick link updated successfully", "data": result}

@router.delete("/footer/quick-link/{link_index}", status_code=status.HTTP_200_OK)
async def delete_quick_link(link_index: int):
    """Admin endpoint to delete quick link"""
    result = await content_service.delete_quick_link(link_index)
    return {"message": "Quick link deleted successfully", "data": result}

@router.post("/footer/social-link", status_code=status.HTTP_201_CREATED)
async def add_social_link(
    name: str = Form(...),
    url: str = Form(...)
):
    """Admin endpoint to add social link"""
    result = await content_service.add_social_link(name, url)
    return {"message": "Social link added successfully", "data": result}

@router.put("/footer/social-link/{link_index}", status_code=status.HTTP_200_OK)
async def update_social_link(
    link_index: int,
    name: Optional[str] = Form(None),
    url: Optional[str] = Form(None)
):
    """Admin endpoint to update social link"""
    result = await content_service.update_social_link(link_index, name, url)
    return {"message": "Social link updated successfully", "data": result}

@router.delete("/footer/social-link/{link_index}", status_code=status.HTTP_200_OK)
async def delete_social_link(link_index: int):
    """Admin endpoint to delete social link"""
    result = await content_service.delete_social_link(link_index)
    return {"message": "Social link deleted successfully", "data": result}

@router.post("/footer/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_footer_section():
    """Admin endpoint to initialize footer section"""
    initial_data = {
        "section": "footer_section",
        "logo_text": "Thigalzhi®",
        "description": "Thigalzhi® Concert Management is transforming live music experiences by connecting, venues, and fans with seamless technology. From booking to analytics, we make concerts unforgettable.",
        "contact": {
            "location": "Coimbatore, India",
            "phone": "+91 98765 43210",
            "email": "contact@thigalzhi.com"
        },
        "quick_links": [
            {"name": "About Us", "url": "/about"},
            {"name": "FAQ", "url": "/faq"}
        ],
        "social_links": [
            {"name": "Facebook", "url": "https://facebook.com/thigalzhi"},
            {"name": "Instagram", "url": "https://instagram.com/thigalzhi"},
            {"name": "LinkedIn", "url": "https://linkedin.com/company/thigalzhi"},
            {"name": "YouTube", "url": "https://youtube.com/thigalzhi"}
        ],
        "copyright_text": "© 2025 Thigalzhi® Concert Management. All rights reserved"
    }
    
    result = await content_service.initialize_footer_section(initial_data)
    return {"message": "Footer section initialized successfully", "data": result}
