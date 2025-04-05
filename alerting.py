import time
import requests # For webhook
# from twilio.rest import Client # For SMS

class Alerter:
    def __init__(self, config):
        self.config = config['alerting']
        self.enable_console = self.config['enable_console_alerts']
        self.enable_sms = self.config['enable_sms_alerts']
        self.enable_webhook = self.config['enable_webhook_alerts']

        # Initialize Twilio client if needed
        self.twilio_client = None
        if self.enable_sms:
            # try:
            #     self.twilio_client = Client(self.config['twilio_sid'], self.config['twilio_token'])
            #     print("Twilio client initialized.")
            # except Exception as e:
            #     print(f"Error initializing Twilio client: {e}. SMS alerts disabled.")
            #     self.enable_sms = False
             print("Warning: Twilio SMS alerting requires uncommenting code and providing credentials.")
             self.enable_sms = False # Disable if not fully set up


    def send_alert(self, alert_data, source_name="Unknown Camera", gps_coords=None):
        """Sends alerts based on configuration."""
        alert_type = alert_data.get('type', 'Generic')
        track_id = alert_data.get('track_id', 'N/A')
        position = alert_data.get('position', ('N/A', 'N/A'))
        timestamp = alert_data.get('timestamp', time.time())
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

        message = f"ALERT [{formatted_time}] Camera: {source_name} | Type: {alert_type.upper()} | TrackID: {track_id} | Position: {position}"
        if gps_coords:
            message += f" | GPS: ({gps_coords[0]:.6f}, {gps_coords[1]:.6f})"
        if alert_type == 'loitering':
             duration = alert_data.get('duration', 0)
             message += f" | Duration: {duration:.1f}s"


        # 1. Console Alert
        if self.enable_console:
            print("="*20 + " ALERT " + "="*20)
            print(message)
            print("="*47)


        # 2. SMS Alert (Requires Twilio Setup)
        if self.enable_sms and self.twilio_client:
            try:
                # self.twilio_client.messages.create(
                #     body=message,
                #     from_=self.config['twilio_from'],
                #     to=self.config['twilio_to']
                # )
                # print(f"SMS alert sent successfully to {self.config['twilio_to']}")
                pass # Placeholder
            except Exception as e:
                print(f"Error sending SMS alert: {e}")

        # 3. Webhook Alert (e.g., to a dashboard backend)
        if self.enable_webhook:
             payload = {
                 'timestamp': timestamp,
                 'formatted_time': formatted_time,
                 'camera_name': source_name,
                 'alert_type': alert_type,
                 'track_id': track_id,
                 'position_pixels': position,
                 'gps_coordinates': gps_coords, # Send if available
                 'details': alert_data # Send full alert data
             }
             try:
                 response = requests.post(self.config['webhook_url'], json=payload, timeout=5)
                 response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                 print(f"Webhook alert sent successfully to {self.config['webhook_url']}")
             except requests.exceptions.RequestException as e:
                 print(f"Error sending webhook alert: {e}")

        # TODO: Add Dashboard update logic if using Flask/Streamlit directly