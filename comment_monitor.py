# Instagram Comment Monitor with OpenAI Humor Replies
# This script monitors ONE specific Instagram post and automatically replies with humor

import time
from instagrapi import Client
from datetime import datetime
import json
import os
import random
import openai
from openai import OpenAI


class OpenAIHumorBot:
    """OpenAI-powered humor bot for generating replies"""
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def generate_humor_response(self, comment_text, username):
        """Generate a humorous response using OpenAI"""
        try:
            # Create a prompt for humor generation
            prompt = f"""
            You are a Pakistani/Indian humor bot that replies to Instagram comments with witty, funny responses.
            
            Rules for your response:
            1. Keep it short (1-2 sentences max)
            2. Use Pakistani/Indian slang and expressions naturally
            3. Be friendly and humorous
            4. Include relevant emojis
            5. Sometimes use Urdu/Hindi words mixed with English
            6. Be respectful and positive
            7. Don't be offensive or inappropriate
            
            Comment from @{username}: "{comment_text}"
            
            Generate a humorous reply:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a funny Pakistani/Indian Instagram comment bot that replies with humor and local slang."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.8
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Add @ mention randomly
            if random.choice([True, False]):
                reply = f"@{username} {reply}"
            
            return reply
            
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            # Fallback responses if OpenAI fails
            fallbacks = [
                f"@{username} Arey bhai! Maza aa gaya! 😄",
                f"Hahaha! {username} ne dil jeet liya! 🤣",
                f"@{username} Comedy ka raja! 👑😂"
            ]
            return random.choice(fallbacks)


class InstagramCommentMonitor:
    """Instagram Comment Monitor with Auto-Reply"""
    
    def __init__(self, username, password, auto_reply=False, openai_api_key=None):
        self.client = Client()
        self.username = username
        self.password = password
        self.auto_reply = auto_reply
        self.seen_comments = set()  # Track comments we've already seen
        self.replied_comments = set()  # Track comments we've replied to
        self.session_file = f"session_{username}.json"  # Save session to avoid repeated 2FA
        
        # Initialize OpenAI bot if auto_reply is enabled
        if auto_reply and openai_api_key:
            self.humor_bot = OpenAIHumorBot(openai_api_key)
        else:
            self.humor_bot = None
        
    def login(self):
        """Login to Instagram with 2FA support and session saving"""
        # Try to load existing session first
        if os.path.exists(self.session_file):
            try:
                print("📁 Found existing session file, trying to load...")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                print("✅ Login successful using saved session!")
                return True
            except Exception as e:
                print(f"⚠️ Saved session failed, trying fresh login: {e}")
                # Delete corrupt session file
                os.remove(self.session_file)
        
        # Fresh login
        try:
            print("Logging into Instagram...")
            self.client.login(self.username, self.password)
            
            # Save session after successful login
            self.client.dump_settings(self.session_file)
            print("✅ Login successful! Session saved for future use.")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "two-factor authentication" in error_msg or "verification_code" in error_msg:
                print("🔐 Two-Factor Authentication detected!")
                print("📱 Please check your authenticator app or SMS for the 6-digit code")
                
                # Get 2FA code from user
                verification_code = input("Enter your 6-digit 2FA code: ").strip()
                
                try:
                    # Login with 2FA code
                    self.client.login(self.username, self.password, verification_code=verification_code)
                    
                    # Save session after successful 2FA login
                    self.client.dump_settings(self.session_file)
                    print("✅ Login successful with 2FA! Session saved for future use.")
                    return True
                except Exception as e2:
                    print(f"❌ 2FA login failed: {e2}")
                    print("💡 Tips:")
                    print("   - Make sure the 2FA code is exactly 6 digits")
                    print("   - Enter the code quickly (they expire fast)")
                    print("   - Try generating a new code if this one expired")
                    return False
            else:
                print(f"❌ Login failed: {e}")
                return False
    
    def get_post_id_from_url(self, post_url):
        """Extract post ID from Instagram URL (supports both posts and reels)"""
        try:
            post_code = None
            
            # Instagram post URL format: https://www.instagram.com/p/POST_CODE/
            if "/p/" in post_url:
                post_code = post_url.split("/p/")[1].split("/")[0]
                print("📝 Detected: Regular Post")
                
            # Instagram reel URL format: https://www.instagram.com/reel/REEL_CODE/
            elif "/reel/" in post_url:
                post_code = post_url.split("/reel/")[1].split("/")[0]
                print("🎬 Detected: Instagram Reel")
                
            else:
                print("❌ Invalid Instagram URL format")
                print("✅ Supported formats:")
                print("   - Posts: https://www.instagram.com/p/ABC123/")
                print("   - Reels: https://www.instagram.com/reel/ABC123/")
                return None
            
            if post_code:
                print(f"🔍 Converting shortcode to media ID: {post_code}")
                
                # Use media_pk_from_code to convert shortcode to numeric ID
                media_id = self.client.media_pk_from_code(post_code)
                print(f"✅ Media ID found: {media_id}")
                return media_id
            
        except Exception as e:
            print(f"❌ Error extracting post ID: {e}")
            print(f"🔗 URL provided: {post_url}")
            print(f"📝 Post code extracted: {post_code if 'post_code' in locals() else 'None'}")
            
            # Try alternative method
            try:
                print("🔄 Trying alternative method...")
                media_info = self.client.media_info_by_shortcode(post_code)
                media_id = media_info.pk
                print(f"✅ Alternative method worked! Media ID: {media_id}")
                return media_id
            except Exception as e2:
                print(f"❌ Alternative method also failed: {e2}")
                return None
    
    def get_post_comments(self, post_id):
        """Get all comments from a specific post"""
        try:
            comments = self.client.media_comments(post_id)
            return comments
        except Exception as e:
            print(f"❌ Error getting comments: {e}")
            return []
    
    def should_reply_to_comment(self, comment):
        """Decide if we should reply to this comment"""
        # Don't reply to your own comments
        if comment.user.username == self.username:
            return False
            
        # Don't reply to already replied comments
        if comment.pk in self.replied_comments:
            return False
            
        # Don't reply to very short comments
        if len(comment.text.strip()) < 3:
            return False
            
        # Skip spam or promotional comments
        spam_keywords = ['follow', 'dm me', 'check out', 'link in bio', 'visit my', 'buy', 'sale']
        comment_lower = comment.text.lower()
        if any(keyword in comment_lower for keyword in spam_keywords):
            return False
            
        return True
    
    def reply_to_comment(self, comment_id, reply_text, media_id):
        """Reply to a specific comment"""
        try:
            # Add random delay to seem more human
            delay = random.randint(10, 30)  # 10-30 seconds
            print(f"⏳ Waiting {delay} seconds before replying...")
            time.sleep(delay)
            
            # Send the reply using the correct method
            # instagrapi uses media_comment() method with reply_to_comment_id parameter
            result = self.client.media_comment(media_id, reply_text, replied_to_comment_id=comment_id)
            print(f"✅ Successfully replied: {reply_text}")
            
            # Mark as replied
            self.replied_comments.add(comment_id)
            return True
            
        except Exception as e:
            print(f"❌ Failed to reply: {e}")
            print(f"🔍 Debug info - Media ID: {media_id}, Comment ID: {comment_id}")
            
            # Try alternative method if the first one fails
            try:
                print("🔄 Trying alternative reply method...")
                # Some versions might use comment_like and then media_comment
                result = self.client.media_comment(media_id, f"@{reply_text}")
                print(f"✅ Alternative method worked!")
                self.replied_comments.add(comment_id)
                return True
            except Exception as e2:
                print(f"❌ Alternative method also failed: {e2}")
                return False
    
    def print_new_comments(self, comments, media_id):
        """Print only new comments that we haven't seen before"""
        new_comments = []
        
        for comment in comments:
            comment_id = comment.pk
            
            if comment_id not in self.seen_comments:
                # This is a new comment!
                self.seen_comments.add(comment_id)
                new_comments.append(comment)
                
                # Print comment details
                print(f"\n🔥 NEW COMMENT DETECTED!")
                print(f"👤 User: @{comment.user.username}")
                print(f"💬 Comment: {comment.text}")
                
                # Handle created_at safely
                try:
                    print(f"⏰ Time: {comment.created_at}")
                except:
                    print(f"⏰ Time: Just now")
                    
                print(f"📍 Comment ID: {comment_id}")
                
                # Auto-reply if enabled
                if self.auto_reply and self.humor_bot and self.should_reply_to_comment(comment):
                    print("🤖 Generating humorous reply...")
                    reply_text = self.humor_bot.generate_humor_response(comment.text, comment.user.username)
                    print(f"💡 Generated reply: {reply_text}")
                    
                    # Send the reply (now passing media_id)
                    if self.reply_to_comment(comment_id, reply_text, media_id):
                        print("✅ Auto-reply sent successfully!")
                    else:
                        print("❌ Auto-reply failed!")
                elif self.auto_reply:
                    print("⏭️ Skipped auto-reply (own comment, spam, or already replied)")
                
                print("-" * 50)
        
        return new_comments
    
    def monitor_post(self, post_url, check_interval=30):
        """Monitor a specific post for new comments"""
        print(f"🎯 Starting to monitor post: {post_url}")
        print(f"🔄 Check interval: {check_interval} seconds")
        print("=" * 60)
        
        # Get post ID from URL
        post_id = self.get_post_id_from_url(post_url)
        if not post_id:
            return
        
        print(f"📝 Post ID: {post_id}")
        
        # Initial load - get existing comments (but don't mark them as seen yet!)
        print("📥 Loading existing comments...")
        initial_comments = self.get_post_comments(post_id)
        
        # Store initial comment IDs for comparison
        initial_comment_ids = {comment.pk for comment in initial_comments}
        
        print(f"✅ Found {len(initial_comments)} existing comments")
        print("👀 Now monitoring for ALL comments (including missed ones)...")
        print("=" * 60)
        
        # Start monitoring loop
        while True:
            try:
                print(f"🔍 Checking for comments... [{datetime.now().strftime('%H:%M:%S')}]")
                
                # Get current comments
                current_comments = self.get_post_comments(post_id)
                
                # On first check, mark older comments as seen but process any new ones
                if not self.seen_comments:  # First time running
                    print("🏁 First check - processing all comments...")
                    # Mark old comments as seen but still process them in case they're new
                    for comment in current_comments:
                        if comment.pk in initial_comment_ids:
                            self.seen_comments.add(comment.pk)
                
                # Print new comments (this will now catch missed comments)
                new_comments = self.print_new_comments(current_comments, post_id)
                
                if new_comments:
                    print(f"✨ Found {len(new_comments)} new comment(s)!")
                else:
                    print("😴 No new comments...")
                
                # Wait before next check
                print(f"⏳ Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                print("⏳ Waiting 60 seconds before retry...")
                time.sleep(60)


def main():
    """Main function to run the comment monitor with auto-reply"""
    print("📱 Instagram Humor Bot with OpenAI Auto-Reply")
    print("=" * 50)
    
    # Get Instagram credentials
    username = input("Enter your Instagram username: ").strip()
    password = input("Enter your Instagram password: ").strip()
    
    # Ask about auto-reply
    auto_reply_input = input("Enable auto-reply with OpenAI humor? (y/n, default=y): ").strip().lower()
    auto_reply = auto_reply_input != 'n'
    
    # Get OpenAI API key if auto-reply is enabled
    openai_api_key = None
    if auto_reply:
        openai_api_key = input("Enter your OpenAI API key: ").strip()
        if not openai_api_key:
            print("❌ OpenAI API key is required for auto-reply!")
            auto_reply = False
    
    # Get post URL to monitor
    print("\nExample: https://www.instagram.com/p/ABC123DEF456/")
    print("Example: https://www.instagram.com/reel/ABC123DEF456/")
    post_url = input("Enter the Instagram post/reel URL to monitor: ").strip()
    
    # Get check interval
    try:
        interval = int(input("Enter check interval in seconds (default 30): ") or "30")
    except ValueError:
        interval = 30
    
    # Create monitor instance
    monitor = InstagramCommentMonitor(username, password, auto_reply, openai_api_key)
    
    # Login
    if not monitor.login():
        print("❌ Failed to login. Please check your credentials.")
        return
    
    # Show settings
    print(f"\n⚙️ Settings:")
    print(f"   🤖 Auto-reply: {'✅ Enabled with OpenAI' if auto_reply else '❌ Disabled'}")
    print(f"   ⏰ Check interval: {interval} seconds")
    print(f"   🎯 Target: {post_url}")
    print("=" * 50)
    
    # Start monitoring
    try:
        monitor.monitor_post(post_url, interval)
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")


if __name__ == "__main__":
    main()