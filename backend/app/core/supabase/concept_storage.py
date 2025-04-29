"""Concept storage operations for Supabase.

This module provides functionality for managing concept data in Supabase.
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, cast

from ...core.config import settings
from ...utils.security.mask import mask_id, mask_path
from .client import SupabaseClient

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases for better type checking
T = TypeVar("T")
APIResponse = Dict[str, Any]  # Supabase API response has a 'data' attribute


class ConceptStorage:
    """Handles concept-related operations in Supabase."""

    def __init__(self, client: SupabaseClient):
        """Initialize with a Supabase client.

        Args:
            client: Configured SupabaseClient instance
        """
        self.client = client
        self.logger = logging.getLogger("supabase_concept")
        self.concepts_table = settings.DB_TABLE_CONCEPTS
        self.palettes_table = settings.DB_TABLE_PALETTES

    def store_concept(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a new concept.

        Args:
            concept_data: Dictionary with concept details including:
                - user_id: UUID of the authenticated user
                - logo_description: User's logo description
                - theme_description: User's theme description
                - image_path: Path to the base image in Supabase Storage
                - image_url: Optional URL to the base image (signed URL)
                - is_anonymous: Whether the user is anonymous (default: True)

        Returns:
            Created concept data or None on error
        """
        try:
            # Ensure we have all required fields
            required_fields = [
                "user_id",
                "logo_description",
                "theme_description",
                "image_path",
            ]
            for field in required_fields:
                if field not in concept_data:
                    self.logger.error(f"Missing required field: {field}")
                    return None

            # Prepare the data for insertion
            insert_data = {
                "user_id": concept_data["user_id"],
                "logo_description": concept_data["logo_description"],
                "theme_description": concept_data["theme_description"],
                "image_path": concept_data["image_path"],
                "is_anonymous": concept_data.get("is_anonymous", True),
            }

            # Add image_url if it exists
            if "image_url" in concept_data and concept_data["image_url"]:
                insert_data["image_url"] = concept_data["image_url"]

            # Explicitly remove any ID field to let the database generate it
            if "id" in insert_data:
                self.logger.warning("Removing ID field from concept data to let database generate it")
                del insert_data["id"]

            # Try using service role key first for highest reliability
            result = self._store_concept_with_service_role(insert_data)
            if result:
                return result

            # Fall back to regular client if service role fails
            self.logger.warning("Service role insert failed, trying regular client")
            response = self.client.client.table(self.concepts_table).insert(insert_data).execute()

            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data:
                self.logger.error("Failed to insert concept")
                return None

            # Extract the first result and return it
            return cast(Dict[str, Any], response.data[0])

        except Exception as e:
            self.logger.error(f"Error storing concept: {e}")
            return None

    def _store_concept_with_service_role(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a concept using the service role key to bypass RLS.

        Args:
            concept_data: Concept data to store

        Returns:
            Created concept data or None on error
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role")
                return None

            # Make a copy of the data to avoid modifying the original
            insert_data = concept_data.copy()

            # Explicitly remove any ID field to let the database generate it
            if "id" in insert_data:
                self.logger.warning("Removing ID field from service role concept data")
                del insert_data["id"]

            # Log the attempt (with masked data)
            masked_user_id = mask_id(insert_data.get("user_id", "unknown"))
            masked_image_path = mask_path(insert_data.get("image_path", ""))
            self.logger.info(f"Attempting to store concept with service role key for user: {masked_user_id}, path: {masked_image_path}")

            # Use the REST API directly with the service role key
            import requests

            api_url = settings.SUPABASE_URL
            table_endpoint = f"{api_url}/rest/v1/{self.concepts_table}"

            response = requests.post(
                table_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json=insert_data,
            )

            if response.status_code == 201:
                self.logger.info(f"Successfully stored concept with service role key: {response.status_code}")
                result_data = response.json()
                if isinstance(result_data, list) and result_data:
                    return cast(Dict[str, Any], result_data[0])
                else:
                    return cast(Dict[str, Any], result_data)
            else:
                self.logger.warning(f"Service role insert failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error storing concept with service role: {e}")
            return None

    def store_color_variations(self, variations: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Store color variations for a concept.

        Args:
            variations: List of color variation dictionaries, each containing:
                - concept_id: UUID of the parent concept
                - palette_name: Name of the color palette
                - colors: JSONB array of hex color codes
                - description: Optional description of the palette
                - image_path: Path to the palette variation image in Storage
                - image_url: Optional URL to the variation image (signed URL)

        Returns:
            Created color variation data or None on error
        """
        try:
            if not variations:
                return []

            # Ensure we have all required fields for each variation
            required_fields = ["concept_id", "palette_name", "colors", "image_path"]

            # Create a clean copy of variations with any ID fields removed
            clean_variations = []
            for variation in variations:
                for field in required_fields:
                    if field not in variation:
                        self.logger.error(f"Missing required field in variation: {field}")
                        return None

                # Create a clean copy without ID field
                clean_variation = variation.copy()
                if "id" in clean_variation:
                    self.logger.warning("Removing ID field from color variation to let database generate it")
                    del clean_variation["id"]

                clean_variations.append(clean_variation)

            # Try using service role key first for highest reliability
            result = self._store_variations_with_service_role(clean_variations)
            if result:
                return result

            # Fall back to regular client if service role fails
            self.logger.warning("Service role insert for variations failed, trying regular client")
            response = self.client.client.table(self.palettes_table).insert(clean_variations).execute()

            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data:
                self.logger.error("Failed to insert color variations")
                return None

            # Cast the result to ensure correct typing
            return cast(List[Dict[str, Any]], response.data)

        except Exception as e:
            self.logger.error(f"Error storing color variations: {e}")
            return None

    def _store_variations_with_service_role(self, variations: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Store color variations using the service role key to bypass RLS.

        Args:
            variations: List of color variation data to store

        Returns:
            Created color variation data or None on error
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role")
                return None

            # Make a clean copy of variations to ensure IDs are removed
            clean_variations = []
            for variation in variations:
                clean_variation = variation.copy()
                if "id" in clean_variation:
                    del clean_variation["id"]
                clean_variations.append(clean_variation)

            # Log the attempt
            self.logger.info(f"Attempting to store {len(clean_variations)} color variations with service role key")

            # Use the REST API directly with the service role key
            import requests

            api_url = settings.SUPABASE_URL
            table_endpoint = f"{api_url}/rest/v1/{self.palettes_table}"

            response = requests.post(
                table_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json=clean_variations,
            )

            if response.status_code == 201:
                self.logger.info(f"Successfully stored {len(clean_variations)} color variations with service role key")
                result_data = response.json()
                return cast(List[Dict[str, Any]], result_data)
            else:
                self.logger.warning(f"Service role insert for variations failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error storing color variations with service role: {e}")
            return None

    def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent concepts for a user.

        Args:
            user_id: UUID of the authenticated user
            limit: Maximum number of concepts to return

        Returns:
            List of concepts WITHOUT their variations (variations should be fetched separately)
        """
        try:
            # First try with service role key for maximum reliability
            concepts = self._get_recent_concepts_with_service_role(user_id, limit)
            if concepts is not None:
                return concepts

            # Fall back to regular client
            self.logger.info(f"Querying recent concepts with user_id: {mask_id(user_id)}")

            # Security: Always filter by user_id to ensure users only see their own data
            # IMPORTANT: Do NOT fetch color_variations here - we will batch fetch them separately
            response = (
                self.client.client.table(self.concepts_table)
                .select("*")  # NOT "*, color_variations(*)" - we'll fetch variations separately
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Check if we have data in the response
            if not hasattr(response, "data"):
                self.logger.warning(f"No data attribute in response for user ID {mask_id(user_id)}")
                return []

            # Cast to ensure proper typing
            data = cast(List[Dict[str, Any]], response.data)

            # Log the results for debugging
            if data:
                self.logger.info(f"Found {len(data)} concepts for user ID {mask_id(user_id)}")
            else:
                self.logger.warning(f"No concepts found for user ID {mask_id(user_id)}")

            # Initialize empty color_variations array for each concept
            for concept in data:
                concept["color_variations"] = []

            return data
        except Exception as e:
            self.logger.error(f"Error retrieving recent concepts: {e}")
            return []

    def _get_recent_concepts_with_service_role(self, user_id: str, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Get recent concepts for a user using the service role key to bypass RLS.

        Args:
            user_id: UUID of the authenticated user
            limit: Maximum number of concepts to return

        Returns:
            List of concepts WITHOUT their variations or None on error
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role for query")
                return None

            # Log the attempt
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Attempting to get recent concepts with service role key for user: {masked_user_id}")

            # Use the REST API directly with the service role key
            import requests

            api_url = settings.SUPABASE_URL

            # Get the concepts WITHOUT their variations
            concepts_endpoint = f"{api_url}/rest/v1/{self.concepts_table}" f"?select=*" f"&user_id=eq.{user_id}" f"&order=created_at.desc" f"&limit={limit}"

            response = requests.get(
                concepts_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                concepts_data = response.json()
                # Cast to ensure proper typing
                concepts = cast(List[Dict[str, Any]], concepts_data)

                # Initialize empty color_variations array for each concept
                for concept in concepts:
                    concept["color_variations"] = []

                self.logger.info(f"Successfully retrieved {len(concepts)} concepts with service role key")
                return concepts
            else:
                self.logger.warning(f"Service role query failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving concepts with service role: {e}")
            return None

    def get_concept_detail(self, concept_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific concept.

        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for security validation

        Returns:
            Concept detail data or None if not found
        """
        try:
            # First try with service role key for maximum reliability
            concept_detail = self._get_concept_detail_with_service_role(concept_id, user_id)
            if concept_detail is not None:
                return concept_detail

            # Fall back to regular client
            # Query the concept with security check for user_id
            response = self.client.client.table(self.concepts_table).select(f"*, {self.palettes_table}(*)").eq("id", concept_id).eq("user_id", user_id).execute()

            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data:
                return None

            # Cast to ensure proper typing and extract the first item
            return cast(Dict[str, Any], response.data[0])
        except Exception as e:
            self.logger.error(f"Error retrieving concept details: {e}")
            return None

    def _get_concept_detail_with_service_role(self, concept_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific concept using the service role key.

        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for security validation

        Returns:
            Concept detail data or None if not found or on error
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role for query")
                return None

            # Log the attempt
            masked_concept_id = mask_id(concept_id)
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Attempting to get concept detail with service role key for concept: {masked_concept_id}, user: {masked_user_id}")

            # Use the REST API directly with the service role key
            import requests

            api_url = settings.SUPABASE_URL

            # Get the concept with user_id verification (for security)
            concept_endpoint = f"{api_url}/rest/v1/{self.concepts_table}" f"?id=eq.{concept_id}" f"&user_id=eq.{user_id}"

            response = requests.get(
                concept_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                concepts = response.json()

                # If we found the concept and it belongs to the user, get its color variations
                if concepts:
                    concept = concepts[0]

                    # Get color variations for this concept
                    variations_endpoint = f"{api_url}/rest/v1/{self.palettes_table}" f"?select=*" f"&concept_id=eq.{concept_id}"

                    variations_response = requests.get(
                        variations_endpoint,
                        headers={
                            "apikey": service_role_key,
                            "Authorization": f"Bearer {service_role_key}",
                            "Content-Type": "application/json",
                        },
                    )

                    if variations_response.status_code == 200:
                        concept["color_variations"] = cast(List[Dict[str, Any]], variations_response.json())
                    else:
                        self.logger.warning(f"Failed to get color variations: {variations_response.status_code}")
                        concept["color_variations"] = []

                    self.logger.info(f"Successfully retrieved concept detail with service role key for concept: {masked_concept_id}")
                    return cast(Dict[str, Any], concept)
                else:
                    self.logger.warning(f"No concept found with ID {masked_concept_id} for user {masked_user_id}")
                    return None
            else:
                self.logger.warning(f"Service role query failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving concept detail with service role: {e}")
            return None

    def delete_all_color_variations(self, user_id: str) -> bool:
        """Delete all color variations for a user.

        Args:
            user_id: UUID of the authenticated user

        Returns:
            True if successful, False otherwise
        """
        try:
            # First get all concept IDs for this user
            concepts_result = self.client.client.table(self.concepts_table).select("id").eq("user_id", user_id).execute()

            if not concepts_result.data:
                self.logger.info(f"No concepts found for user ID {mask_id(user_id)}")
                return True

            # Extract concept IDs
            concept_ids = [concept.get("id") for concept in concepts_result.data]

            # Delete all color variations for these concepts
            for concept_id in concept_ids:
                self.client.client.table(self.palettes_table).delete().eq("concept_id", concept_id).execute()

            return True
        except Exception as e:
            self.logger.error(f"Error deleting color variations: {e}")
            return False

    def delete_all_concepts(self, user_id: str) -> bool:
        """Delete all concepts for a user.

        Args:
            user_id: UUID of the authenticated user

        Returns:
            True if successful, False otherwise
        """
        try:
            # Due to foreign key constraints, this will also delete color variations
            self.client.client.table(self.concepts_table).delete().eq("user_id", user_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting concepts: {e}")
            return False

    def get_concept_by_task_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a concept by its task ID.

        Args:
            task_id: Task ID of the concept to retrieve
            user_id: UUID of the authenticated user (for security/RLS)

        Returns:
            Concept data or None if not found
        """
        try:
            # Try using service role key first for highest reliability
            result = self._get_concept_by_task_id_with_service_role(task_id, user_id)
            if result:
                return result

            # Fall back to regular client if service role fails
            self.logger.warning("Service role query for task failed, trying regular client")

            # Get the concept
            query = self.client.client.table(self.concepts_table).select("*").eq("task_id", task_id).eq("user_id", user_id).limit(1)

            response = query.execute()

            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data or len(response.data) == 0:
                masked_task_id = mask_id(task_id)
                self.logger.info(f"No concept found for task ID: {masked_task_id}")
                return None

            # Cast to ensure proper typing
            concept = cast(Dict[str, Any], response.data[0])

            masked_concept_id = mask_id(concept.get("id", ""))
            self.logger.info(f"Retrieved concept {masked_concept_id} for task ID: {mask_id(task_id)}")

            return concept

        except Exception as e:
            self.logger.error(f"Error getting concept by task ID: {e}")
            return None

    def _get_concept_by_task_id_with_service_role(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a concept by its task ID using the service role key to bypass RLS.

        Args:
            task_id: Task ID of the concept to retrieve
            user_id: UUID of the authenticated user (for security/RLS)

        Returns:
            Concept data or None if not found
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role")
                return None

            # Log the attempt
            masked_task_id = mask_id(task_id)
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Attempting to get concept with service role key for task ID: {masked_task_id}, user: {masked_user_id}")

            # Use the REST API directly with the service role key
            import requests

            api_url = settings.SUPABASE_URL
            query_params = f"task_id=eq.{task_id}&user_id=eq.{user_id}&limit=1"
            table_endpoint = f"{api_url}/rest/v1/{self.concepts_table}?{query_params}"

            response = requests.get(
                table_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0:
                    self.logger.info(f"Successfully retrieved concept with service role key for task ID: {masked_task_id}")
                    return cast(Dict[str, Any], result[0])
                else:
                    self.logger.info(f"No concept found for task ID: {masked_task_id}")
                    return None
            else:
                self.logger.warning(f"Service role query failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error getting concept by task ID with service role: {e}")
            return None

    def get_variations_by_concept_ids(self, concept_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Batch fetch color variations for multiple concepts at once.

        Args:
            concept_ids: List of concept IDs to fetch variations for

        Returns:
            Dictionary mapping concept_id to a list of its variations
        """
        if not concept_ids:
            return {}

        try:
            # Try with service role first for reliability
            result = self._get_variations_by_concept_ids_with_service_role(concept_ids)
            if result is not None:
                return result

            # Fall back to regular client if service role fails
            self.logger.warning("Service role fetch failed, trying regular client")

            from supabase.postgrest.base_request_builder import BaseFilterRequestBuilder

            # We need to create an "in" filter for the concept_ids
            # Using .or_ to build a query like "concept_id.eq(id1),concept_id.eq(id2),..."
            builder: BaseFilterRequestBuilder = self.client.client.table(self.palettes_table).select("*")
            for i, concept_id in enumerate(concept_ids):
                if i == 0:
                    builder = builder.eq("concept_id", concept_id)
                else:
                    builder = builder.or_(f"concept_id.eq.{concept_id}")

            response = builder.execute()

            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data:
                # No variations found for these concepts
                return {}

            # Cast the data to ensure proper typing
            data = cast(List[Dict[str, Any]], response.data)

            # Group variations by concept_id
            variations_by_concept: Dict[str, List[Dict[str, Any]]] = {}
            for variation in data:
                # Safely handle the concept_id to ensure it's a string
                raw_concept_id = variation.get("concept_id")
                if raw_concept_id is None:
                    continue

                # Ensure concept_id is treated as a string
                concept_id = str(raw_concept_id)

                # Initialize list for this concept if it doesn't exist yet
                if concept_id not in variations_by_concept:
                    variations_by_concept[concept_id] = []

                # Add the variation to the appropriate concept
                variations_by_concept[concept_id].append(variation)

            return variations_by_concept

        except Exception as e:
            self.logger.error(f"Error fetching variations by concept IDs: {e}")
            return {}

    def _get_variations_by_concept_ids_with_service_role(self, concept_ids: List[str]) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """Batch fetch color variations for multiple concepts using service role key.

        Args:
            concept_ids: List of concept IDs to fetch variations for

        Returns:
            Dictionary mapping concept_id to a list of its variations, or None on error
        """
        try:
            # Get the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.warning("No service role key available, cannot use service role")
                return None

            # Build the query - this will be a series of requests, one for each concept ID
            # This is more efficient than multiple individual requests due to connection reuse
            import requests

            api_url = settings.SUPABASE_URL

            # We'll collect all variations in one go to minimize round trips
            concept_filter = f"concept_id=in.({','.join(concept_ids)})"
            table_endpoint = f"{api_url}/rest/v1/{self.palettes_table}?select=*&{concept_filter}"

            response = requests.get(
                table_endpoint,
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                },
            )

            if response.status_code == 200:
                self.logger.info(f"Successfully fetched variations with service role key: {response.status_code}")
                variations_data = response.json()
                # Cast to ensure proper typing
                variations = cast(List[Dict[str, Any]], variations_data)

                # Group variations by concept_id
                variations_by_concept: Dict[str, List[Dict[str, Any]]] = {}
                for variation in variations:
                    # Safely handle the concept_id to ensure it's a string
                    raw_concept_id = variation.get("concept_id")
                    if raw_concept_id is None:
                        continue

                    # Ensure concept_id is treated as a string
                    concept_id = str(raw_concept_id)

                    # Initialize list for this concept if it doesn't exist yet
                    if concept_id not in variations_by_concept:
                        variations_by_concept[concept_id] = []

                    # Add the variation to the appropriate concept
                    variations_by_concept[concept_id].append(variation)

                return variations_by_concept
            else:
                self.logger.warning(f"Service role fetch failed: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error fetching variations with service role: {e}")
            return None
