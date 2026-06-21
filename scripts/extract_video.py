#!/usr/bin/env python3
"""
Extract transcript from a single YouTube video
"""

import sys
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed = urlparse(url)
    
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
        elif parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
        elif parsed.path.startswith('/v/'):
            return parsed.path.split('/')[2]
    elif parsed.hostname in ['youtu.be']:
        return parsed.path[1:]
    
    raise ValueError(f"Could not extract video ID from URL: {url}")

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def extract_single_video(video_url):
    """Extract transcript from a single video"""
    try:
        video_id = get_video_id(video_url)
        print(f"📹 Extracting transcript for video ID: {video_id}")
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text
        full_text = " ".join([entry['text'] for entry in transcript_list])
        
        # Calculate duration
        duration = transcript_list[-1]['start'] + transcript_list[-1]['duration'] if transcript_list else 0
        
        # Format output
        output = "=" * 80 + "\n"
        output += f"VIDÉO: Single Video Extract\n"
        output += f"DATE D'EXTRACTION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += "=" * 80 + "\n\n"
        
        output += "┌" + "─" * 74 + "┐\n"
        output += f"│ VIDÉO #1{' ' * 66}│\n"
        output += "├" + "─" * 74 + "┤\n"
        output += f"│ TITRE: Video from {video_id}{' ' * (74 - len(f'TITRE: Video from {video_id}'))}│\n"
        output += f"│ URL: {video_url}{' ' * (74 - len(f'URL: {video_url}'))}│\n"
        output += f"│ DURÉE: {format_duration(duration)}{' ' * (74 - len(f'DURÉE: {format_duration(duration)}'))}│\n"
        output += f"│ DATE: {datetime.now().strftime('%Y-%m-%d')}{' ' * (74 - len(f'DATE: {datetime.now().strftime(\"%Y-%m-%d\")}'))}│\n"
        output += "└" + "─" * 74 + "┘\n\n"
        
        output += full_text + "\n\n"
        output += "=" * 80 + "\n"
        
        # Save to file
        filename = f"transcript_{video_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ Transcript saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_video.py <video_url>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    extract_single_video(video_url)
