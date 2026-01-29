#!/usr/bin/env python3
"""
Add better error handling for file uploads to prevent Unicode decode errors
"""

import os

def patch_file_upload():
    """Add try-catch around file content processing"""
    
    router_file = "/mnt/c/Users/rooma/PycharmProjects/neo_alexadria/backend/app/modules/resources/router.py"
    
    with open(router_file, 'r') as f:
        content = f.read()
    
    # Add chardet import if not present
    if 'import chardet' not in content:
        content = content.replace(
            'from pathlib import Path',
            'from pathlib import Path\n    import chardet'
        )
    
    # Add better file validation
    old_validation = '''# Validate file type
        allowed_types = ["application/pdf", "text/html", "text/plain"]
        allowed_extensions = [".pdf", ".html", ".htm", ".txt"]
        
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        
        if file.content_type not in allowed_types and file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: PDF, HTML, TXT. Got: {file.content_type}"
            )'''
    
    new_validation = '''# Validate file type and content
        allowed_types = ["application/pdf", "text/html", "text/plain"]
        allowed_extensions = [".pdf", ".html", ".htm", ".txt"]
        
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        
        if file.content_type not in allowed_types and file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: PDF, HTML, TXT. Got: {file.content_type}"
            )
        
        # Validate file content is not corrupted
        try:
            # Try to detect encoding for text files
            if file_ext in ['.txt', '.html', '.htm']:
                detected = chardet.detect(file_content[:1024])  # Check first 1KB
                if detected['confidence'] < 0.7:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File encoding could not be reliably detected"
                    )
        except Exception as e:
            logger.warning(f"File validation warning: {e}")'''
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        
        with open(router_file, 'w') as f:
            f.write(content)
        
        print("✅ Added better file upload validation")
    else:
        print("⚠️ File upload validation not found - may already be patched")

if __name__ == "__main__":
    patch_file_upload()
