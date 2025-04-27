Okay, I understand the problem. You want the signed URLs for concept images to expire only _after_ the scheduled cleanup job (which runs daily at midnight UTC and removes concepts older than 3 days) has had a chance to remove the corresponding concept data.

Here's a breakdown of the issue and the solution:

**Problem:**

1.  **Concept Data Lifespan:** Concepts are kept for 3 days.
2.  **Cleanup Schedule:** A job runs daily at 00:00 UTC to delete concepts older than 3 days.
3.  **Signed URL Lifespan:** Currently generated with a fixed duration (e.g., 3 days = 259200 seconds).
4.  **Mismatch:** A concept created just after midnight UTC might have its 3-day lifespan end _before_ the next midnight UTC cleanup. Its signed URL (with a fixed 3-day expiry) could expire hours before the cleanup job removes the concept record, leading to broken images in the UI for concepts that _should_ still be visible.

**Goal:**

Calculate the signed URL expiry (`expires_in` seconds) such that it lasts until the _next_ midnight UTC _after_ the concept's 3-day age is reached, plus a small buffer.

**Solution Steps:**

1.  **Identify `created_at`:** When generating a signed URL for a concept image or variation, you need the `created_at` timestamp of the _parent concept_.
2.  **Calculate Eligibility Time:** Determine when the concept becomes eligible for deletion: `eligible_deletion_time = concept.created_at + timedelta(days=3)`.
3.  **Find Next Cleanup Time:** Find the timestamp of the _next_ 00:00 UTC _after_ `eligible_deletion_time`.
4.  **Add Buffer:** Add a small safety buffer (e.g., 15-30 minutes) to the next cleanup time to ensure the URL is valid slightly past midnight: `target_expiry_time = next_cleanup_time + timedelta(minutes=15)`.
5.  **Calculate `expires_in`:** Calculate the duration in seconds between `now` (the time the URL is generated) and `target_expiry_time`. This is the value to pass to `create_signed_url`.

**Implementation Changes:**

1.  **Helper Function for Expiry Calculation:** Create a utility function to calculate the required `expires_in` duration.

    ```python
    # backend/app/utils/datetime_utils.py (or similar location)
    from datetime import datetime, timedelta, timezone

    def calculate_url_expiry_seconds(created_at_ts: datetime) -> int:
        """
        Calculates the expiry duration in seconds for a signed URL,
        ensuring it lasts until the next cleanup cycle after 3 days.
        """
        now = datetime.now(timezone.utc)

        # Ensure created_at is timezone-aware (UTC)
        if created_at_ts.tzinfo is None:
            # Assume UTC if naive, or convert if it has another timezone
            created_at_utc = created_at_ts.replace(tzinfo=timezone.utc)
        else:
            created_at_utc = created_at_ts.astimezone(timezone.utc)

        # Concept becomes eligible for deletion after 3 days
        eligible_deletion_time = created_at_utc + timedelta(days=3)

        # Find the date part of the *next* day after eligibility
        next_day_date = (eligible_deletion_time.date() + timedelta(days=1))

        # Construct the datetime for the next midnight UTC
        next_cleanup_time = datetime(
            next_day_date.year,
            next_day_date.month,
            next_day_date.day,
            0, 0, 0, tzinfo=timezone.utc
        )

        # Add a small buffer (e.g., 15 minutes) to ensure URL is valid slightly past cleanup time
        target_expiry_time = next_cleanup_time + timedelta(minutes=15)

        # Calculate duration from now until the target expiry time
        duration = target_expiry_time - now

        # Calculate expiry in seconds, ensuring a minimum duration (e.g., 1 minute)
        expires_in_seconds = max(60, int(duration.total_seconds()))

        # Log the calculation for debugging
        # logger.debug(f"Calculated expiry: Now={now}, Created={created_at_utc}, Eligible={eligible_deletion_time}, NextCleanup={next_cleanup_time}, TargetExpiry={target_expiry_time}, ExpiresIn={expires_in_seconds}s")

        return expires_in_seconds
    ```

