#!/usr/bin/env python3
"""
Extract transcripts from all videos in a YouTube channel
"""

import sys
import time
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

# Try to import scrapetube (for getting channel videos)
try:
    import scrapetube
    HAS_SCRAPETUBE = True
except ImportError:
    HAS_SCRAPETUBE = False
    print("⚠️ scrapetube not available, using alternative method")

def get_channel_id(url):
    """Extract channel ID or handle from YouTube URL"""
    parsed = urlparse(url)
    path = parsed.path
    
    # Handle different channel URL formats
    if '/@' in path:
        return path.split('/@')[1].split('/')[0], 'handle'
    elif '/channel/' in path:
        return path.split('/channel/')[1].split('/')[0], 'id'
    elif '/c/' in path:
        return path.split('/c/')[1].split('/')[0], 'custom'
    elif '/user/' in path:
        return path.split('/user/')[1].split('/')[0], 'user'
    
    raise ValueError(f"Could not extract channel identifier from URL: {url}")

def get_channel_videos(channel_url):
    """Get all video IDs from a channel"""
    try:
        channel_id, id_type = get_channel_id(channel_url)
        print(f"📺 Channel identifier: {channel_id} (type: {id_type})")
        
        if HAS_SCRAPETUBE:
            if id_type == 'handle':
                videos = scrapetube.get_channel(channel_username=channel_id)
            else:
                videos = scrapetube.get_channel(channel_id=channel_id)
            
            video_ids = [video['videoId'] for video in videos]
            return video_ids
        else:
            print("❌ scrapetube is required for channel extraction")
            print("Install with: pip install scrapetube")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error getting channel videos: {str(e)}")
        sys.exit(1)

def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def extract_channel(channel_url):
    """Extract transcripts from all videos in a channel"""
    try:
        print("🔍 Fetching channel videos...")
        video_ids = get_channel_videos(channel_url)
        total_videos = len(video_ids)
        
        print(f"📊 Found {total_videos} videos")
        
        # Prepare output file
        output = "=" * 80 + "\n"
        output += f"CHAÎNE: {channel_url}\n"
        output += f"DATE D'EXTRACTION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"NOMBRE DE VIDÉOS: {total_videos}\n"
        output += "=" * 80 + "\n\n"
        
        successful = 0
        failed = 0
        
        for idx, video_id in enumerate(video_ids, 1):
            try:
                print(f"[{idx}/{total_videos}] Processing video: {video_id}")
                
                # Get transcript
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([entry['text'] for entry in transcript_list])
                
                # Calculate duration
                duration = transcript_list[-1]['start'] + transcript_list[-1]['duration'] if transcript_list else 0
                
                # Add to output
                output += "┌" + "─" * 74 + "┐\n"
                output += f"│ VIDÉO #{idx}{' ' * (74 - len(f'VIDÉO #{idx}'))}│\n"
                output += "├" + "─" * 74 + "┤\n"
                output += f"│ TITRE: Video {video_id}{' ' * (74 - len(f'TITRE: Video {video_id}'))}│\n"
                output += f"│ URL: https://www.youtube.com/watch?v={video_id}{' ' * (74 - len(f'URL: https://www.youtube.com/watch?v={video_id}'))}│\n"
                output += f"│ DURÉE: {format_duration(duration)}{' ' * (74 - len(f'DURÉE: {format_duration(duration)}'))}│\n"
                output += f"│ DATE: {datetime.now().strftime('%Y-%m-%d')}{' ' * (74 - len(f'DATE: {datetime.now().strftime(\"%Y-%m-%d\")}'))}│\n"
                output += "└" + "─" * 74 + "┘\n\n"
                
                output += full_text + "\n\n"
                output += "=" * 80 + "\n\n"
                
                successful += 1
                
                # Respect rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Failed to extract transcript for {video_id}: {str(e)}")
                failed += 1
                continue
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transcripts_channel_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"\n✅ Extraction complete!")
        print(f"📊 Successful: {successful}/{total_videos}")
        print(f"❌ Failed: {failed}/{total_videos}")
        print(f"💾 Saved to: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_channel.py <channel_url>")
        sys.exit(1)
    
    channel_url = sys.argv[1]
    extract_channel(channel_url)
