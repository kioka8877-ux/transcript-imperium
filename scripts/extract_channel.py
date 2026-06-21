#!/usr/bin/env python3
"""
Extract transcripts from all videos in a YouTube channel using yt-dlp
"""

import sys
import time
import json
import subprocess
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

def get_channel_videos(channel_url):
    """Get all video IDs from a channel using yt-dlp"""
    try:
        print(f"📺 Fetching videos from: {channel_url}")
        
        # Use yt-dlp to get video list
        result = subprocess.run(
            [
                'yt-dlp',
                '--flat-playlist',
                '--dump-json',
                '--no-warnings',
                channel_url
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp error: {result.stderr}")
        
        # Parse JSON output
        video_ids = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                video_id = data.get('id')
                if video_id:
                    video_ids.append(video_id)
            except json.JSONDecodeError:
                continue
        
        return video_ids
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout while fetching channel videos")
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
        
        if total_videos == 0:
            print("⚠️ No videos found in this channel")
            sys.exit(1)
        
        # Prepare output file
        extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        output = "=" * 80 + "\n"
        output += f"CHAÎNE: {channel_url}\n"
        output += f"DATE D'EXTRACTION: {extraction_date}\n"
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
                
                # Format current date once
                current_date = datetime.now().strftime('%Y-%m-%d')
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Add to output
                output += "┌" + "─" * 74 + "┐\n"
                
                video_header = f"VIDÉO #{idx}"
                output += f"│ {video_header}{' ' * (72 - len(video_header))}│\n"
                output += "├" + "─" * 74 + "┤\n"
                
                title_line = f"TITRE: Video {video_id}"
                output += f"│ {title_line}{' ' * (72 - len(title_line))}│\n"
                
                url_line = f"URL: {video_url}"
                output += f"│ {url_line}{' ' * (72 - len(url_line))}│\n"
                
                duration_line = f"DURÉE: {format_duration(duration)}"
                output += f"│ {duration_line}{' ' * (72 - len(duration_line))}│\n"
                
                date_line = f"DATE: {current_date}"
                output += f"│ {date_line}{' ' * (72 - len(date_line))}│\n"
                
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_channel.py <channel_url>")
        sys.exit(1)
    
    channel_url = sys.argv[1]
    extract_channel(channel_url)
