import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModifierOption(BaseModel):
    name_en: str = Field(description="Size or option name in English (e.g. 'Half', 'Full', '1 pc', 'Single', 'Glass')")
    name_ar: str = Field(description="Size or option name in Arabic (e.g. 'نصف', 'كامل', 'كوب', 'حبة')")
    price: float = Field(description="Price of this specific size/option")

class MenuItem(BaseModel):
    name_en: str = Field(description="English name of the item")
    name_ar: str = Field(description="Arabic name of the item")
    description_en: Optional[str] = Field(None, description="English description of the item")
    description_ar: Optional[str] = Field(None, description="Arabic description of the item")
    price: Optional[float] = Field(None, description="Direct price if the item only has a single price. If it has multiple sizes/prices (modifiers), set this to 0 (zero) and populate the 'options' list instead.")
    options: List[ModifierOption] = Field(default=[], description="List of different sizes or pricing variations if applicable (e.g., half/full, small/medium/large)")
    tags: List[str] = Field(default=[], description="Food tags, e.g. ['non_veg', 'veg', 'beverage', 'dessert']")
    item_type: str = Field(default="non_veg", description="Classification of the item: 'non_veg', 'veg', 'beverage', 'dessert'")

class MenuCategory(BaseModel):
    name_en: str = Field(description="English name of the category (e.g., 'Fresh Karahi/Korma', 'Cold Beverage')")
    name_ar: str = Field(description="Arabic name of the category (e.g., 'كراهي وكورما', 'مشروبات باردة')")
    items: List[MenuItem] = Field(description="List of menu items in this category")

class MenuStructure(BaseModel):
    categories: List[MenuCategory] = Field(description="List of all extracted menu categories and their items")


def extract_menu_from_file(api_key: str, file_content: bytes, mime_type: str, filename: str = "") -> MenuStructure:
    """
    Uploads a menu file (Image, PDF, or Excel/CSV text) to Gemini 2.5 Flash,
    extracts the menu hierarchical structure, translates English/Arabic names,
    and returns a structured Pydantic model.
    """
    logger.info(f"Initiating Gemini OCR/Extraction. File: '{filename}', Mime Type: '{mime_type}'")
    
    # Initialize Google GenAI client
    client = genai.Client(api_key=api_key)
    
    prompt = """
    You are an expert menu digitizer and bilingual translator.
    Your task is to analyze the provided menu document (which may be an image, a PDF, or structured spreadsheet text) and extract all categories, items, prices, and size/quantity options.
    
    Rules:
    1. Extract all names in both English and Arabic.
    2. If a name (category, item, or option) is only present in English, translate it accurately to Arabic.
    3. If a name is only present in Arabic, translate it accurately to English.
    4. If the menu is bilingual, pair the English name with its Arabic equivalent.
    5. Carefully analyze prices and options.
       - If an item has multiple sizes/portions/pricing variations (e.g., 'Half' and 'Full', 'Small'/'Medium'/'Large', 'Glass' and 'Jug', 'Single' and 'Double', or different weights like '250g'/'500g'/'1kg'), list them in the 'options' array with their respective prices. In this case, the item's main 'price' field MUST be set to 0.
       - If an item has only a single price (e.g. it only has one size or a single default price listed), set the 'price' field to that value and leave the 'options' array empty.
       - Do not invent options if there is only one price column.
    6. **Table/Column Grouping Rule (CRITICAL)**:
       - Scan the document for column headers indicating sizes, portions, or variations (e.g., 'Half', 'Full', 'Quarter', '1 Kg', 'Single', 'Double', 'Small', 'Medium', 'Large', 'Pot', 'Plate').
       - If such headers are present, every item in that section MUST be treated as having multiple sizes/options.
       - You MUST group the prices under the same item name in the 'options' list. 
       - For example, 'Chicken Karahi' should NOT be split into two items ('Chicken Karahi Half' and 'Chicken Karahi Full'). It must be ONE item with name 'Chicken Karahi' (Arabic: 'كراهي دجاج'), base price 0, and two options: 'Half' (price: 30) and 'Full' (price: 54).
       - If an item under a multi-price section is missing a price in one of the columns (e.g. 'Chicken Boneless Handi' has a blank under 'Half' and 24 under 'Full'), you should only include the option that has a price ('Full' = 24). If it has only one option with a price, still keep it as an option inside 'options' (e.g., options = [{'name_en': 'Full', 'name_ar': 'كامل', 'price': 24.0}]) with base price 0, so that it keeps the table structure intact!
    7. Classify items into 'item_type': 'veg', 'non_veg', 'beverage', 'dessert', etc. Use 'non_veg' as the default for meat dishes, 'veg' for vegetarian items, 'beverage' for drinks, and 'dessert' for sweets.
    8. Be highly accurate. Capture all items, prices, and categories. Do not omit any menu item found in the document.
    """
    
    # Check if the file is a spreadsheet (Excel or CSV)
    fn_lower = filename.lower()
    is_excel = mime_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ] or fn_lower.endswith(('.xlsx', '.xls'))
    
    is_csv = mime_type in ["text/csv", "application/csv"] or fn_lower.endswith('.csv')
    
    contents = []
    if is_excel:
        import io
        import pandas as pd
        try:
            logger.info("Parsing input Excel file locally...")
            sheets_dict = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
            markdown_parts = []
            for sheet_name, df in sheets_dict.items():
                markdown_parts.append(f"## Sheet: {sheet_name}\n")
                markdown_parts.append(df.to_string(index=False))
            text_content = "\n\n".join(markdown_parts)
            contents = [prompt, f"Here is the text content from the uploaded spreadsheet file:\n\n{text_content}"]
            logger.info("Successfully converted Excel file to text prompt.")
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise ValueError(f"Failed to parse Excel file locally: {e}")
            
    elif is_csv:
        import io
        import pandas as pd
        try:
            logger.info("Parsing input CSV file locally...")
            df = pd.read_csv(io.BytesIO(file_content))
            text_content = df.to_string(index=False)
            contents = [prompt, f"Here is the text content from the uploaded CSV file:\n\n{text_content}"]
            logger.info("Successfully converted CSV file to text prompt.")
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            raise ValueError(f"Failed to parse CSV file locally: {e}")
            
    else:
        # Standard media file (Image, PDF, etc.) processed directly by Gemini Part API
        part = types.Part.from_bytes(
            data=file_content,
            mime_type=mime_type
        )
        contents = [part, prompt]
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MenuStructure,
                temperature=0.1
            )
        )
        
        logger.info("Gemini extraction successful, validating JSON schema...")
        menu_data = MenuStructure.model_validate_json(response.text)
        return menu_data
        
    except Exception as e:
        logger.error(f"Error during Gemini processing/parsing: {e}")
        raise ValueError(f"Failed to process menu file with Gemini: {str(e)}")
