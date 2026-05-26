# Airtable Configuration Guide

## Overview

The Airtable integration now uses a **configurable field mapping system**. You can easily customize which fields are extracted and sent to Airtable by editing `airtable_config.py`.

## Key Features

1. **Configurable Field Mapping**: Define which fields to extract in `airtable_config.py`
2. **Always Includes rawData**: A `rawData` field is automatically added with the full JSON
3. **Flexible JSON Paths**: Support for nested paths like `"Invoice.Invoice Number"`
4. **Custom Extractors**: Define custom functions to format complex data

## Quick Start

### Step 1: Edit `airtable_config.py`

Open `airtable_config.py` and configure the `AIRTABLE_FIELD_MAPPING` dictionary:

```python
AIRTABLE_FIELD_MAPPING = {
    # Airtable Field Name: JSON Path
    "Invoice Number": "Invoice.Invoice Number",
    "Customer Name": "Bill To.Customer Name",
    "Total": "TOTAL",
    # ... add more fields
}
```

### Step 2: Create Matching Fields in Airtable

Create fields in your Airtable table that match the keys in `AIRTABLE_FIELD_MAPPING`:

- `Invoice Number` (Single line text)
- `Customer Name` (Single line text)
- `Total` (Single line text or Number)
- `rawData` (Long text) - **Always required!**

### Step 3: Test

Run your API and process a PDF. The system will:
1. Extract data from PDF
2. Map only the configured fields
3. Add `rawData` with full JSON
4. Insert into Airtable

## JSON Path Syntax

### Simple Keys
```python
"Invoice Number": "Invoice Number"  # Direct key
```

### Nested Objects
```python
"Customer Name": "Bill To.Customer Name"  # Nested path
"Invoice Date": "Invoice.Date"  # Another nested path
```

### Array Items
```python
"First Item": "Items[0].Product"  # First item's Product field
```

### Arrays (Full Array)
```python
"Items": "Items"  # Will use custom extractor if defined
```

## Example Configuration

For the sample invoice PDF, here's a complete configuration:

```python
AIRTABLE_FIELD_MAPPING = {
    # Invoice Information
    "Invoice Number": "Invoice.Invoice Number",
    "Invoice Date": "Invoice.Date",
    "Due Date": "Invoice.Due Date",
    
    # Customer Information
    "Customer Name": "Bill To.Customer Name",
    "Company": "Bill To.Company",
    "Address": "Bill To.Address",
    "Email": "Bill To.Email",
    
    # Financial
    "Subtotal": "Subtotal",
    "Tax": "Tax (8.5%)",
    "Total": "TOTAL",
    
    # Payment
    "Payment Terms": "Payment Terms",
    
    # Items (will be formatted by custom extractor)
    "Items": "Items",
}
```

## Custom Extractors

For complex data formatting, define custom extractor functions:

```python
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

# Map to field name
CUSTOM_EXTRACTORS = {
    "Items": extract_items_as_text,
}
```

## The rawData Field

**The `rawData` field is ALWAYS included automatically.** It contains the full JSON extracted from the PDF, formatted as a readable string.

This ensures you always have access to all data, even if you don't map all fields.

## Changing PDF Formats

When your PDF format changes:

1. **Update the field mapping** in `airtable_config.py`
2. **Update Airtable fields** to match new field names
3. **Keep `rawData` field** - it's always there with everything

## Troubleshooting

### Field Not Found

If a field path doesn't exist in the JSON:
- The field will be skipped (not cause an error)
- Check logs for: `"Field 'X' (path: Y) not found in data"`

### Field Name Mismatch

If Airtable says "unknown field":
- Check field names match exactly (case-sensitive)
- Ensure field exists in your Airtable table
- Check logs for the exact field names being sent

### Empty Fields

If fields are empty:
- Verify JSON path is correct
- Check if data exists at that path in your JSON
- Use `rawData` to see the full structure

## Best Practices

1. **Start Simple**: Map a few key fields first, test, then add more
2. **Use rawData**: Always check `rawData` to see the full extracted data
3. **Test Incrementally**: Add fields one at a time and test
4. **Document Changes**: Comment your field mappings for future reference

## Example: Adapting to New PDF Format

**Old PDF Structure:**
```json
{
  "Invoice": {"Number": "123"},
  "Customer": {"Name": "John"}
}
```

**New PDF Structure:**
```json
{
  "Document": {"InvoiceID": "123"},
  "Client": {"FullName": "John"}
}
```

**Update Configuration:**
```python
# Old mapping
"Invoice Number": "Invoice.Number",
"Customer Name": "Customer.Name",

# New mapping
"Invoice Number": "Document.InvoiceID",
"Customer Name": "Client.FullName",
```

The `rawData` field will always contain the full JSON, so you can reference it to see the structure.

