1. Palette Generation
When a concept is created, the system first generates color palettes:
The API call is made to /generate or /generate-with-palettes endpoint
The generate_multiple_palettes method in JigsawStackClient is called
This method:
Sends a prompt to JigsawStack's API with a detailed request for multiple distinct color palettes
Each palette includes a name, description, and 5 hex color codes
The response is parsed to extract the palette information
If the API fails, fallback default palettes are provided
2. Image Generation - Main Concept
For the main concept image:
The generate_image method in JigsawStackClient is called
This sends a request to JigsawStack's image generation API with:
The user-provided prompt
Configuration parameters like aspect ratio and quality settings
The API returns binary image data (not a URL)
This binary data is directly uploaded to Supabase storage
3. Color Palette Variations
For each palette variation, there are two approaches:
When using /generate endpoint:
Original image is already generated
apply_color_palette in SupabaseClient applies colors by:
Downloading the original image from storage
Creating a color overlay using the first color in the palette
Blending it with the original image (30% opacity)
Uploading the modified image to the "palette-images" bucket
When using /generate-with-palettes endpoint:
generate_concept_with_palettes in ConceptService is called
For each palette, it calls generate_image_with_palette from JigsawStackClient which:
Takes the logo prompt and adds specific instructions to use the palette colors
Sends this to the JigsawStack API to generate a completely new image with those colors
Returns binary image data
The binary data is stored in Supabase
Key Methods in client.py
generate_image: Creates a new image from a text prompt
generate_image_with_palette: Creates an image using specific colors
generate_multiple_palettes: Creates multiple color palette schemes
refine_image: Modifies an existing image based on instructions
The system is designed with flexibility, allowing palette variations to be created either by:
Generating all-new images with the specified colors, or
Applying color overlays to an existing image
Your recent changes limit the number of palette variations to 2 (plus the original) and ensure the palette variations have distinct colors by applying a color overlay from the palette.