"""
Handler for crop_production_info table operations in Supabase
"""

from typing import Optional, Dict, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv('config/openai_key.env')

class CropProductionInfoHandler:
    """Handler for managing crop production information in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL', 'https://itcsdacjopedjcyhqyki.supabase.co')
        supabase_key = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk')
        
        if not supabase_key:
            raise ValueError("SUPABASE_ANON_KEY not found in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table_name = 'crop_production_info'
    
    def get_crop_id_by_name(self, crop_name: str) -> Optional[int]:
        """Get crop ID by crop name"""
        try:
            result = self.supabase.table('crops').select('id').eq('crop_name', crop_name.lower()).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            return None
        except Exception as e:
            print(f"Error getting crop ID for {crop_name}: {e}")
            return None
    
    def insert_production_info(
        self,
        crop_name: str,
        production_notes: Optional[str] = None,
        land_preparation: Optional[str] = None,
        manure_application: Optional[str] = None,
        planting_info: Optional[str] = None,
        fertilizer_application: Optional[str] = None,
        weeding: Optional[str] = None,
        storing: Optional[str] = None,
        source_document: Optional[str] = None,
        extraction_confidence: int = 80
    ) -> Dict[str, Any]:
        """
        Insert crop production information
        
        Args:
            crop_name: Name of the crop
            production_notes: Things to take note in production
            land_preparation: Land preparation information
            manure_application: Manure application information
            planting_info: General planting information
            fertilizer_application: Fertilizer application information
            weeding: Weeding information
            storing: Storage requirements and harvesting guidelines
            source_document: Source PDF or document name
            extraction_confidence: Confidence score (0-100)
        
        Returns:
            Dict with success status and data/error message
        """
        try:
            # Get crop ID
            crop_id = self.get_crop_id_by_name(crop_name)
            if not crop_id:
                return {
                    'success': False,
                    'error': f'Crop "{crop_name}" not found in database'
                }
            
            # Prepare data
            data = {
                'crop_id': crop_id,
                'extraction_confidence': extraction_confidence
            }
            
            # Add optional fields
            if production_notes:
                data['production_notes'] = production_notes
            if land_preparation:
                data['land_preparation'] = land_preparation
            if manure_application:
                data['manure_application'] = manure_application
            if planting_info:
                data['planting_info'] = planting_info
            if fertilizer_application:
                data['fertilizer_application'] = fertilizer_application
            if weeding:
                data['weeding'] = weeding
            if storing:
                data['storing'] = storing
            if source_document:
                data['source_document'] = source_document
            
            # Insert or update (upsert)
            result = self.supabase.table(self.table_name).upsert(
                data,
                on_conflict='crop_id'
            ).execute()
            
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_production_info(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """
        Get production information for a crop
        
        Args:
            crop_name: Name of the crop
        
        Returns:
            Dict with production info or None if not found
        """
        try:
            crop_id = self.get_crop_id_by_name(crop_name)
            if not crop_id:
                return None
            
            result = self.supabase.table(self.table_name).select('*').eq('crop_id', crop_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting production info for {crop_name}: {e}")
            return None
    
    def get_all_production_info(self) -> list:
        """
        Get all crop production information
        
        Returns:
            List of all production info records with crop names
        """
        try:
            result = self.supabase.table(self.table_name).select(
                '*, crops(crop_name, scientific_name, category)'
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting all production info: {e}")
            return []
    
    def update_production_info(
        self,
        crop_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update production information for a crop
        
        Args:
            crop_name: Name of the crop
            **kwargs: Fields to update (production_notes, land_preparation, etc.)
        
        Returns:
            Dict with success status and data/error message
        """
        try:
            crop_id = self.get_crop_id_by_name(crop_name)
            if not crop_id:
                return {
                    'success': False,
                    'error': f'Crop "{crop_name}" not found in database'
                }
            
            # Prepare update data
            update_data = {}
            allowed_fields = [
                'production_notes', 'land_preparation', 'manure_application',
                'planting_info', 'fertilizer_application', 'weeding', 'storing',
                'source_document', 'extraction_confidence'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
            
            if not update_data:
                return {
                    'success': False,
                    'error': 'No valid fields to update'
                }
            
            # Update
            result = self.supabase.table(self.table_name).update(
                update_data
            ).eq('crop_id', crop_id).execute()
            
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_production_info(self, crop_name: str) -> Dict[str, Any]:
        """
        Delete production information for a crop
        
        Args:
            crop_name: Name of the crop
        
        Returns:
            Dict with success status
        """
        try:
            crop_id = self.get_crop_id_by_name(crop_name)
            if not crop_id:
                return {
                    'success': False,
                    'error': f'Crop "{crop_name}" not found in database'
                }
            
            self.supabase.table(self.table_name).delete().eq('crop_id', crop_id).execute()
            
            return {
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

