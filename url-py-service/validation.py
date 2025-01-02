import re

def validate_post_data(data):
    original_url = data.get('original_url')
    custom_url = data.get('custom_url')

    if not original_url:
        return 'Original URL is required.'
    if not re.match(r'https?://[^\s/$.?#].[^\s]*', original_url):
        return 'Invalid URL format.'

    if custom_url:
        if len(custom_url) < 8 or len(custom_url) > 16:
            return 'Custom URLs must be between 8 and 16 characters long.'
        # Check if custom URL already exists in Redis
        if redis_1.exists(custom_url) or redis_2.exists(custom_url):
            return 'Custom URL already exists.'
    
    return None

def validate_get_data(short_url):
    if not short_url:
        return 'Short URL is required.'
    return None
