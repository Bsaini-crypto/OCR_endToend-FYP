"""
Airtable field mapping configuration.
Edit this file to configure which fields to extract and map to Airtable.

IMPORTANT: This configuration is OPTIONAL!
- If you define fields here, those will be used first (Strategy 1)
- If this is empty or fields fail, the system will AUTO-FLATTEN all fields (Strategy 2)
- If that fails, it will insert only rawData (Strategy 3)
- The system ALWAYS ensures a record is inserted!

The "rawData" field is ALWAYS included automatically with the full JSON.
"""

# ============================================================================
# AIRTABLE FIELD MAPPING CONFIGURATION (OPTIONAL)
# ============================================================================
# 
# This file defines which fields from the extracted JSON will be mapped to
# Airtable. You can customize this based on your PDF format and Airtable schema.
#
# If you leave this empty ({}), the system will automatically flatten ALL fields
# from your JSON and try to insert them.
#
# Format:
#   "Airtable Field Name": "JSON Path"
#
# JSON Path can be:
#   - Simple key: "Invoice Number"
#   - Nested path: "Invoice.Invoice Number" or "Bill To.Customer Name"
#   - Array item: "Items[0].Product" (first item's Product)
#   - Custom function: Use a lambda function for complex extraction
#
# ============================================================================

# Example configuration for invoice PDFs
AIRTABLE_FIELD_MAPPING = {
    # Invoice Information
    "Invoice Number": "Invoice.Invoice Number",
    "Invoice Date": "Invoice.Date",
    "Due Date": "Invoice.Due Date",
    
    # Customer Information
    "Customer Name": "Bill To.Customer Name",
    "Company": "Bill To.Company",
    "Address": "Bill To.Address",
    "City State ZIP": "Bill To.City, State ZIP",
    "Email": "Bill To.Email",
    
    # Financial Information
    "Subtotal": "Subtotal",
    "Tax": "Tax (8.5%)",
    "Shipping": "Shipping",
    "Total": "TOTAL",
    
    # Payment Information
    "Payment Terms": "Payment Terms",
    "Payment Method": "Payment Method",
    
    # Notes
    "Notes": "Notes",
    
    # Items (formatted as text)
    "Items": "Items",  # Will be formatted as readable text
}

# ============================================================================
# CUSTOM FIELD EXTRACTORS (Optional)
# ============================================================================
# If you need custom logic to extract or format fields, define functions here

def extract_items_as_text(items):
    """Format items array as readable text."""
    if not items or not isinstance(items, list):
        return ""
    
    formatted_items = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            parts = []
            for key, value in item.items():
                parts.append(f"{key}: {value}")
            formatted_items.append(f"{i}. {', '.join(parts)}")
        else:
            formatted_items.append(f"{i}. {item}")
    
    return "\n".join(formatted_items)

# Map field names to custom extractor functions (optional)
CUSTOM_EXTRACTORS = {
    "Items": extract_items_as_text,
}

# ============================================================================
# FIELD TYPE HINTS (Optional - for documentation)
# ============================================================================
# This is just for reference - actual types are set in Airtable
AIRTABLE_FIELD_TYPES = {
    "Invoice Number": "Single line text",
    "Invoice Date": "Date or Single line text",
    "Due Date": "Date or Single line text",
    "Customer Name": "Single line text",
    "Company": "Single line text",
    "Address": "Long text",
    "City State ZIP": "Single line text",
    "Email": "Email",
    "Subtotal": "Single line text or Number",
    "Tax": "Single line text or Number",
    "Shipping": "Single line text or Number",
    "Total": "Single line text or Number",
    "Payment Terms": "Single line text",
    "Payment Method": "Single line text",
    "Notes": "Long text",
    "Items": "Long text",
    "rawData": "Long text",  # Always included
}

