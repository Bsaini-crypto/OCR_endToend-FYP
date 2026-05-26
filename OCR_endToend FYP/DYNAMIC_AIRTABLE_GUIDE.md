# Dynamic Airtable Integration Guide

## How It Works Now

The Airtable integration is now **fully dynamic and resilient**. It uses a **3-strategy approach** to ensure records are **always inserted**:

### Strategy 1: Configured Mapping (If Available)
- Uses fields defined in `airtable_config.py`
- Fastest and most controlled approach
- If this fails, falls back to Strategy 2

### Strategy 2: Auto-Flatten All Fields
- Automatically detects ALL fields in your JSON
- Flattens nested structures (e.g., `Invoice.Number` → `Invoice - Number`)
- Formats arrays as readable text
- If this fails due to invalid fields, removes them and retries
- If still fails, falls back to Strategy 3

### Strategy 3: rawData Only (Always Works)
- Inserts only the `rawData` field with full JSON
- This should ALWAYS work (unless table doesn't exist or auth fails)
- Ensures you never lose data

## Key Features

✅ **Always Inserts Records** - Multiple fallback strategies ensure success
✅ **Dynamic Field Detection** - Automatically finds all fields in your JSON
✅ **Error Recovery** - Removes invalid fields and retries
✅ **No Configuration Required** - Works out of the box, but you can customize
✅ **rawData Always Included** - Full JSON always available

## Setup

### Minimum Setup (Just rawData)

1. **Create Airtable Table** with ONE field:
   - `rawData` (Long text) - **Required!**

2. **That's it!** The system will automatically insert records with full JSON.

### Recommended Setup (With Auto-Flattened Fields)

1. **Create Airtable Table** with:
   - `rawData` (Long text) - **Required!**
   - Any other fields you want (optional - system will auto-detect)

2. **Process a PDF** - The system will:
   - Auto-flatten all fields from JSON
   - Try to insert all fields
   - If some fields don't exist in Airtable, remove them and retry
   - Always succeed with at least `rawData`

### Advanced Setup (With Custom Mapping)

1. **Edit `airtable_config.py`** to define specific fields
2. **Create matching fields** in Airtable
3. System will use your mapping first, then fall back if needed

## How Field Names Are Generated

When auto-flattening, nested structures become:

```
JSON: {"Invoice": {"Number": "123"}}
Airtable Field: "Invoice - Number"
```

Arrays are formatted as:
```
JSON: [{"Product": "A", "Price": "$100"}]
Airtable Field: "Items" = "1. Product: A, Price: $100"
```

## Example Workflow

1. **PDF Processed** → JSON extracted
2. **Strategy 1**: Try configured mapping (if exists)
   - ✅ Success → Done!
   - ❌ Fail → Continue to Strategy 2
3. **Strategy 2**: Auto-flatten all fields
   - ✅ Success → Done!
   - ❌ Fail (invalid fields) → Remove invalid fields, retry
   - ✅ Success → Done!
   - ❌ Still fail → Continue to Strategy 3
4. **Strategy 3**: Insert only rawData
   - ✅ Success → Done! (You still have all data in rawData)

## Field Name Cleaning

The system automatically cleans field names:
- Removes `()`, `%`, `/` characters
- Limits length to 60 characters
- Handles special characters gracefully

## Limits and Safety

- **Array items**: Limited to first 10 items (to prevent huge fields)
- **Field values**: Limited to 100,000 characters (Airtable limit)
- **Nesting depth**: Limited to 5 levels (prevents infinite recursion)
- **Field names**: Limited to 60 characters

## Troubleshooting

### "Even rawData insertion failed"

This means:
- ❌ Table doesn't exist → Create table with `rawData` field
- ❌ Wrong Base ID → Check `AIRTABLE_BASE_ID` in `.env`
- ❌ Wrong Table Name → Check `AIRTABLE_TABLE_NAME` in `.env`
- ❌ Invalid API Key → Check `AIRTABLE_API_KEY` in `.env`
- ❌ `rawData` field doesn't exist → Create it in Airtable!

### "Some fields not inserted"

This is normal! The system:
1. Tries to insert all fields
2. If some fail, removes them and retries
3. Always succeeds with remaining fields + rawData

Check logs to see which fields were removed.

### "Want specific field names"

Edit `airtable_config.py` to define exact field mappings. The system will use those first.

## Best Practices

1. **Always create `rawData` field** - This ensures records are always inserted
2. **Let it auto-flatten first** - See what fields are generated, then customize if needed
3. **Check logs** - They show which strategy succeeded
4. **Start simple** - Just `rawData` field works perfectly!

## Example Logs

```
Attempting Strategy 1: Configured mapping (15 fields)
✅ Record created using configured mapping: recXXXXXXXXXXXXXX
```

Or if that fails:
```
Attempting Strategy 1: Configured mapping (15 fields)
Strategy 1 failed: Unknown field name
Attempting Strategy 2: Auto-flattened all fields (23 fields)
✅ Record created using auto-flattened fields: recXXXXXXXXXXXXXX
```

Or if that also fails:
```
Strategy 2 failed: Invalid fields detected: ['Field1', 'Field2']
Attempting Strategy 2b: Removed invalid fields (21 fields)
✅ Record created after removing invalid fields: recXXXXXXXXXXXXXX
```

Or as last resort:
```
Attempting Strategy 3: Only rawData field
✅ Record created with rawData only: recXXXXXXXXXXXXXX
```

## Summary

**The system is now bulletproof!** It will always insert records, even if:
- Field names don't match
- Some fields don't exist in Airtable
- Configuration is missing
- PDF format changes

Just ensure `rawData` field exists in your Airtable table, and you're good to go! 🚀

