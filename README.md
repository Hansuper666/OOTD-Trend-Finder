# OOTD Trend Finder

A web application for finding outfit-of-the-day images based on text descriptions or image uploads using AI-powered semantic search.

## Setup Instructions

### Prerequisites

- Python 3.11

### Installation

1. Clone the repository or unzip the project files to a local directory:

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root (or edit the existing one):
```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./ootd.db
PINTEREST_API_KEY=not_needed_for_local_images
IMAGE_STORAGE_PATH=./ootd_images
UPLOAD_PATH=./app/static/uploads
```

Note: The OpenAI API key is not required since we're using local CLIP models for image analysis. We easily change to use OpenAI API to process the images, but I don't have a working OpenAI API for vision models. Thus, I use CLIP for this project, which works the same as an API.

### Download OOTD Images

1. Run the image download script:
```bash
python download_fashion_images.py --limit 60 --dir "./ootd_images"
```

This will download approximately 50-60 outfit images to the `ootd_images` directory.

### Process Images

1. Process the downloaded images to extract features and tags:
```bash
python process_local_images.py
```

This step analyzes all images using the CLIP model and stores the results in the database.

2. If you want to update the image tags at any point, run:
```bash
python reprocess_images.py
```

### Run the Application

1. Start the web server:
```bash
python -m uvicorn app.main:app --reload
```

2. Open a web browser and navigate to:
```
http://localhost:8000/
```

## Using the Application

### Text-Based Search

1. Enter a description of the outfit you're looking for in the search box
   - Examples: "casual outfit with jeans", "formal dress", "blue shirt"
   - Try specific clothing items, styles, or colors
   
2. Click the "Search" button to find matching outfits

### Image Search

1. Click the "Choose File" button in the "Or search by image" section
2. Select an image of clothing or an outfit from your computer
3. Click "Find Similar Outfits" to see matching results

### Image Analysis

When you upload an image for search, the system will also analyze it and display:
- Detected clothing items
- Overall style
- Color palette
- Suitable occasions

## Troubleshooting

- If search returns no results, try lowering the similarity threshold in `app/config/settings.py` (e.g., change `SIMILARITY_THRESHOLD` to 0.1)
- If images don't display properly, ensure the `ootd_images` directory contains the downloaded images
- If the application fails to start, check that all dependencies are installed correctly 
