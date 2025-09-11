import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class ResultsManager:
    def __init__(self, results_dir="results"):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def get_result_files(self) -> List[Dict[str, Any]]:
        """Get a list of all saved result files"""
        files = []
        for filename in os.listdir(self.results_dir):
            if filename.startswith("evaluation_") and filename.endswith(".json"):
                file_path = os.path.join(self.results_dir, filename)
                # Get file information
                stats = os.stat(file_path)
                # Extract session ID and timestamp from file name
                parts = filename.replace("evaluation_", "").replace(".json", "").split("_")
                session_id = parts[0]
                timestamp = "_".join(parts[1:]) if len(parts) > 1 else ""
                
                # Read summary information from the result file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Calculate a simple summary
                        total = len(data)
                        passed = sum(1 for r in data if r.get("evaluation", {}).get("passed") == True)
                        failed = sum(1 for r in data if r.get("evaluation", {}).get("passed") == False)
                        error = total - passed - failed
                except Exception as e:
                    print(f"ファイル読み込みエラー {filename}: {str(e)}")
                    total, passed, failed, error = 0, 0, 0, 0
                
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "human_date": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "file_size": round(stats.st_size / 1024, 1),  # KBでサイズ表示
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "error": error,
                        "pass_rate": round(passed / total * 100, 2) if total > 0 else 0
                    }
                })
        
        # Sort by date in descending order
        return sorted(files, key=lambda x: x["human_date"], reverse=True)
    
    def get_result_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get results from file names"""
        file_path = os.path.join(self.results_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"ファイル読み込みエラー {filename}: {str(e)}")
                return None
        return None
    
    def get_results_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all result files related to the session ID"""
        return [f for f in self.get_result_files() if f["session_id"] == session_id]
