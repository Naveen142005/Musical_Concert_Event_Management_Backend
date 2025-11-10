from pydantic import BaseModel, Field
from typing import List, Optional

class HeroStats(BaseModel):
    total_events: int
    satisfied_clients: str
    customer_rating: str
    tickets_sold: str

class HeroSectionUpdate(BaseModel):
    heading: Optional[str] = None
    subheading: Optional[str] = None
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None
    stats: Optional[HeroStats] = None

class HeroSectionResponse(BaseModel):
    _id: str
    section: str = "hero_section"
    heading: str
    subheading: str
    cta_text: str
    cta_link: str
    stats: HeroStats
    image_path: Optional[str] = None




class VenueSlide(BaseModel):
    title: str
    description: str
    cta_text: str
    image_path: Optional[str] = None

class VenueCarouselResponse(BaseModel):
    _id: str
    section: str = "venue_carousel"
    slides: List[VenueSlide]

class VenueSlideUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cta_text: Optional[str] = None



class BandCard(BaseModel):
    title: str
    description: str
    cta_text: str
    image_path: Optional[str] = None
    image_url: Optional[str] = None

class BandsResponse(BaseModel):
    _id: str
    section: str = "bands_section"
    heading: str
    subheading: str
    bands: List[BandCard]


class FAQItem(BaseModel):
    question: str
    answer: str

class FAQResponse(BaseModel):
    _id: str
    section: str = "faq_section"
    heading: str
    subheading: str
    faqs: List[FAQItem]



class AboutUsInfo(BaseModel):
    icon: str  # icon name or class
    title: str
    description: str

class AboutUsResponse(BaseModel):
    _id: str
    section: str = "about_us_section"
    badge: str
    heading: str
    description: str
    gallery_images: List[str] = []  # List of image URLs
    info_cards: List[AboutUsInfo]


class ContactInfo(BaseModel):
    location: str
    phone: str
    email: str

class QuickLink(BaseModel):
    name: str
    url: str

class SocialLink(BaseModel):
    name: str
    url: str

class FooterResponse(BaseModel):
    _id: str
    section: str = "footer_section"
    logo_text: str
    description: str
    contact: ContactInfo
    quick_links: List[QuickLink]
    social_links: List[SocialLink]
    copyright_text: str
    background_image: Optional[str] = None
    background_image_url: Optional[str] = None
