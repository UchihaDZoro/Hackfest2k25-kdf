import time
import numpy as np
from collections import defaultdict, deque
import cv2 # For pointPolygonTest

class BehaviorAnalyzer:
    def __init__(self, config):
        self.config = config
        # Store track history: track_id -> deque([(timestamp, center_x, center_y), ...])
        self.track_history = defaultdict(lambda: deque(maxlen=100)) # Store last ~3 seconds at 30fps
        # Store first seen timestamp for loitering: track_id -> timestamp
        self.first_seen = {}
        # Store last alert time for cooldown: track_id -> timestamp
        self.last_alert_time = {}
        # Store state: track_id -> { "loitering": False, "near_fence": False }
        self.track_state = defaultdict(dict)

        self.fence_zones_poly = []
        if config['behavior_analysis']['fence_zones']:
             for zone in config['behavior_analysis']['fence_zones']:
                 self.fence_zones_poly.append(np.array(zone, np.int32))


    def update(self, tracks):
        """Analyzes tracks for suspicious behavior."""
        current_time = time.time()
        active_track_ids = set()
        alerts = [] # List of dictionaries: {'type': 'loitering'/'fence', 'track_id': id, 'position': (x,y)}

        if tracks is None or len(tracks) == 0:
             # Clean up old tracks if no tracks detected in frame
             self._cleanup_old_tracks(current_time, active_track_ids)
             return alerts

        for track in tracks:
            # Assuming track format: [x1, y1, x2, y2, track_id, conf, cls]
            if len(track) < 5: continue
            x1, y1, x2, y2 = map(int, track[:4])
            track_id = int(track[4])
            active_track_ids.add(track_id)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2 # Using bottom center might be better for proximity
            bottom_center_y = y2

            # Update history
            self.track_history[track_id].append((current_time, center_x, bottom_center_y))

            # --- 1. Loitering Detection ---
            loiter_threshold = self.config['behavior_analysis']['loitering_threshold_seconds']
            alert_cooldown = self.config['alerting']['alert_cooldown_seconds']

            if track_id not in self.first_seen:
                self.first_seen[track_id] = current_time
                self.track_state[track_id]['loitering'] = False # Initial state

            # Check duration
            duration = current_time - self.first_seen[track_id]
            is_currently_loitering = False
            if duration > loiter_threshold:
                # Optional: Check if movement is minimal within the history duration
                # Simple check: just time presence for now
                is_currently_loitering = True


            # Trigger alert only if state changes to loitering and cooldown passed
            if is_currently_loitering and not self.track_state[track_id].get('loitering', False):
                 last_alert = self.last_alert_time.get(track_id, 0)
                 if current_time - last_alert > alert_cooldown:
                     alerts.append({
                         'type': 'loitering',
                         'track_id': track_id,
                         'duration': duration,
                         'position': (center_x, bottom_center_y),
                         'timestamp': current_time
                     })
                     self.last_alert_time[track_id] = current_time
                     self.track_state[track_id]['loitering'] = True # Update state
            elif not is_currently_loitering:
                 self.track_state[track_id]['loitering'] = False # Reset state if not loitering


            # --- 2. Fence Proximity / Tampering Detection ---
            proximity_threshold = self.config['behavior_analysis']['fence_proximity_threshold']
            is_near_fence = False
            if self.fence_zones_poly:
                for zone_poly in self.fence_zones_poly:
                    # Check distance from track's bottom center point to the polygon boundary
                    dist = cv2.pointPolygonTest(zone_poly, (center_x, bottom_center_y), True)
                    # dist > 0: inside, dist < 0: outside, dist == 0: on boundary
                    # Check if point is close to the boundary (negative dist close to 0) or inside
                    if dist >= -proximity_threshold: # Close to or inside the zone
                        is_near_fence = True
                        break # Found near at least one zone


            # Trigger alert only if state changes to near_fence and cooldown passed
            if is_near_fence and not self.track_state[track_id].get('near_fence', False):
                 last_alert = self.last_alert_time.get(track_id, 0) # Share cooldown or use separate?
                 if current_time - last_alert > alert_cooldown:
                     alerts.append({
                         'type': 'fence_proximity',
                         'track_id': track_id,
                         'position': (center_x, bottom_center_y),
                         'timestamp': current_time
                     })
                     self.last_alert_time[track_id] = current_time
                     self.track_state[track_id]['near_fence'] = True # Update state
            elif not is_near_fence:
                 self.track_state[track_id]['near_fence'] = False # Reset state

            # --- 3. Other Behaviors (Placeholders) ---
            # TODO: Add crawling detection (requires pose estimation or aspect ratio analysis)
            # TODO: Add drone detection alert (based on class from detector)


        # --- Cleanup old track data ---
        self._cleanup_old_tracks(current_time, active_track_ids)

        return alerts

    def _cleanup_old_tracks(self, current_time, active_track_ids):
        """Removes data for tracks that haven't been seen for a while."""
        cleanup_threshold = 60 # Seconds after which to remove inactive track data
        ids_to_remove = [
            tid for tid, history in self.track_history.items()
            if tid not in active_track_ids and history and (current_time - history[-1][0] > cleanup_threshold)
        ]

        for tid in ids_to_remove:
            if tid in self.track_history: del self.track_history[tid]
            if tid in self.first_seen: del self.first_seen[tid]
            if tid in self.last_alert_time: del self.last_alert_time[tid]
            if tid in self.track_state: del self.track_state[tid]
            # print(f"Cleaned up data for inactive track ID: {tid}")