from scholarly import scholarly
import json
from datetime import datetime
import os

# --- 核心修正 ---
# 獲取當前腳本 (main.py) 所在的目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
# 組合出正確的 results 資料夾路徑
results_dir = os.path.join(script_dir, 'results')
# -----------------

try:
    print("🚀 Starting scholar crawler")

    # 執行爬蟲
    author: dict = scholarly.search_author_id('ook-p6wAAAAJ')
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    name = author['name']
    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']:v for v in author['publications']}
    print("✅ Successfully fetched data for:", name)
    print(json.dumps(author, indent=2)) # 在 Action 中印出太多資訊可能會讓 Log 難以閱讀，建議移除或註解

    # 確保 results 資料夾存在 (會在 google_scholar_crawler/ 下建立)
    os.makedirs(results_dir, exist_ok=True)
    print(f"📂 Results directory '{results_dir}' is ready.")

    # --- 將結果寫入檔案 ---
    gs_data_path = os.path.join(results_dir, 'gs_data.json')
    with open(gs_data_path, 'w', encoding='utf-8') as outfile:
        json.dump(author, outfile, ensure_ascii=False, indent=2)
    print(f"📝 Wrote gs_data.json to {gs_data_path}")
    
    shieldio_data = {
      "schemaVersion": 1,
      "label": "citations",
      "message": f"{author['citedby']}",
    }
    
    gs_data_shieldsio_path = os.path.join(results_dir, 'gs_data_shieldsio.json')
    with open(gs_data_shieldsio_path, 'w', encoding='utf-8') as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False, indent=2)
    print(f"📝 Wrote gs_data_shieldsio.json to {gs_data_shieldsio_path}")

    print("✅ Crawler script finished successfully.")

except Exception as e:
    print(f"❌ An error occurred: {e}")
    exit(1)