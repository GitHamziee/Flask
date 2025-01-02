from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
import datetime
from zap_scanner import ZAPScanner  # Ensure you have this module or logic
from bson.objectid import ObjectId

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017")
db = client["Pentesting"]

# Initialize the ZAP Scanner
zap_scanner = ZAPScanner()  # Replace with your ZAP scanner initialization

def execute_scheduled_scans():
    """Execute scans that are scheduled to run."""
    now = datetime.datetime.utcnow()
    scheduled_scans = db.ScheduledScans.find({"status": "pending", "schedule_time": {"$lte": now}})
    
    for scan in scheduled_scans:
        try:
            # Perform the scan
            if scan['scan_type'] == 'spider':
                result = zap_scanner.spider_scan(scan['url'], scan['max_depth'])
            elif scan['scan_type'] == 'active':
                result = zap_scanner.active_scan(scan['url'])
            elif scan['scan_type'] == 'comprehensive':
                result = zap_scanner.comprehensive_scan(scan['url'])
            else:
                result = {"error": "Invalid scan type selected"}

            # Update the scan result in the database
            db.ScheduledScans.update_one(
                {"_id": scan["_id"]},
                {"$set": {"status": "completed", "result": result}}
            )
        except Exception as e:
            # Update the scan status as failed
            db.ScheduledScans.update_one(
                {"_id": scan["_id"]},
                {"$set": {"status": "failed", "result": {"error": str(e)}}}
            )

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(execute_scheduled_scans, 'interval', minutes=1)  # Run every minute
scheduler.start()
