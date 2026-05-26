# Airtable Setup and Data Mapping Guide

## How Data Mapping Works

### Understanding the Mapping Process

When your PDF is processed, the extracted data is structured as JSON. This JSON is then **flattened** and mapped to Airtable fields.

### Example: Nested JSON to Airtable Fields

**Input JSON (from PDF):**
```json
{
  "Invoice": {
    "Invoice Number": "INV-2024-001234",
    "Date": "January 15, 2024"
  },
  "Bill To": {
    "Customer Name": "John Doe",
    "Company": "Acme Corporation"
  },
  "Items": [
    {"Product": "Product A", "Price": "$500.00"},
    {"Product": "Product B", "Price": "$734.56"}
  ]
}
```

**Flattened to Airtable Fields:**
```
Invoice - Invoice Number: "INV-2024-001234"
Invoice - Date: "January 15, 2024"
Bill To - Customer Name: "John Doe"
Bill To - Company: "Acme Corporation"
Items: "1. Product: Product A, Price: $500.00\n2. Product: Product B, Price: $734.56"
```

### Field Name Formatting Rules

1. **Nested Objects**: Flattened with " - " separator
   - `{"Bill To": {"Name": "John"}}` → Field: `Bill To - Name`

2. **Arrays of Objects**: Converted to formatted text
   - Each item numbered and formatted as: `1. Key1: Value1, Key2: Value2`

3. **Simple Arrays**: Joined with semicolons
   - `["Item1", "Item2"]` → `"Item1; Item2"`

4. **Special Characters**: Cleaned
   - `"Tax (8.5%)"` → `"Tax 8.5Percent"` or `"Tax - 8.5Percent"`

## Setting Up Your Airtable Table

### Step 1: Create Your Table

1. Go to your Airtable base
2. Create a new table (or use existing)
3. Name it (default: "Records" - must match `AIRTABLE_TABLE_NAME` in `.env`)

### Step 2: Create Fields Based on Your PDF Structure

**Option A: Match Flattened Field Names (Recommended)**

Create fields that match the flattened structure:

- `Invoice - Invoice Number` (Single line text)
- `Invoice - Date` (Date or Single line text)
- `Bill To - Customer Name` (Single line text)
- `Bill To - Company` (Single line text)
- `Bill To - Address` (Long text)
- `Items` (Long text) - for formatted item lists
- `TOTAL` (Single line text or Number)
- `Payment Terms` (Single line text)

**Option B: Use Simplified Field Names**

If you want cleaner field names, you can:
1. Create fields with simpler names
2. Modify the flattening logic in `airtable_client.py`
3. Or manually map fields

### Step 3: Field Types

Choose appropriate field types:

- **Text fields**: Use "Single line text" or "Long text"
- **Numbers**: Use "Number" field type (remove $ and commas first)
- **Dates**: Use "Date" field type (format: YYYY-MM-DD)
- **Lists**: Use "Long text" for formatted arrays

### Step 4: Test Field Names

The easiest way to see what field names are being sent:

1. Check the logs when processing a PDF
2. Look for: `"Field names: [...]"` in debug logs
3. Or check the error message if insertion fails - it often shows which fields don't exist

## Common Issues and Solutions

### Issue 1: "Field not found" Error

**Problem**: Field names in Airtable don't match the flattened field names.

**Solution**:
1. Check the exact field names being sent (see logs)
2. Create matching fields in Airtable (case-sensitive!)
3. Or modify `_format_data_for_airtable()` in `airtable_client.py` to use different field names

### Issue 2: "Invalid value for field type"

**Problem**: Data type doesn't match Airtable field type.

**Solution**:
- Numbers: Remove currency symbols and commas, convert to number
- Dates: Format as YYYY-MM-DD
- Check Airtable field type matches the data being sent

### Issue 3: Nested Data Not Showing

**Problem**: Nested objects are being flattened but you want them differently.

**Solution**:
- Modify `_format_data_for_airtable()` in `airtable_client.py`
- Or create separate fields for each nested level
- Or use a "Long text" field and store JSON string

### Issue 4: Arrays Not Displaying Well

**Problem**: Arrays are formatted as text but you want them as linked records.

**Solution**:
- Current implementation formats arrays as text
- For linked records, you'd need to:
  1. Create separate records for each array item
  2. Link them to the main record
  3. Modify the code to handle this

## Debugging Airtable Integration

### Enable Debug Logging

In `flask-ocr.py`, you can enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check What's Being Sent

The code logs:
- Number of fields being sent
- Sample field names (first 10)
- Full error messages if insertion fails

### Test with Simple Data

Start with a simple PDF that extracts to flat JSON:
```json
{
  "Name": "John Doe",
  "Amount": "$100.00",
  "Date": "2024-01-15"
}
```

Create matching fields in Airtable:
- `Name` (Single line text)
- `Amount` (Single line text)
- `Date` (Date or Single line text)

## Quick Setup Checklist

- [ ] Airtable base created
- [ ] Table created with matching name (`AIRTABLE_TABLE_NAME`)
- [ ] API key obtained and added to `.env`
- [ ] Base ID obtained and added to `.env`
- [ ] Fields created matching flattened field names
- [ ] Field types match data types
- [ ] Test with sample PDF
- [ ] Check logs for any errors
- [ ] Verify record appears in Airtable

## Example Airtable Table Schema

For the sample invoice PDF, create these fields:

| Field Name | Type | Example Value |
|------------|------|---------------|
| Invoice - Invoice Number | Single line text | INV-2024-001234 |
| Invoice - Date | Single line text | January 15, 2024 |
| Invoice - Due Date | Single line text | February 15, 2024 |
| Bill To - Customer Name | Single line text | John Doe |
| Bill To - Company | Single line text | Acme Corporation |
| Bill To - Address | Long text | 123 Main Street |
| Bill To - City, State ZIP | Single line text | New York, NY 10001 |
| Bill To - Email | Email | john.doe@acme.com |
| Items | Long text | 1. Product: Product A, Price: $500.00... |
| Subtotal | Single line text | $1,484.56 |
| Tax 8.5Percent | Single line text | $126.19 |
| Shipping | Single line text | $50.00 |
| TOTAL | Single line text | $1,660.75 |
| Payment Terms | Single line text | Net 30 |
| Payment Method | Single line text | Bank Transfer |
| Notes | Long text | Thank you for your business!... |

## Need Help?

1. Check the application logs for detailed error messages
2. Verify your `.env` file has correct credentials
3. Test with a simple PDF first
4. Check Airtable API documentation: https://airtable.com/api

