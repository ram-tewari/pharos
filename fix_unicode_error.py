#!/usr/bin/env python3
"""
Fix for Unicode decode error in file upload endpoint.
This patch handles binary files and non-UTF-8 content gracefully.
"""

# Add this to backend/app/modules/resources/router.py in the upload_resource_file function
# Replace the file reading section around line 280-320

FIXED_FILE_HANDLING = '''
        # Save file to temporary location with proper encoding handling
        storage_dir = Path("storage/uploads")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = storage_dir / safe_filename
        
        # Write binary content directly (no encoding issues)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved to: {file_path}")
        
        # Create resource record with file path as identifier
        resource_data = {
            "url": f"file://{file_path.absolute()}",
            "title": title or file.filename or "Uploaded Document",
            "description": description,
            "creator": creator,
            "language": language,
            "type": type or file_ext.lstrip("."),
            "source": str(file_path.absolute()),
            "identifier": str(file_path.absolute()),
        }
        
        resource = create_pending_resource(db, resource_data)
        logger.info(f"Resource created: {resource.id}, file stored at: {file_path}")
        
        # Set response status
        response.status_code = status.HTTP_202_ACCEPTED
        
        # Process file with proper encoding detection
        try:
            from ...utils.content_extractor import ContentExtractor
            from ...shared.ai_core import AICore
            
            ce_instance = ContentExtractor()
            ai_instance = AICore()
            
            # Process based on file type with encoding safety
            if file_ext == '.pdf':
                # PDF files are binary - no encoding issues
                extracted = ce_instance.extract_from_pdf(file_content)
            elif file_ext in ['.html', '.htm']:
                # HTML files - detect encoding or use UTF-8 with error handling
                try:
                    # Try UTF-8 first
                    html_content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    # Fallback to latin-1 or detect encoding
                    import chardet
                    detected = chardet.detect(file_content)
                    encoding = detected.get('encoding', 'latin-1')
                    html_content = file_content.decode(encoding, errors='replace')
                
                extracted = ce_instance.extract_from_html(html_content)
            elif file_ext == '.txt':
                # Text files - detect encoding
                try:
                    text_content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    import chardet
                    detected = chardet.detect(file_content)
                    encoding = detected.get('encoding', 'latin-1')
                    text_content = file_content.decode(encoding, errors='replace')
                
                extracted = {
                    'content': text_content,
                    'title': title or file.filename or "Uploaded Text",
                    'metadata': {}
                }
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
'''

print("Apply this fix to backend/app/modules/resources/router.py")
print("Also add 'import chardet' to requirements.txt")
