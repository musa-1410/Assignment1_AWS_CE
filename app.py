import os
import requests
import boto3
from flask import Flask, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
s3 = boto3.client('s3', region_name='us-east-1')

API_KEY = '2sRJSch08FWMboQQkYZI2ii1FCVsdqkT'
BUCKET_NAME = 'unievent-posters-giki-unique123' # Change to your globally unique bucket name

def fetch_and_store_events():
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={API_KEY}&size=5"
    response = requests.get(url).json()
    events = []
    
    for event in response.get('_embedded', {}).get('events', []):
        title = event['name']
        date = event.get('dates', {}).get('start', {}).get('localDate', 'TBD')
        venue = event.get('_embedded', {}).get('venues', [{}])[0].get('name', 'TBD')
        image_url = event['images'][0]['url']
        
        # Download image from API and upload to S3
        img_data = requests.get(image_url).content
        filename = secure_filename(f"{title.replace(' ', '_')}.jpg")
        
        # Upload to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=img_data, ContentType='image/jpeg')
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
        events.append({'title': title, 'date': date, 'venue': venue, 'image': s3_url})
        
    return events

@app.route('/')
def index():
    # In a production app, you'd cache this in memory or a database to avoid hitting the API on every page load
    events = fetch_and_store_events()
    return render_template('index.html', events=events)
# --- Add this new route ---
@app.route('/health')
def health_check():
    return "OK", 200
# --------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)