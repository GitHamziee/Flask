import requests
import time


class ZAPScanner:
    def __init__(self, zap_url="http://localhost:8080"):
        """
        Initialize the ZAPScanner with the ZAP URL.
        No API key is required.
        """
        self.zap_url = zap_url

    def spider_scan(self, target_url, max_depth=10):
        """
        Perform a spider scan on the target URL.
        """
        try:
            spider_url = f"{self.zap_url}/JSON/spider/action/scan/"
            response = requests.get(spider_url, params={
                "url": target_url,
                "maxChildren": max_depth,
            })

            if response.status_code == 200:
                scan_id = response.json().get("scan")
                print(f"Spider scan started. Scan ID: {scan_id}")
                return {"scan_id": scan_id, "status": "Spider scan started"}
            else:
                return {"error": f"Spider scan failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def check_spider_progress(self, scan_id):
        """
        Check the progress of the spider scan.
        """
        try:
            status_url = f"{self.zap_url}/JSON/spider/view/status/"
            while True:
                response = requests.get(status_url, params={"scanId": scan_id})
                if response.status_code == 200:
                    progress = int(response.json().get("status", 0))
                    print(f"Spider scan progress: {progress}%")
                    if progress >= 100:
                        print("Spider scan completed.")
                        break
                    time.sleep(2)  # Poll every 2 seconds
                else:
                    return {"error": f"Failed to fetch spider scan status with status code {response.status_code}"}
            return {"status": "Spider scan completed"}
        except Exception as e:
            return {"error": str(e)}

    def stop_spider_scan(self, scan_id):
        """
        Stop a spider scan by scan ID.
        """
        try:
            stop_url = f"{self.zap_url}/JSON/spider/action/stop/"
            response = requests.get(stop_url, params={"scanId": scan_id})
            if response.status_code == 200:
                return {"status": "Spider scan stopped successfully"}
            else:
                return {"error": f"Failed to stop spider scan with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def active_scan(self, target_url):
        """
        Perform an active scan on the target URL.
        """
        try:
            scan_url = f"{self.zap_url}/JSON/ascan/action/scan/"
            response = requests.get(scan_url, params={"url": target_url})

            if response.status_code == 200:
                scan_id = response.json().get("scan")
                print(f"Active scan started. Scan ID: {scan_id}")
                return {"scan_id": scan_id, "status": "Active scan started"}
            else:
                return {"error": f"Active scan failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def check_active_progress(self, scan_id):
        """
        Check the progress of the active scan.
        """
        try:
            status_url = f"{self.zap_url}/JSON/ascan/view/status/"
            while True:
                response = requests.get(status_url, params={"scanId": scan_id})
                if response.status_code == 200:
                    progress = int(response.json().get("status", 0))
                    print(f"Active scan progress: {progress}%")
                    if progress >= 100:
                        print("Active scan completed.")
                        break
                    time.sleep(2)  # Poll every 2 seconds
                else:
                    return {"error": f"Failed to fetch active scan status with status code {response.status_code}"}
            return {"status": "Active scan completed"}
        except Exception as e:
            return {"error": str(e)}

    def stop_active_scan(self, scan_id):
        """
        Stop an active scan by scan ID.
        """
        try:
            stop_url = f"{self.zap_url}/JSON/ascan/action/stop/"
            response = requests.get(stop_url, params={"scanId": scan_id})
            if response.status_code == 200:
                return {"status": "Active scan stopped successfully"}
            else:
                return {"error": f"Failed to stop active scan with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_alerts(self, target_url):
        """
        Retrieve alerts for the given target URL.
        """
        try:
            alerts_url = f"{self.zap_url}/JSON/core/view/alerts/"
            response = requests.get(alerts_url, params={"baseurl": target_url})

            if response.status_code == 200:
                alerts = response.json().get("alerts", [])
                print(f"Retrieved {len(alerts)} alerts.")
                return {"alerts": alerts}
            else:
                return {"error": f"Failed to fetch alerts with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def comprehensive_scan(self, target_url, max_depth=10):
        """
        Perform a comprehensive scan (Spider + Active Scan) on the target URL.
        """
        try:
            # Perform Spider Scan
            spider_scan_result = self.spider_scan(target_url, max_depth)
            if "error" in spider_scan_result:
                return spider_scan_result
            self.check_spider_progress(spider_scan_result["scan_id"])

            # Perform Active Scan
            active_scan_result = self.active_scan(target_url)
            if "error" in active_scan_result:
                return active_scan_result
            self.check_active_progress(active_scan_result["scan_id"])

            # Retrieve Alerts
            alerts = self.get_alerts(target_url)
            return alerts
        except Exception as e:
            return {"error": str(e)}
