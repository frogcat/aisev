import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from starlette.responses import StreamingResponse
import io
import csv

class HTMLExporter:
    """Class for outputting evaluation results in HTML format"""
    
    @staticmethod
    def generate_html_report(results: List[Dict[str, Any]], session_id: str, timestamp: str = None) -> str:
        """Generate HTML reports from evaluation results"""
        
        # Basic information
        if timestamp:
            report_date = timestamp
        else:
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculation of statistics
        total = len(results)
        # Exclude skipped evaluation items
        not_skipped_results = [r for r in results if not r.get("evaluation", {}).get("skipped", False)]
        passed = sum(1 for r in not_skipped_results if r.get("evaluation", {}).get("passed") == True)
        failed = sum(1 for r in not_skipped_results if r.get("evaluation", {}).get("passed") == False)
        error = len(not_skipped_results) - passed - failed
        skipped = total - len(not_skipped_results)
        pass_rate = round(passed / len(not_skipped_results) * 100, 2) if len(not_skipped_results) > 0 else 0
        
        # Calculation of statistics by category
        category_stats = {}
        for r in results:
            cat = r.get("category", "未分類")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
            
            # Check whether the evaluation has been skipped
            if r.get("evaluation", {}).get("skipped", False):
                category_stats[cat]["skipped"] += 1
            else:
                category_stats[cat]["total"] += 1
                if r.get("evaluation", {}).get("passed") == True:
                    category_stats[cat]["passed"] += 1
                elif r.get("evaluation", {}).get("passed") == False:
                    category_stats[cat]["failed"] += 1
                else:
                    category_stats[cat]["error"] += 1
        
        # Generation of HTML
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM評価レポート - {report_date}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .container {{
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-box {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .summary-item {{
            flex: 1;
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            margin: 0 10px;
        }}
        .total {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
        }}
        .passed {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }}
        .failed {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }}
        .error {{
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
        }}
        .skipped {{
            background-color: #e9ecef;
            border: 1px solid #ced4da;
        }}
        .progress-bar {{
            height: 20px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .progress {{
            height: 100%;
            background-color: #28a745;
            border-radius: 5px;
            text-align: center;
            color: white;
            line-height: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .detail-box {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .requirement {{
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid #6c757d;
            margin-bottom: 10px;
        }}
        .prompt {{
            padding: 10px;
            background: #e9ecef;
            border-radius: 5px;
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        .response {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        .evaluation {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .passed-result {{
            background-color: #d4edda;
        }}
        .failed-result {{
            background-color: #f8d7da;
        }}
        .error-result {{
            background-color: #fff3cd;
        }}
        .skipped-result {{
            background-color: #e9ecef;
        }}
        .header-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .category-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            background: #6c757d;
            color: white;
            font-size: 0.8em;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>LLM評価レポート</h1>
        <div class="header-info">
            <div>
                <p><strong>セッションID:</strong> {session_id}</p>
                <p><strong>レポート生成日時:</strong> {report_date}</p>
            </div>
        </div>
        
        <h2>評価サマリー</h2>
        <div class="summary-box">
            <div class="summary-item total">
                <h3>{total}</h3>
                <p>テスト総数</p>
            </div>
            <div class="summary-item passed">
                <h3>{passed}</h3>
                <p>合格</p>
            </div>
            <div class="summary-item failed">
                <h3>{failed}</h3>
                <p>不合格</p>
            </div>
            <div class="summary-item error">
                <h3>{error}</h3>
                <p>エラー</p>
            </div>
            <div class="summary-item skipped">
                <h3>{skipped}</h3>
                <p>スキップ</p>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress" style="width: {pass_rate}%;">{pass_rate}% 合格</div>
        </div>
        
        <h2>カテゴリ別結果</h2>
        <table>
            <thead>
                <tr>
                    <th>カテゴリ</th>
                    <th>テスト数</th>
                    <th>合格</th>
                    <th>不合格</th>
                    <th>エラー</th>
                    <th>スキップ</th>
                    <th>合格率</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add table rows for each category
        for category, stats in category_stats.items():
            cat_pass_rate = round(stats["passed"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0
            html += f"""
                <tr>
                    <td>{category}</td>
                    <td>{stats["total"]}</td>
                    <td>{stats["passed"]}</td>
                    <td>{stats["failed"]}</td>
                    <td>{stats["error"]}</td>
                    <td>{stats["skipped"]}</td>
                    <td>{cat_pass_rate}%</td>
                </tr>"""
        
        html += """
            </tbody>
        </table>
        
        <h2>詳細結果</h2>
"""
        
        # Add details of each test result
        for i, result in enumerate(results):
            prompt = result.get("prompt", "")
            category = result.get("category", "未分類")
            requirement = result.get("requirement", "")
            target_response = result.get("target_response", "")
            evaluation = result.get("evaluation", {})
            passed = evaluation.get("passed")
            skipped = evaluation.get("skipped", False)
            reason = evaluation.get("reason", "")
            
            if skipped:
                result_class = "skipped-result"
                result_text = "スキップ"
            elif passed is True:
                result_class = "passed-result"
                result_text = "合格"
            elif passed is False:
                result_class = "failed-result"
                result_text = "不合格"
            else:
                result_class = "error-result"
                result_text = "エラー"
            
            html += f"""
        <div class="detail-box">
            <h3>テスト #{i+1} - <span class="{result_class}">{result_text}</span></h3>
            <span class="category-badge">{category}</span>
            
            <div class="requirement">
                <strong>要件:</strong> {requirement}
            </div>
            
            <h4>敵対的プロンプト</h4>
            <div class="prompt">{prompt}</div>
            
            <h4>ターゲットAIの応答</h4>
            <div class="response">{target_response}</div>
            
            <h4>評価結果</h4>
            <div class="evaluation {result_class}">
                <p><strong>判定:</strong> {result_text}</p>
                <p><strong>理由:</strong> {reason}</p>
            </div>
        </div>
"""
        
        # End of HTML
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def generate_csv_report(results: List[Dict[str, Any]]) -> bytes:
        """評価結果からCSV形式のレポートを生成"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            "テスト番号", "カテゴリ", "要件", "敵対的プロンプト", 
            "ターゲットAIの応答", "判定", "理由", "スキップ"
        ])
        
        # Data row
        for i, result in enumerate(results):
            if result.get("evaluation", {}).get("skipped", False):
                status = "スキップ"
            elif result.get("evaluation", {}).get("passed") == True:
                status = "合格"
            elif result.get("evaluation", {}).get("passed") == False:
                status = "不合格"
            else:
                status = "エラー"
                
            writer.writerow([
                i+1,
                result.get("category", ""),
                result.get("requirement", ""),
                result.get("prompt", ""),
                result.get("target_response", ""),
                status,
                result.get("evaluation", {}).get("reason", ""),
                "はい" if result.get("evaluation", {}).get("skipped", False) else "いいえ"
            ])
        
        return output.getvalue().encode("utf-8-sig")  # UTF-8 with BOM for Excel compatibility

def setup_html_export_routes(app: FastAPI):
    """Set up HTML output routes for the FastAPI main app"""
    
    @app.get("/export/html/{session_id}")
    async def export_results_html(session_id: str, request: Request):
        """Export the evaluation results of the current session in HTML format"""
        from app import sessions  # Import here to avoid circular imports
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        session = sessions[session_id]
        
        if not session["evaluation_results"]:
            raise HTTPException(status_code=400, detail="評価結果がありません")
        
        html_content = HTMLExporter.generate_html_report(
            session["evaluation_results"], 
            session_id
        )
        
        headers = {
            'Content-Disposition': f'attachment; filename="evaluation_report_{session_id}.html"'
        }
        
        return HTMLResponse(content=html_content, headers=headers)
    
    @app.get("/export/csv/{session_id}")
    async def export_results_csv(session_id: str, request: Request):
        """Export the evaluation results of the current session in CSV format"""
        from app import sessions  # Import here to avoid circular imports
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        session = sessions[session_id]
        
        if not session["evaluation_results"]:
            raise HTTPException(status_code=400, detail="評価結果がありません")
        
        csv_content = HTMLExporter.generate_csv_report(session["evaluation_results"])
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="evaluation_report_{session_id}.csv"'
            }
        )
    
    @app.get("/export/html/file/{filename}")
    async def export_file_html(filename: str, request: Request):
        """Export saved evaluation results files in HTML format"""
        from results_manager import ResultsManager
        
        results_manager = ResultsManager()
        results = results_manager.get_result_by_filename(filename)
        
        if not results:
            raise HTTPException(status_code=404, detail="結果ファイルが見つかりません")
        
        # Extract session ID and timestamp from file name
        parts = filename.replace("evaluation_", "").replace(".json", "").split("_")
        session_id = parts[0]
        timestamp = "_".join(parts[1:]) if len(parts) > 1 else ""
        
        html_content = HTMLExporter.generate_html_report(
            results, 
            session_id,
            timestamp
        )
        
        headers = {
            'Content-Disposition': f'attachment; filename="evaluation_report_{filename.replace(".json", ".html")}"'
        }
        
        return HTMLResponse(content=html_content, headers=headers)
    
    @app.get("/export/csv/file/{filename}")
    async def export_file_csv(filename: str, request: Request):
        """Export saved evaluation results files in CSV format"""
        from results_manager import ResultsManager
        
        results_manager = ResultsManager()
        results = results_manager.get_result_by_filename(filename)
        
        if not results:
            raise HTTPException(status_code=404, detail="結果ファイルが見つかりません")
        
        csv_content = HTMLExporter.generate_csv_report(results)
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="evaluation_report_{filename.replace(".json", ".csv")}"'
            }
        )