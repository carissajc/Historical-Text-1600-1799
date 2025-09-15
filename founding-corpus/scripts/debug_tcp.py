#!/usr/bin/env python3
"""
Debug version of TCP loader to see what's in the zip files.
"""

import zipfile
from pathlib import Path

def debug_zip_contents(zip_path):
    """Debug what's inside a zip file."""
    print(f"\n=== Debugging {zip_path} ===")
    
    try:
        with zipfile.ZipFile(zip_path) as zf:
            print(f"Zip file: {zip_path}")
            print(f"Total files: {len(zf.namelist())}")
            
            # Show first 20 files
            print("\nFirst 20 files:")
            for i, name in enumerate(zf.namelist()[:20]):
                print(f"  {i+1:2d}. {name}")
            
            # Look for XML files
            xml_files = [name for name in zf.namelist() if name.lower().endswith((".xml", ".tei"))]
            print(f"\nXML files found: {len(xml_files)}")
            
            if xml_files:
                print("First 10 XML files:")
                for i, name in enumerate(xml_files[:10]):
                    print(f"  {i+1:2d}. {name}")
                
                # Try to read the first XML file
                if xml_files:
                    first_xml = xml_files[0]
                    print(f"\nTrying to read first XML file: {first_xml}")
                    try:
                        content = zf.read(first_xml)
                        print(f"Content length: {len(content)} bytes")
                        print(f"First 500 characters:")
                        print(content[:500].decode('utf-8', errors='ignore'))
                    except Exception as e:
                        print(f"Error reading XML: {e}")
            
            # Look for other file types
            other_extensions = set()
            for name in zf.namelist():
                if '.' in name:
                    ext = name.split('.')[-1].lower()
                    other_extensions.add(ext)
            
            print(f"\nOther file extensions found: {sorted(other_extensions)}")
            
    except Exception as e:
        print(f"Error opening zip file: {e}")

def main():
    """Debug all TCP zip files."""
    print("=== TCP Zip Files Debug ===")
    
    # Check Evans-TCP
    evans_zip = Path("data_raw/evans_tcp/evans.zip")
    if evans_zip.exists():
        debug_zip_contents(evans_zip)
    else:
        print("Evans zip not found")
    
    # Check ECCO-TCP
    ecco_zip = Path("data_raw/ecco_tcp/ecco_all.zip")
    if ecco_zip.exists():
        debug_zip_contents(ecco_zip)
    else:
        print("ECCO zip not found")

if __name__ == "__main__":
    main() 