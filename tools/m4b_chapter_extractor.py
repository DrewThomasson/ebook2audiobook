#!/usr/bin/env python3
"""
M4B Chapter Extractor

A command-line tool to extract chapters from M4B audiobook files
and save them as individual MP3 files.

Requirements:
- ffmpeg installed and accessible in PATH
- Python 3.6+

Usage:
    python m4b_chapter_extractor.py input.m4b -o output_folder
"""

import argparse
import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Optional


class M4BChapterExtractor:
    def __init__(self, input_file: str, output_dir: str, quality: str = "192k"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.quality = quality
        
        # Validate input file
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not self.input_file.suffix.lower() in ['.m4b', '.m4a']:
            raise ValueError("Input file must be an M4B or M4A file")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available in the system PATH."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_chapters(self) -> List[Dict]:
        """Extract chapter information from the M4B file."""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_chapters',
            str(self.input_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return data.get('chapters', [])
        except subprocess.CalledProcessError as e:
            print(f"Error getting chapters: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing chapter data: {e}")
            return []
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing/replacing invalid characters."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        # Ensure filename isn't too long (limit to 200 characters)
        if len(filename) > 200:
            filename = filename[:200].strip()
        
        return filename or "Chapter"
    
    def format_time(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS.mmm format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def extract_chapter(self, chapter: Dict, chapter_num: int, total_chapters: int) -> bool:
        """Extract a single chapter to MP3 file."""
        # Get chapter title
        title = chapter.get('tags', {}).get('title', f"Chapter {chapter_num:02d}")
        title = self.sanitize_filename(title)
        
        # Create output filename
        output_filename = f"{chapter_num:02d} - {title}.mp3"
        output_path = self.output_dir / output_filename
        
        # Get start and end times
        start_time = float(chapter['start_time'])
        end_time = float(chapter['end_time'])
        duration = end_time - start_time
        
        print(f"Extracting [{chapter_num}/{total_chapters}]: {title}")
        print(f"  Duration: {self.format_time(duration)}")
        
        # FFmpeg command to extract chapter
        cmd = [
            'ffmpeg',
            '-i', str(self.input_file),
            '-ss', str(start_time),
            '-t', str(duration),
            '-acodec', 'libmp3lame',
            '-ab', self.quality,
            '-map_metadata', '0',
            '-id3v2_version', '3',
            '-metadata', f'title={title}',
            '-metadata', f'track={chapter_num}/{total_chapters}',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Saved: {output_filename}")
                return True
            else:
                print(f"  ✗ Error extracting chapter: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ✗ Exception during extraction: {e}")
            return False
    
    def extract_all_chapters(self) -> bool:
        """Extract all chapters from the M4B file."""
        print(f"Processing: {self.input_file.name}")
        print(f"Output directory: {self.output_dir}")
        
        # Check if FFmpeg is available
        if not self.check_ffmpeg():
            print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
            return False
        
        # Get chapters
        chapters = self.get_chapters()
        if not chapters:
            print("No chapters found in the M4B file.")
            return False
        
        print(f"Found {len(chapters)} chapters")
        print("-" * 50)
        
        # Extract each chapter
        success_count = 0
        for i, chapter in enumerate(chapters, 1):
            if self.extract_chapter(chapter, i, len(chapters)):
                success_count += 1
            print()
        
        # Summary
        print("-" * 50)
        print(f"Extraction complete: {success_count}/{len(chapters)} chapters extracted successfully")
        
        if success_count == len(chapters):
            print("All chapters extracted successfully!")
            return True
        else:
            print(f"Warning: {len(chapters) - success_count} chapters failed to extract")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract chapters from M4B audiobook files as individual MP3 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python m4b_chapter_extractor.py audiobook.m4b -o chapters/
    python m4b_chapter_extractor.py audiobook.m4b -o output/ -q 128k
    python m4b_chapter_extractor.py audiobook.m4b -o output/ --quality 256k

Requirements:
    - FFmpeg must be installed and accessible in PATH
    - Input file must be M4B or M4A format
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input M4B audiobook file'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for extracted MP3 chapters'
    )
    
    parser.add_argument(
        '-q', '--quality',
        default='192k',
        help='MP3 audio quality/bitrate (default: 192k). Examples: 128k, 192k, 256k, 320k'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Create extractor instance
        extractor = M4BChapterExtractor(
            input_file=args.input_file,
            output_dir=args.output,
            quality=args.quality
        )
        
        # Extract chapters
        success = extractor.extract_all_chapters()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()