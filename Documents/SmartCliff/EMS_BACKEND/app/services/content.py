from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile
from pathlib import Path
import shutil
import uuid
from app.database.connection_mongo import content
from app.utils.common import get_image_url, raise_exception, validate_image_file

# Create upload directory
UPLOAD_DIR = Path("uploads/content")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ContentService:
    
    async def get_hero_content(self):
        """Fetch current hero section content"""
        try:
            hero_doc = await content.find_one({"section": "hero_section"})
            if hero_doc:
                hero_doc["_id"] = str(hero_doc["_id"])
                
                if (hero_doc["image_path"]):
                    hero_doc["image_path"] = get_image_url(hero_doc["image_path"])
                return hero_doc
            return None
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")
        
    async def update_hero_content(
        self,
        heading: Optional[str],
        subheading: Optional[str],
        cta_text: Optional[str],
        cta_link: Optional[str],
        total_events: Optional[str],
        satisfied_clients: Optional[str],
        customer_rating: Optional[str],
        tickets_sold: Optional[str],
        image: Optional[UploadFile]
    ):
    
        try:
            update_data = {}
            
            # Text field validations
            if heading:
                if len(heading.strip()) < 3:
                    raise_exception(status_code=422, detail="Heading length should be above 2")
                update_data["heading"] = heading.strip()
                
            if subheading:
                if len(subheading.strip()) < 3:
                    raise_exception(status_code=422, detail="Sub heading length should be above 2")
                update_data["subheading"] = subheading.strip()
                
            if cta_text:
                if len(cta_text.strip()) < 2:
                    raise_exception(status_code=422, detail="CTA text length should be above 1")
                update_data["cta_text"] = cta_text.strip()
                
            if cta_link:
                if not cta_link.strip().startswith(('/', 'http://', 'https://')):
                    raise_exception(status_code=422, detail="Invalid Link. Link should start with /, http://, or https://")
                update_data["cta_link"] = cta_link.strip()
            
            # Stats validations
            stats = {}
            if total_events and total_events.strip():
                try:
                    events_int = int(total_events)
                    if events_int >= 0:
                        stats["total_events"] = events_int
                except ValueError:
                    pass
            if satisfied_clients and satisfied_clients.strip():
                stats["satisfied_clients"] = satisfied_clients.strip()
            if customer_rating and customer_rating.strip():
                stats["customer_rating"] = customer_rating.strip()
            if tickets_sold and tickets_sold.strip():
                stats["tickets_sold"] = tickets_sold.strip()
            if stats:
                update_data["stats"] = stats
            
            # Image validation and save
            if image  and image.filename:
                await validate_image_file(image, max_size_mb=5)  
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                update_data["image_path"] = str(file_path)
            
            if not update_data:
                raise_exception(status_code=400, detail="No fields to update")
            
            # Update database
            result = await content.update_one(
                {"section": "hero_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_hero_content()
            else:
                raise_exception(status_code=404, detail="Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")

    async def initialize_hero_content(self, initial_data: Dict[str, Any]):
        """Initialize hero section with default content"""
        try:
            existing = await content.find_one({"section": "hero_section"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_hero_content()
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")


    # Venue section 
    
    async def get_venue_carousel(self):
        """Fetch venue carousel content"""
        try:
            carousel = await content.find_one({"section": "venue_carousel"})
            if carousel:
                carousel["_id"] = str(carousel["_id"])
                
                # Convert image paths to URLs
                if "slides" in carousel:
                    for slide in carousel["slides"]:
                        if "image_path" in slide and slide["image_path"]:
                            image_path = get_image_url(slide["image_path"])
                            slide["image_path"] = image_path
                        else:
                            image_path = None
                            slide["image_path"] = None
                return carousel
            return None
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")
    
    async def add_venue_slide(
        self,
        title: str,
        description: str,
        cta_text: str,
        image: Optional[UploadFile]
    ):
        """Add a new slide to venue carousel"""
        try:
            # Validate inputs
            if not title or len(title.strip()) < 3:
                raise_exception(status_code=422, detail="Title must be at least 3 characters")
            if not description or len(description.strip()) < 10:
                raise_exception(status_code=422, detail="Description must be at least 10 characters")
            if not cta_text or len(cta_text.strip()) < 2:
                raise_exception(status_code=422, detail="CTA text must be at least 2 characters")
            
            slide_data = {
                "title": title.strip(),
                "description": description.strip(),
                "cta_text": cta_text.strip()
            }
            
            # Handle image upload
            if image and image.filename:
                await validate_image_file(image, max_size_mb=5)
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                slide_data["image_path"] = (str(file_path))
            
            # Add slide to carousel
            result = await content.update_one(
                {"section": "venue_carousel"},
                {"$push": {"slides": slide_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_venue_carousel()
            else:
                raise_exception(status_code=404, detail="Failed to add slide")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")
    
    async def update_venue_slide(
        self,
        slide_index: int,
        title: Optional[str],
        description: Optional[str],
        cta_text: Optional[str],
        image: Optional[UploadFile]
    ):
        
        """Update a specific slide in venue carousel"""
        try:
            # Get current carousel
            carousel = await content.find_one({"section": "venue_carousel"})
            if not carousel or "slides" not in carousel:
                raise_exception(status_code=404, detail="Venue carousel not found")
            
            if slide_index < 0 or slide_index >= len(carousel["slides"]):
                raise_exception(status_code=404, detail=f"Slide index {slide_index} not found")
            
            update_fields = {}
            
            # Validate and update fields
            if title:
                if len(title.strip()) < 3:
                    raise_exception(status_code=422, detail="Title must be at least 3 characters")
                update_fields[f"slides.{slide_index}.title"] = title.strip()
            
            if description:
                if len(description.strip()) < 10:
                    raise_exception(status_code=422, detail="Description must be at least 10 characters")
                update_fields[f"slides.{slide_index}.description"] = description.strip()
            
            if cta_text:
                if len(cta_text.strip()) < 2:
                    raise_exception(status_code=422, detail="CTA text must be at least 2 characters")
                update_fields[f"slides.{slide_index}.cta_text"] = cta_text.strip()
            
            # Handle image upload
            if image and image.filename:
                await validate_image_file(image, max_size_mb=5)
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                update_fields[f"slides.{slide_index}.image_path"] = str(file_path)
            
            if not update_fields:
                raise_exception(status_code=400, detail="No fields to update")
            
            # Update slide
            result = await content.update_one(
                {"section": "venue_carousel"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_venue_carousel()
            else:
                raise_exception(status_code=404, detail="Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")
    
    async def delete_venue_slide(self, slide_index: int):
        """Delete a slide from venue carousel"""
        try:
            # Get current carousel
            carousel = await content.find_one({"section": "venue_carousel"})
            if not carousel or "slides" not in carousel:
                raise_exception(status_code=404, detail="Venue carousel not found")
            print(len(carousel["slides"]))
            print(slide_index)
            print(slide_index >= len(carousel["slides"]))
            
            if slide_index < 0 or slide_index >= len(carousel["slides"]):
                print("ehiiiiiiiiii")
                raise_exception(status_code=404, detail=f"Slide index {slide_index} not found")
            
            # Get slide to delete (for file cleanup)
            slide_to_delete = carousel["slides"][slide_index]
            
            # Delete from array
            carousel["slides"].pop(slide_index)
            
            # Update database
            result = await content.update_one(
                {"section": "venue_carousel"},
                {"$set": {"slides": carousel["slides"]}}
            )
            
            # Delete image file if exists
            if "image_path" in slide_to_delete and slide_to_delete["image_path"]:
                try:
                    Path(slide_to_delete["image_path"]).unlink(missing_ok=True)
                except:
                    pass
            
            if result.matched_count > 0:
                return await self.get_venue_carousel()
            else:
                raise_exception(status_code=404, detail="Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")
    
    async def initialize_venue_carousel(self, initial_data: Dict[str, Any]):
        """Initialize venue carousel with default slides"""
        try:
            existing = await content.find_one({"section": "venue_carousel"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_venue_carousel()
            
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(status_code=500, detail=f"Database error: {str(e)}")

    #BAND--------------------------
    
    async def get_bands_section(self):
        """Fetch bands section content"""
        try:
            bands_section = await content.find_one({"section": "bands_section"})
            if bands_section:
                bands_section["_id"] = str(bands_section["_id"])
                
                # Convert image paths to absolute URLs
                if "bands" in bands_section:
                    for band in bands_section["bands"]:
                        if "image_path" in band and band["image_path"]:
                            band["image_url"] = get_image_url(band["image_path"])
                        else:
                            band["image_path"] = None
                            band["image_url"] = None
                
                return bands_section
            return None
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_band(
        self,
        title: str,
        description: str,
        cta_text: str,
        image: Optional[UploadFile]
    ):
        """Add a new band to bands section"""
        try:
            # Validate inputs
            if not title or len(title.strip()) < 3:
                raise_exception(422, "Band title must be at least 3 characters")
            if not description or len(description.strip()) < 10:
                raise_exception(422, "Band description must be at least 10 characters")
            if not cta_text or len(cta_text.strip()) < 2:
                raise_exception(422, "CTA text must be at least 2 characters")
            
            band_data = {
                "title": title.strip(),
                "description": description.strip(),
                "cta_text": cta_text.strip()
            }
            
            # Handle image upload
            if image and image.filename:
                await validate_image_file(image, max_size_mb=5)
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                # Store relative path in DB
                relative_path = f"uploads/content/{filename}"
                band_data["image_path"] = relative_path
            
            # Add band to section
            result = await content.update_one(
                {"section": "bands_section"},
                {"$push": {"bands": band_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_bands_section()
            else:
                raise_exception(404, "Failed to add band")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_band(
        self,
        band_index: int,
        title: Optional[str],
        description: Optional[str],
        cta_text: Optional[str],
        image: Optional[UploadFile]
    ):
        """Update a specific band in bands section"""
        try:
            # Get current bands section
            bands_section = await content.find_one({"section": "bands_section"})
            if not bands_section or "bands" not in bands_section:
                raise_exception(404, "Bands section not found")
            
            if band_index < 0 or band_index >= len(bands_section["bands"]):
                raise_exception(404, f"Band index {band_index} not found")
            
            update_fields = {}
            
            # Validate and update fields
            if title:
                if len(title.strip()) < 3:
                    raise_exception(422, "Band title must be at least 3 characters")
                update_fields[f"bands.{band_index}.title"] = title.strip()
            
            if description:
                if len(description.strip()) < 10:
                    raise_exception(422, "Band description must be at least 10 characters")
                update_fields[f"bands.{band_index}.description"] = description.strip()
            
            if cta_text:
                if len(cta_text.strip()) < 2:
                    raise_exception(422, "CTA text must be at least 2 characters")
                update_fields[f"bands.{band_index}.cta_text"] = cta_text.strip()
            
            # Handle image upload
            print(image)
            if image and image.filename:
                await validate_image_file(image, max_size_mb=5)
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                # Store relative path in DB
                relative_path = f"uploads/content/{filename}"
                print(relative_path)
                update_fields[f"bands.{band_index}.image_path"] = relative_path
            
            if not update_fields:
                raise_exception(400, "No fields to update")
            
            # Update band
            result = await content.update_one(
                {"section": "bands_section"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_bands_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_band(self, band_index: int):
        """Delete a band from bands section"""
        try:
            # Get current bands section
            bands_section = await content.find_one({"section": "bands_section"})
            if not bands_section or "bands" not in bands_section:
                raise_exception(404, "Bands section not found")
            
            if band_index < 0 or band_index >= len(bands_section["bands"]):
                raise_exception(404, f"Band index {band_index} not found")
            
            # Get band to delete (for file cleanup)
            band_to_delete = bands_section["bands"][band_index]
            
            # Delete from array
            bands_section["bands"].pop(band_index)
            
            # Update database
            result = await content.update_one(
                {"section": "bands_section"},
                {"$set": {"bands": bands_section["bands"]}}
            )
            
            # Delete image file if exists
            if "image_path" in band_to_delete and band_to_delete["image_path"]:
                try:
                    abs_path = get_image_url(band_to_delete["image_path"])
                    Path(abs_path).unlink(missing_ok=True)
                except:
                    pass
            
            if result.matched_count > 0:
                return await self.get_bands_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_bands_section_header(
        self,
        heading: Optional[str],
        subheading: Optional[str]
    ):
        """Update bands section heading and subheading"""
        try:
            update_data = {}
            
            if heading:
                if len(heading.strip()) < 3:
                    raise_exception(422, "Heading must be at least 3 characters")
                update_data["heading"] = heading.strip()
            
            if subheading:
                if len(subheading.strip()) < 10:
                    raise_exception(422, "Subheading must be at least 10 characters")
                update_data["subheading"] = subheading.strip()
            
            if not update_data:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "bands_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_bands_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def initialize_bands_section(self, initial_data: Dict[str, Any]):
        """Initialize bands section with default content"""
        try:
            existing = await content.find_one({"section": "bands_section"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_bands_section()
            
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")


#FAQ

    
    async def get_faq_section(self):
        """Fetch FAQ section"""
        try:
            faq_section = await content.find_one({"section": "faq_section"})
            if faq_section:
                faq_section["_id"] = str(faq_section["_id"])
                return faq_section
            return None
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_faq(self, question: str, answer: str):
        """Add new FAQ"""
        try:
            if not question or len(question.strip()) < 5:
                raise_exception(422, "Question must be at least 5 characters")
            if not answer or len(answer.strip()) < 10:
                raise_exception(422, "Answer must be at least 10 characters")
            
            faq_data = {
                "question": question.strip(),
                "answer": answer.strip()
            }
            
            result = await content.update_one(
                {"section": "faq_section"},
                {"$push": {"faqs": faq_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_faq_section()
            else:
                raise_exception(404, "Failed to add FAQ")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_faq(
        self,
        faq_index: int,
        question: Optional[str],
        answer: Optional[str]
    ):
        """Update specific FAQ"""
        try:
            faq_section = await content.find_one({"section": "faq_section"})
            if not faq_section or "faqs" not in faq_section:
                raise_exception(404, "FAQ section not found")
            
            if faq_index < 0 or faq_index >= len(faq_section["faqs"]):
                raise_exception(404, f"FAQ index {faq_index} not found")
            
            update_fields = {}
            
            if question:
                if len(question.strip()) < 5:
                    raise_exception(422, "Question must be at least 5 characters")
                update_fields[f"faqs.{faq_index}.question"] = question.strip()
            
            if answer:
                if len(answer.strip()) < 10:
                    raise_exception(422, "Answer must be at least 10 characters")
                update_fields[f"faqs.{faq_index}.answer"] = answer.strip()
            
            if not update_fields:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "faq_section"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_faq_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_faq(self, faq_index: int):
        """Delete FAQ"""
        try:
            faq_section = await content.find_one({"section": "faq_section"})
            if not faq_section or "faqs" not in faq_section:
                raise_exception(404, "FAQ section not found")
            
            if faq_index < 0 or faq_index >= len(faq_section["faqs"]):
                raise_exception(404, f"FAQ index {faq_index} not found")
            
            faq_section["faqs"].pop(faq_index)
            
            result = await content.update_one(
                {"section": "faq_section"},
                {"$set": {"faqs": faq_section["faqs"]}}
            )
            
            if result.matched_count > 0:
                return await self.get_faq_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_faq_header(
        self,
        heading: Optional[str],
        subheading: Optional[str]
    ):
        """Update FAQ section header"""
        try:
            update_data = {}
            
            if heading:
                if len(heading.strip()) < 3:
                    raise_exception(422, "Heading must be at least 3 characters")
                update_data["heading"] = heading.strip()
            
            if subheading:
                if len(subheading.strip()) < 5:
                    raise_exception(422, "Subheading must be at least 5 characters")
                update_data["subheading"] = subheading.strip()
            
            if not update_data:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "faq_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_faq_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def initialize_faq_section(self, initial_data: Dict[str, Any]):
        """Initialize FAQ section"""
        try:
            existing = await content.find_one({"section": "faq_section"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_faq_section()
            
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")

#ABOUT US
    async def get_about_us_section(self) :
        """Fetch About Us section"""
        try:
            about_section = await content.find_one({"section": "about_us_section"})
            if about_section:
                about_section["_id"] = str(about_section["_id"])
                
                # Convert gallery image paths to absolute URLs
                if "gallery_images" in about_section:
                    about_section["gallery_images"] = [
                        get_image_url(img) for img in about_section["gallery_images"]
                    ]
                
                return about_section
            return None
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_about_us_header(
        self,
        badge: Optional[str],
        heading: Optional[str],
        description: Optional[str]
    ) :
        """Update About Us header"""
        try:
            update_data = {}
            
            if badge:
                if len(badge.strip()) < 2:
                    raise_exception(422, "Badge must be at least 2 characters")
                update_data["badge"] = badge.strip()
            
            if heading:
                if len(heading.strip()) < 3:
                    raise_exception(422, "Heading must be at least 3 characters")
                update_data["heading"] = heading.strip()
            
            if description:
                if len(description.strip()) < 10:
                    raise_exception(422, "Description must be at least 10 characters")
                update_data["description"] = description.strip()
            
            if not update_data:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_gallery_image(self, image: UploadFile) :
        """Add image to gallery"""
        try:
            if not image or not image.filename:
                raise_exception(400, "Image is required")
            
            await validate_image_file(image, max_size_mb=5)
            
            file_ext = Path(image.filename).suffix.lower()
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            relative_path = f"uploads/content/{filename}"
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$push": {"gallery_images": relative_path}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Failed to add image")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_gallery_image(self, image_index: int) :
        """Delete gallery image"""
        try:
            about_section = await content.find_one({"section": "about_us_section"})
            if not about_section or "gallery_images" not in about_section:
                raise_exception(404, "About Us section not found")
            
            if image_index < 0 or image_index >= len(about_section["gallery_images"]):
                raise_exception(404, f"Image index {image_index} not found")
            
            image_to_delete = about_section["gallery_images"][image_index]
            about_section["gallery_images"].pop(image_index)
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$set": {"gallery_images": about_section["gallery_images"]}}
            )
            
            # Delete file
            if image_to_delete:
                try:
                    abs_path = get_image_url(image_to_delete)
                    Path(abs_path).unlink(missing_ok=True)
                except:
                    pass
            
            if result.matched_count > 0:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_info_card(
        self,
        icon: str,
        title: str,
        description: str
    ) :
        """Add info card"""
        try:
            if not icon or len(icon.strip()) < 1:
                raise_exception(422, "Icon is required")
            if not title or len(title.strip()) < 3:
                raise_exception(422, "Title must be at least 3 characters")
            if not description or len(description.strip()) < 10:
                raise_exception(422, "Description must be at least 10 characters")
            
            card_data = {
                "icon": icon.strip(),
                "title": title.strip(),
                "description": description.strip()
            }
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$push": {"info_cards": card_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Failed to add info card")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_info_card(
        self,
        card_index: int,
        icon: Optional[str],
        title: Optional[str],
        description: Optional[str]
    ) :
        """Update info card"""
        try:
            about_section = await content.find_one({"section": "about_us_section"})
            if not about_section or "info_cards" not in about_section:
                raise_exception(404, "About Us section not found")
            
            if card_index < 0 or card_index >= len(about_section["info_cards"]):
                raise_exception(404, f"Info card index {card_index} not found")
            
            update_fields = {}
            
            if icon:
                if len(icon.strip()) < 1:
                    raise_exception(422, "Icon is required")
                update_fields[f"info_cards.{card_index}.icon"] = icon.strip()
            
            if title:
                if len(title.strip()) < 3:
                    raise_exception(422, "Title must be at least 3 characters")
                update_fields[f"info_cards.{card_index}.title"] = title.strip()
            
            if description:
                if len(description.strip()) < 10:
                    raise_exception(422, "Description must be at least 10 characters")
                update_fields[f"info_cards.{card_index}.description"] = description.strip()
            
            if not update_fields:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_info_card(self, card_index: int) :
        """Delete info card"""
        try:
            about_section = await content.find_one({"section": "about_us_section"})
            if not about_section or "info_cards" not in about_section:
                raise_exception(404, "About Us section not found")
            
            if card_index < 0 or card_index >= len(about_section["info_cards"]):
                raise_exception(404, f"Info card index {card_index} not found")
            
            about_section["info_cards"].pop(card_index)
            
            result = await content.update_one(
                {"section": "about_us_section"},
                {"$set": {"info_cards": about_section["info_cards"]}}
            )
            
            if result.matched_count > 0:
                return await self.get_about_us_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def initialize_about_us_section(self, initial_data: Dict[str, Any]) :
        """Initialize About Us section"""
        try:
            existing = await content.find_one({"section": "about_us_section"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_about_us_section()
            
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")



class ContentService:
    # ... existing methods ...
    
    async def get_footer_section(self) :
        """Fetch footer section"""
        try:
            footer = await content.find_one({"section": "footer_section"})
            if footer:
                footer["_id"] = str(footer["_id"])
                
                # Convert background image path to URL
                if "background_image" in footer and footer["background_image"]:
                    footer["background_image_url"] = get_image_url(footer["background_image"])
                else:
                    footer["background_image"] = None
                    footer["background_image_url"] = None
                
                return footer
            return None
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_footer_header(
        self,
        logo_text: Optional[str],
        description: Optional[str],
        copyright_text: Optional[str],
        image: Optional[UploadFile]
    ) :
        """Update footer header info and background image"""
        try:
            update_data = {}
            
            if logo_text:
                if len(logo_text.strip()) < 2:
                    raise_exception(422, "Logo text must be at least 2 characters")
                update_data["logo_text"] = logo_text.strip()
            
            if description:
                if len(description.strip()) < 10:
                    raise_exception(422, "Description must be at least 10 characters")
                update_data["description"] = description.strip()
            
            if copyright_text:
                if len(copyright_text.strip()) < 5:
                    raise_exception(422, "Copyright text must be at least 5 characters")
                update_data["copyright_text"] = copyright_text.strip()
            
            # Handle background image
            if image and image.filename:
                await validate_image_file(image, max_size_mb=5)
                
                file_ext = Path(image.filename).suffix.lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                relative_path = f"uploads/content/{filename}"
                update_data["background_image"] = relative_path
            
            if not update_data:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_contact_info(
        self,
        location: Optional[str],
        phone: Optional[str],
        email: Optional[str]
    ) :
        """Update contact information"""
        try:
            update_data = {}
            
            if location:
                if len(location.strip()) < 3:
                    raise_exception(422, "Location must be at least 3 characters")
                update_data["contact.location"] = location.strip()
            
            if phone:
                if len(phone.strip()) < 10:
                    raise_exception(422, "Phone must be at least 10 characters")
                update_data["contact.phone"] = phone.strip()
            
            if email:
                if len(email.strip()) < 5 or "@" not in email:
                    raise_exception(422, "Valid email is required")
                update_data["contact.email"] = email.strip()
            
            if not update_data:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": update_data},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_quick_link(self, name: str, url: str) :
        """Add quick link"""
        try:
            if not name or len(name.strip()) < 2:
                raise_exception(422, "Link name must be at least 2 characters")
            if not url or len(url.strip()) < 3:
                raise_exception(422, "Link URL must be at least 3 characters")
            if not url.strip().startswith(('/', 'http://', 'https://')):
                raise_exception(422, "Link URL must start with /, http://, or https://")
            
            link_data = {
                "name": name.strip(),
                "url": url.strip()
            }
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$push": {"quick_links": link_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Failed to add quick link")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_quick_link(
        self,
        link_index: int,
        name: Optional[str],
        url: Optional[str]
    ) :
        """Update quick link"""
        try:
            footer = await content.find_one({"section": "footer_section"})
            if not footer or "quick_links" not in footer:
                raise_exception(404, "Footer section not found")
            
            if link_index < 0 or link_index >= len(footer["quick_links"]):
                raise_exception(404, f"Quick link index {link_index} not found")
            
            update_fields = {}
            
            if name:
                if len(name.strip()) < 2:
                    raise_exception(422, "Link name must be at least 2 characters")
                update_fields[f"quick_links.{link_index}.name"] = name.strip()
            
            if url:
                if len(url.strip()) < 3:
                    raise_exception(422, "Link URL must be at least 3 characters")
                if not url.strip().startswith(('/', 'http://', 'https://')):
                    raise_exception(422, "Link URL must start with /, http://, or https://")
                update_fields[f"quick_links.{link_index}.url"] = url.strip()
            
            if not update_fields:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_quick_link(self, link_index: int) :
        """Delete quick link"""
        try:
            footer = await content.find_one({"section": "footer_section"})
            if not footer or "quick_links" not in footer:
                raise_exception(404, "Footer section not found")
            
            if link_index < 0 or link_index >= len(footer["quick_links"]):
                raise_exception(404, f"Quick link index {link_index} not found")
            
            footer["quick_links"].pop(link_index)
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": {"quick_links": footer["quick_links"]}}
            )
            
            if result.matched_count > 0:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def add_social_link(self, name: str, url: str) :
        """Add social link"""
        try:
            if not name or len(name.strip()) < 2:
                raise_exception(422, "Social link name must be at least 2 characters")
            if not url or len(url.strip()) < 5:
                raise_exception(422, "Social link URL must be at least 5 characters")
            if not url.strip().startswith(('http://', 'https://')):
                raise_exception(422, "Social link URL must start with http:// or https://")
            
            link_data = {
                "name": name.strip(),
                "url": url.strip()
            }
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$push": {"social_links": link_data}},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Failed to add social link")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def update_social_link(
        self,
        link_index: int,
        name: Optional[str],
        url: Optional[str]
    ) :
        """Update social link"""
        try:
            footer = await content.find_one({"section": "footer_section"})
            if not footer or "social_links" not in footer:
                raise_exception(404, "Footer section not found")
            
            if link_index < 0 or link_index >= len(footer["social_links"]):
                raise_exception(404, f"Social link index {link_index} not found")
            
            update_fields = {}
            
            if name:
                if len(name.strip()) < 2:
                    raise_exception(422, "Social link name must be at least 2 characters")
                update_fields[f"social_links.{link_index}.name"] = name.strip()
            
            if url:
                if len(url.strip()) < 5:
                    raise_exception(422, "Social link URL must be at least 5 characters")
                if not url.strip().startswith(('http://', 'https://')):
                    raise_exception(422, "Social link URL must start with http:// or https://")
                update_fields[f"social_links.{link_index}.url"] = url.strip()
            
            if not update_fields:
                raise_exception(400, "No fields to update")
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": update_fields}
            )
            
            if result.matched_count > 0:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Update failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def delete_social_link(self, link_index: int) :
        """Delete social link"""
        try:
            footer = await content.find_one({"section": "footer_section"})
            if not footer or "social_links" not in footer:
                raise_exception(404, "Footer section not found")
            
            if link_index < 0 or link_index >= len(footer["social_links"]):
                raise_exception(404, f"Social link index {link_index} not found")
            
            footer["social_links"].pop(link_index)
            
            result = await content.update_one(
                {"section": "footer_section"},
                {"$set": {"social_links": footer["social_links"]}}
            )
            
            if result.matched_count > 0:
                return await self.get_footer_section()
            else:
                raise_exception(404, "Delete failed")
                
        except HTTPException:
            raise
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")
    
    async def initialize_footer_section(self, initial_data: Dict[str, Any]) :
        """Initialize footer section"""
        try:
            existing = await content.find_one({"section": "footer_section"})
            if not existing:
                await content.insert_one(initial_data)
                return await self.get_footer_section()
            
            existing["_id"] = str(existing["_id"])
            return existing
        except Exception as e:
            raise_exception(500, f"Database error: {str(e)}")



content_service = ContentService()
