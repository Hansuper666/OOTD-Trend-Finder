import os
import numpy as np
import torch
from PIL import Image
import openai
from transformers import CLIPProcessor, CLIPModel
from ..config.settings import settings
from ..utils.image_utils import preprocess_image
from sqlalchemy.orm import Session
from ..database.models import OutfitImage, ImageFeature, ImageTag

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

class AIService:
    def __init__(self):
        # Initialize CLIP model for image-text matching
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(settings.EMBEDDING_MODEL).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(settings.EMBEDDING_MODEL)
        
    def generate_image_embedding(self, image):
        """
        Generate embedding vector for an image using CLIP
        
        Args:
            image (PIL.Image): Image to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        # Convert to numpy and normalize
        embedding = image_features.cpu().numpy()[0]
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def generate_text_embedding(self, text):
        """
        Generate embedding vector for text using CLIP
        
        Args:
            text (str): Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector
        """
        inputs = self.processor(text=text, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        
        # Convert to numpy and normalize
        embedding = text_features.cpu().numpy()[0]
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding

    def analyze_image(self, image):
        """
        Analyze image using CLIP to match with predefined clothing tags
        
        Args:
            image (PIL.Image): Image to analyze
            
        Returns:
            str: JSON string containing analysis results
        """
        try:
            import json
            
            # Predefined clothing items
            clothing_items = [
                "jeans", "t-shirt", "blouse", "dress", "skirt", "pants", 
                "jacket", "coat", "sweater", "hoodie", "shorts", "blazer",
                "suit", "tank top", "shirt", "cardigan", "sweatshirt",
                "denim jacket", "leather jacket", "trench coat", "turtleneck",
                "polo shirt", "button-up shirt", "crop top", "jumpsuit", "romper"
            ]
            
            # Predefined styles
            styles = [
                "casual", "formal", "business casual", "streetwear", "vintage", 
                "bohemian", "preppy", "sporty", "athleisure", "minimalist",
                "elegant", "chic", "grunge", "punk", "retro", "classic", 
                "trendy", "edgy", "glamorous", "feminine", "masculine"
            ]
            
            # Predefined colors
            colors = [
                "red", "blue", "green", "yellow", "purple", "pink", "orange", 
                "black", "white", "gray", "brown", "beige", "navy", "teal",
                "maroon", "olive", "cream", "turquoise", "lavender", "burgundy"
            ]
            
            # Predefined occasions
            occasions = [
                "casual day out", "work", "formal event", "party", "date night",
                "weekend", "beach", "outdoor activity", "gym", "dinner",
                "interview", "wedding", "vacation", "travel", "business meeting"
            ]
            
            # Generate text embeddings for each category
            clothing_embeddings = [self.generate_text_embedding(item) for item in clothing_items]
            style_embeddings = [self.generate_text_embedding(style) for style in styles]
            color_embeddings = [self.generate_text_embedding(color) for color in colors]
            occasion_embeddings = [self.generate_text_embedding(occasion) for occasion in occasions]
            
            # Generate image embedding
            image_embedding = self.generate_image_embedding(image)
            
            # Find top matching clothing items
            clothing_scores = [np.dot(image_embedding, emb) for emb in clothing_embeddings]
            top_clothing_indices = np.argsort(clothing_scores)[-5:][::-1]  # Top 5 clothing items
            matched_clothing = [clothing_items[i] for i in top_clothing_indices if clothing_scores[i] > 0.2]
            
            # Find best matching style
            style_scores = [np.dot(image_embedding, emb) for emb in style_embeddings]
            best_style_index = np.argmax(style_scores)
            matched_style = styles[best_style_index]
            
            # Find top matching colors
            color_scores = [np.dot(image_embedding, emb) for emb in color_embeddings]
            top_color_indices = np.argsort(color_scores)[-3:][::-1]  # Top 3 colors
            matched_colors = [colors[i] for i in top_color_indices if color_scores[i] > 0.2]
            
            # Find top matching occasions
            occasion_scores = [np.dot(image_embedding, emb) for emb in occasion_embeddings]
            top_occasion_indices = np.argsort(occasion_scores)[-3:][::-1]  # Top 3 occasions
            matched_occasions = [occasions[i] for i in top_occasion_indices if occasion_scores[i] > 0.2]
            
            # Ensure we have at least some values
            if not matched_clothing:
                matched_clothing = ["unidentified clothing item"]
            if not matched_style:
                matched_style = "casual"
            if not matched_colors:
                matched_colors = ["neutral"]
            if not matched_occasions:
                matched_occasions = ["casual day out"]
            
            # Create analysis result
            analysis = {
                "clothing_items": matched_clothing,
                "style": matched_style,
                "color_palette": matched_colors,
                "occasions": matched_occasions
            }
            
            return json.dumps(analysis)
            
        except Exception as e:
            print(f"Error analyzing image with CLIP: {e}")
            import traceback
            traceback.print_exc()
            
            # Return fallback JSON in case of error
            default_response = {
                "clothing_items": ["clothing item"],
                "style": "casual",
                "color_palette": ["neutral"],
                "occasions": ["casual day out"]
            }
            return json.dumps(default_response)
    
    def find_similar_outfits(self, db: Session, embedding, limit=5):
        """
        Find similar outfits based on embedding similarity
        
        Args:
            db (Session): Database session
            embedding (np.ndarray): Embedding to compare against
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of similar OutfitImage objects
        """
        # Get all image features from the database
        image_features = db.query(ImageFeature).all()
        
        # Calculate similarity for each image
        results = []
        for feature in image_features:
            db_embedding = np.frombuffer(feature.embedding, dtype=np.float32)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding, db_embedding)
            
            if similarity >= settings.SIMILARITY_THRESHOLD:
                # Get the associated image
                image = db.query(OutfitImage).filter(OutfitImage.id == feature.image_id).first()
                results.append((image, similarity))
        
        # Sort by similarity (highest first) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def search_by_text(self, db: Session, query_text, limit=5):
        """
        Search for outfits using text query
        
        Args:
            db (Session): Database session
            query_text (str): Text query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching OutfitImage objects with similarity scores
        """
        # Generate embedding for the query text
        text_embedding = self.generate_text_embedding(query_text)
        
        # Find similar outfits
        return self.find_similar_outfits(db, text_embedding, limit)
    
    def search_by_image(self, db: Session, query_image, limit=5):
        """
        Search for outfits using uploaded image
        
        Args:
            db (Session): Database session
            query_image (PIL.Image): Query image
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching OutfitImage objects with similarity scores
        """
        # Generate embedding for the query image
        image_embedding = self.generate_image_embedding(query_image)
        
        # Find similar outfits
        return self.find_similar_outfits(db, image_embedding, limit)

    def get_tags_for_image(self, image):
        """
        Extract tags from image analysis
        
        Args:
            image (PIL.Image): Image to analyze
            
        Returns:
            list: List of (tag, confidence) tuples
        """
        try:
            # Analyze image
            analysis = self.analyze_image(image)
            
            import json
            try:
                analysis_dict = json.loads(analysis)
                
                # Extract tags with confidence
                tags = []
                
                # Add clothing items as tags
                if "clothing_items" in analysis_dict:
                    for item in analysis_dict["clothing_items"]:
                        tags.append((item, 0.95))  # High confidence for detected items
                
                # Add style as tag
                if "style" in analysis_dict:
                    tags.append((analysis_dict["style"], 0.9))
                    
                # Add colors as tags
                if "color_palette" in analysis_dict:
                    for color in analysis_dict["color_palette"]:
                        tags.append((color, 0.85))
                        
                # Add occasions as tags
                if "occasions" in analysis_dict:
                    for occasion in analysis_dict["occasions"]:
                        tags.append((occasion, 0.8))
                
                return tags
            except json.JSONDecodeError:
                # Return fallback tags if JSON parsing fails
                return [("clothing", 0.7), ("fashion", 0.7), ("outfit", 0.7)]
                
        except Exception as e:
            print(f"Error extracting tags from image: {e}")
            # Return fallback tags in case of error
            return [("clothing", 0.7), ("fashion", 0.7), ("outfit", 0.7)]

ai_service = AIService() 