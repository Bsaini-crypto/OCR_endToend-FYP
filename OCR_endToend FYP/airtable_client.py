"""
Airtable CRM integration module.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from pyairtable import Api
from pyairtable.formulas import match

# Import field mapping configuration
try:
    from airtable_config import AIRTABLE_FIELD_MAPPING, CUSTOM_EXTRACTORS
except ImportError:
    # Default empty mapping if config doesn't exist
    AIRTABLE_FIELD_MAPPING = {}
    CUSTOM_EXTRACTORS = {}

logger = logging.getLogger(__name__)

class AirtableClient:
    """Handles Airtable CRM operations."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None, 
                 table_name: Optional[str] = None):
        """
        Initialize Airtable client.
        
        Args:
            api_key: Airtable API key (from environment if not provided)
            base_id: Airtable Base ID (from environment if not provided)
            table_name: Airtable Table name (from environment if not provided)
        """
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID")
        self.table_name = table_name or os.getenv("AIRTABLE_TABLE_NAME", "Records")
        
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY environment variable is required")
        if not self.base_id:
            raise ValueError("AIRTABLE_BASE_ID environment variable is required")
        
        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)
        logger.info(f"Airtable client initialized for table: {self.table_name}")
    
    def create_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in Airtable dynamically.
        Automatically flattens all fields and handles errors gracefully.
        Always ensures record is inserted (at minimum with rawData).
        
        Args:
            data: Dictionary containing the extracted JSON data
            
        Returns:
            Created record from Airtable
        """
        # Strategy 1: Try with configured mapping + rawData
        # Strategy 2: Try with auto-flattened all fields + rawData
        # Strategy 3: Try with only rawData (always works)
        
        raw_data_json = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Strategy 1: Use configured mapping if available
        if AIRTABLE_FIELD_MAPPING:
            try:
                record_data = self._format_data_for_airtable(data)
                record_data["rawData"] = raw_data_json
                logger.info(f"Attempting Strategy 1: Configured mapping ({len(record_data)} fields)")
                record = self.table.create(record_data)
                logger.info(f"✅ Record created using configured mapping: {record.get('id')}")
                return record
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {str(e)}")
                # Continue to Strategy 2
        
        # Strategy 2: Auto-flatten all fields dynamically
        try:
            record_data = self._auto_flatten_data(data)
            record_data["rawData"] = raw_data_json
            logger.info(f"Attempting Strategy 2: Auto-flattened all fields ({len(record_data)} fields)")
            record = self.table.create(record_data)
            logger.info(f"✅ Record created using auto-flattened fields: {record.get('id')}")
            return record
        except Exception as e:
            error_details = self._extract_error_details(e)
            invalid_fields = self._extract_invalid_fields(error_details)
            
            if invalid_fields:
                logger.warning(f"Strategy 2 failed: Invalid fields detected: {invalid_fields}")
                # Strategy 2b: Remove invalid fields and try again
                try:
                    cleaned_data = {k: v for k, v in record_data.items() if k not in invalid_fields}
                    cleaned_data["rawData"] = raw_data_json
                    logger.info(f"Attempting Strategy 2b: Removed invalid fields ({len(cleaned_data)} fields)")
                    record = self.table.create(cleaned_data)
                    logger.info(f"✅ Record created after removing invalid fields: {record.get('id')}")
                    return record
                except Exception as e2:
                    logger.warning(f"Strategy 2b failed: {str(e2)}")
                    # Continue to Strategy 3
        
        # Strategy 3: Only rawData (this should always work)
        try:
            record_data = {"rawData": raw_data_json}
            logger.info("Attempting Strategy 3: Only rawData field")
            record = self.table.create(record_data)
            logger.info(f"✅ Record created with rawData only: {record.get('id')}")
            return record
        except Exception as e:
            # This is a critical error - rawData should always work
            error_msg = str(e)
            error_details = self._extract_error_details(e)
            logger.error(f"❌ CRITICAL: Even rawData insertion failed: {error_msg}")
            logger.error(f"Error details: {error_details}")
            
            # Check for authentication/table issues
            if error_details:
                if isinstance(error_details, dict):
                    error_type = error_details.get('error', {}).get('type', '')
                    if 'UNAUTHORIZED' in error_type or 'NOT_FOUND' in error_type:
                        logger.error("❌ Authentication or table configuration issue!")
                        logger.error("   Check: AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME")
                        logger.error("   Also ensure 'rawData' field exists in your Airtable table!")
            
            raise Exception(f"Failed to insert record even with rawData only. Check Airtable configuration. Error: {error_msg}")
    
    def _extract_error_details(self, error: Exception) -> Optional[Dict[str, Any]]:
        """Extract error details from exception."""
        if hasattr(error, 'response'):
            try:
                if hasattr(error.response, 'json'):
                    return error.response.json()
                elif hasattr(error.response, 'text'):
                    try:
                        return json.loads(error.response.text)
                    except:
                        return {"text": error.response.text}
            except:
                pass
        return None
    
    def _extract_invalid_fields(self, error_details: Optional[Dict[str, Any]]) -> List[str]:
        """Extract list of invalid field names from error."""
        invalid_fields = []
        if error_details and isinstance(error_details, dict):
            error = error_details.get('error', {})
            error_type = error.get('type', '')
            error_message = error.get('message', '')
            
            if 'UNKNOWN_FIELD_NAME' in error_type or 'unknown field' in error_message.lower():
                # Try to extract field name from message
                # Airtable error format: "Could not parse: Unknown field name: 'FieldName'"
                import re
                matches = re.findall(r"['\"]([^'\"]+)['\"]", error_message)
                invalid_fields.extend(matches)
        
        return invalid_fields
    
    def _format_data_for_airtable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for Airtable insertion using configured field mapping.
        Only extracts fields defined in AIRTABLE_FIELD_MAPPING.
        
        Args:
            data: Raw data dictionary from PDF extraction
            
        Returns:
            Formatted data for Airtable with only configured fields
        """
        formatted = {}
        
        # If no mapping configured, return empty (will use auto-flatten instead)
        if not AIRTABLE_FIELD_MAPPING:
            return formatted
        
        # Extract each configured field
        for airtable_field, json_path in AIRTABLE_FIELD_MAPPING.items():
            try:
                value = self._extract_value_by_path(data, json_path)
                
                # Apply custom extractor if defined
                if airtable_field in CUSTOM_EXTRACTORS:
                    extractor = CUSTOM_EXTRACTORS[airtable_field]
                    value = extractor(value)
                
                # Convert to string and clean
                if value is not None:
                    formatted[airtable_field] = str(value).strip()
                else:
                    # Field not found in data - skip
                    logger.debug(f"Field '{airtable_field}' (path: {json_path}) not found in data")
                    
            except Exception as e:
                logger.warning(f"Error extracting field '{airtable_field}' from path '{json_path}': {e}")
                # Continue with other fields
        
        logger.info(f"Mapped {len(formatted)} fields from configuration")
        return formatted
    
    def _auto_flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically flatten all fields from JSON data for Airtable.
        This is the dynamic fallback when no mapping is configured.
        
        Args:
            data: Raw data dictionary from PDF extraction
            
        Returns:
            Flattened data with all fields
        """
        formatted = {}
        
        def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = " - ", max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
            """Recursively flatten nested dictionary."""
            if current_depth >= max_depth:
                # Prevent infinite recursion, convert to JSON string
                return {parent_key: json.dumps(d, ensure_ascii=False)} if parent_key else {}
            
            result = {}
            for k, v in d.items():
                # Clean field name (remove special characters that might cause issues)
                clean_key = str(k).replace("(", "").replace(")", "").replace("%", "Percent").replace("/", "-").strip()
                
                # Create full key
                if parent_key:
                    new_key = f"{parent_key}{sep}{clean_key}"
                else:
                    new_key = clean_key
                
                # Limit key length (Airtable has field name length limits)
                if len(new_key) > 60:
                    new_key = new_key[:57] + "..."
                
                if isinstance(v, dict):
                    # Recursively flatten nested dict
                    nested = flatten_dict(v, new_key, sep, max_depth, current_depth + 1)
                    result.update(nested)
                elif isinstance(v, list):
                    # Handle arrays
                    if v and isinstance(v[0], dict):
                        # Array of objects - format as readable text
                        formatted_items = []
                        for i, item in enumerate(v[:10], 1):  # Limit to 10 items
                            if isinstance(item, dict):
                                item_parts = []
                                for item_key, item_value in item.items():
                                    item_parts.append(f"{item_key}: {item_value}")
                                formatted_items.append(f"{i}. {', '.join(item_parts)}")
                            else:
                                formatted_items.append(f"{i}. {item}")
                        result[new_key] = "\n".join(formatted_items)
                        if len(v) > 10:
                            result[new_key] += f"\n... and {len(v) - 10} more items"
                    else:
                        # Simple array - join with semicolon
                        result[new_key] = "; ".join([str(item) for item in v[:50]])  # Limit array size
                        if len(v) > 50:
                            result[new_key] += f" ... ({len(v)} total items)"
                elif v is not None:
                    # Regular value - convert to string
                    str_value = str(v).strip()
                    # Limit value length (Airtable has field value limits)
                    if len(str_value) > 100000:  # Airtable long text limit
                        str_value = str_value[:100000] + "... (truncated)"
                    result[new_key] = str_value
            
            return result
        
        formatted = flatten_dict(data)
        logger.info(f"Auto-flattened {len(formatted)} fields from JSON data")
        return formatted
    
    def _extract_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Extract value from nested dictionary using dot notation path.
        
        Examples:
            "Invoice Number" -> data["Invoice Number"]
            "Invoice.Invoice Number" -> data["Invoice"]["Invoice Number"]
            "Items[0].Product" -> data["Items"][0]["Product"]
        
        Args:
            data: Dictionary to extract from
            path: Dot-notation path (e.g., "Invoice.Invoice Number")
            
        Returns:
            Extracted value or None if not found
        """
        try:
            # Handle array indexing like "Items[0].Product"
            if '[' in path and ']' in path:
                # Split on [ to get base path and index
                parts = path.split('[', 1)
                base_path = parts[0]
                rest = parts[1]
                
                # Get index
                index_part = rest.split(']', 1)[0]
                index = int(index_part)
                remaining_path = rest.split(']', 1)[1].lstrip('.')
                
                # Get base value
                base_value = self._extract_value_by_path(data, base_path)
                if isinstance(base_value, list) and len(base_value) > index:
                    item = base_value[index]
                    if remaining_path:
                        return self._extract_value_by_path(item, remaining_path)
                    return item
                return None
            
            # Simple dot notation path
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
                
                if value is None:
                    return None
            
            return value
            
        except (KeyError, TypeError, IndexError, ValueError) as e:
            logger.debug(f"Could not extract path '{path}': {e}")
            return None
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record by ID.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            Record data or None if not found
        """
        try:
            return self.table.get(record_id)
        except Exception as e:
            logger.error(f"Failed to get Airtable record: {e}")
            return None

