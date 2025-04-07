# OOTD Trend Finder - Instructions

Follow these steps to run the OOTD Trend Finder application with your downloaded images:

## Step 1: Set up your OpenAI API Key

1. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

   You can get an API key from [OpenAI's Platform](https://platform.openai.com/api-keys).

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Process the Downloaded Images

Run the script to process your downloaded OOTD images:

```bash
python process_local_images.py
```

This will:
- Initialize the database
- Process all your images in the ootd_images directory
- Extract features and tags using AI

## Step 4: Run the Application

Start the web application:

```bash
uvicorn app.main:app --reload
```

## Step 5: Use the Application

1. Open your browser and go to: http://localhost:8000/docs

2. Available endpoints:
   - `GET /api/images` - View all processed images
   - `POST /api/search/text` - Search by text description (e.g., "casual outfit with green shirt")
   - `POST /api/search/image` - Upload an image to find similar outfits
   - `POST /api/analyze` - Analyze a specific outfit image

## Example Usage

1. **Text Search**: Use `/api/search/text` with query like "summer outfit with jeans"

2. **Image Search**: Upload a clothing image to `/api/search/image` to find similar outfits

3. **Image Analysis**: Upload an image to `/api/analyze` to get detailed analysis of the outfit

## Troubleshooting

- If you see errors related to the OpenAI API, check your API key in the `.env` file
- If images aren't being processed correctly, try processing them in smaller batches
- If you want to reset the database, delete the `ootd.db` file and run `process_local_images.py` again 