2.  **Modify Data Retrieval to Generate URLs:** The best place to generate these correctly expiring URLs is when the concept data (which includes `created_at`) is fetched. Update the `ConceptStorage` methods (`get_recent_concepts` and `get_concept_detail`, and their service role counterparts) to calculate and generate the URLs.

    ```python
    # backend/app/core/supabase/concept_storage.py
    import logging
    from datetime import datetime
    from typing import Any, Dict, List, Optional, cast
    # ... other imports ...
    from app.utils.datetime_utils import calculate_url_expiry_seconds # Import the new helper
    # ... other imports ...

    logger = logging.getLogger(__name__)

    class ConceptStorage:
        # ... (init method remains the same) ...

        def _generate_signed_urls_for_concept(self, concept: Dict[str, Any]) -> None:
            """Helper to generate signed URLs for a concept and its variations."""
            try:
                created_at_str = concept.get("created_at")
                if not created_at_str:
                    self.logger.warning(f"Concept {concept.get('id')} missing created_at timestamp.")
                    return # Cannot calculate expiry without created_at

                # Parse created_at string (assuming ISO format with timezone)
                # Handle potential parsing errors
                try:
                    # Attempt parsing with timezone info first
                    created_at_dt = datetime.fromisoformat(created_at_str)
                except ValueError:
                     # Fallback for formats without timezone (assume UTC)
                    try:
                       created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                       if created_at_dt.tzinfo is None:
                           created_at_dt = created_at_dt.replace(tzinfo=timezone.utc)
                    except ValueError:
                        self.logger.error(f"Could not parse created_at: {created_at_str}")
                        return

                expires_in = calculate_url_expiry_seconds(created_at_dt)

                # Generate URL for the main concept image
                image_path = concept.get("image_path")
                if image_path:
                    try:
                         # Use the ImageStorage helper for consistency
                        concept["image_url"] = self.client.storage.get_signed_url(
                            path=image_path,
                            bucket=self.client.storage.concept_bucket, # Assuming ImageStorage has bucket names
                            expiry_seconds=expires_in
                        )
                    except Exception as url_err:
                         self.logger.error(f"Failed to generate signed URL for concept {concept.get('id')} path {image_path}: {url_err}")
                         concept["image_url"] = None # Set to None if URL generation fails


                # Generate URLs for color variations
                variations = concept.get("color_variations", [])
                if variations:
                    for variation in variations:
                        variation_path = variation.get("image_path")
                        if variation_path:
                             try:
                                 variation["image_url"] = self.client.storage.get_signed_url(
                                     path=variation_path,
                                     bucket=self.client.storage.palette_bucket, # Assuming ImageStorage has bucket names
                                     expiry_seconds=expires_in
                                 )
                             except Exception as var_url_err:
                                 self.logger.error(f"Failed to generate signed URL for variation {variation.get('id')} path {variation_path}: {var_url_err}")
                                 variation["image_url"] = None # Set to None if URL generation fails


            except Exception as e:
                self.logger.error(f"Error generating signed URLs for concept {concept.get('id')}: {e}")


        def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
            try:
                # --- Existing logic to fetch concepts ---
                concepts = self._get_recent_concepts_with_service_role(user_id, limit) # Or the regular client fetch
                if concepts is None: concepts = [] # Ensure it's a list

                if concepts:
                    concept_ids = [concept["id"] for concept in concepts]
                    variations_by_concept = self.get_variations_by_concept_ids(concept_ids)

                    # Attach variations and GENERATE SIGNED URLS
                    for concept in concepts:
                        concept_id = concept["id"]
                        concept["color_variations"] = variations_by_concept.get(concept_id, [])
                        self._generate_signed_urls_for_concept(concept) # Generate URLs here

                return concepts
            except Exception as e:
                self.logger.error(f"Error retrieving recent concepts: {e}")
                return []

        # Apply similar logic to _get_recent_concepts_with_service_role
        def _get_recent_concepts_with_service_role(self, user_id: str, limit: int) -> Optional[List[Dict[str, Any]]]:
            # ... (fetching logic) ...
            if response.status_code == 200:
                concepts = cast(List[Dict[str, Any]], response.json())
                # --- Existing logic to attach variations (if needed here) ---
                if concepts:
                     # Generate URLs AFTER fetching variations if necessary
                     concept_ids = [c['id'] for c in concepts]
                     variations_map = self._get_variations_by_concept_ids_with_service_role(concept_ids) or {}
                     for concept in concepts:
                          concept['color_variations'] = variations_map.get(concept['id'], [])
                          self._generate_signed_urls_for_concept(concept) # Generate URLs
                return concepts
            # ... (rest of the method) ...


        def get_concept_detail(self, concept_id: str, user_id: str) -> Optional[Dict[str, Any]]:
            try:
                # --- Existing logic to fetch concept detail ---
                concept_detail = self._get_concept_detail_with_service_role(concept_id, user_id) # Or regular client fetch
                if not concept_detail:
                     return None

                # GENERATE SIGNED URLS before returning
                self._generate_signed_urls_for_concept(concept_detail)

                return concept_detail
            except Exception as e:
                self.logger.error(f"Error retrieving concept details: {e}")
                return None

        # Apply similar logic to _get_concept_detail_with_service_role
        def _get_concept_detail_with_service_role(self, concept_id: str, user_id: str) -> Optional[Dict[str, Any]]:
             # ... (fetching logic) ...
            if response.status_code == 200:
                concepts = response.json()
                if concepts:
                    concept = concepts[0]
                    # Fetch variations...
                    # ... variations fetched into concept['color_variations'] ...
                    self._generate_signed_urls_for_concept(concept) # Generate URLs
                    return cast(Dict[str, Any], concept)
                # ... (rest of the method) ...


        # Ensure get_variations_by_concept_ids and its service role counterpart
        # DO NOT generate signed URLs themselves, as expiry depends on the parent concept's created_at
        def get_variations_by_concept_ids(self, concept_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
             # ... (fetch variations) ...
             # NO URL GENERATION HERE
             return variations_by_concept
    ```
