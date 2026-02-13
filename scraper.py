import requests
import pandas as pd
import time
import os

# --- 配置区 ---
BASE_URL = "https://cosylab.iiitd.edu.in/flavordb/entities_json?id="
SAVE_FILE = "flavordb_data.csv"
MAX_ID = 2600  # 设定上限
BATCH_SIZE = 20 # 每20个存档一次

def get_last_id():
    """检查进度：看看到底抓到哪了"""
    if os.path.exists(SAVE_FILE):
        try:
            df = pd.read_csv(SAVE_FILE)
            if not df.empty:
                return int(df['id'].max())
        except:
            return 0
    return 0

def run_scraper():
    last_id = get_last_id()
    start_id = last_id + 1
    
    # 加载已有数据
    if os.path.exists(SAVE_FILE):
        try:
            results = pd.read_csv(SAVE_FILE).to_dict('records')
        except:
            results = []
    else:
        results = []

    print(f"🔄 正在检查断点... 已完成至 ID {last_id}。准备从 {start_id} 开始捕捉！")

    if start_id > MAX_ID:
        print("✨ 恭喜！全量数据已抓取完毕。")
        return

    for i in range(start_id, MAX_ID + 1):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(f"{BASE_URL}{i}", timeout=15, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                molecules = data.get("molecules", [])
                
                # 提取细节
                flavor_set = set()
                molecule_names = []
                for m in molecules:
                    profiles = m.get("flavor_profile", "")
                    if profiles:
                        flavor_set.update(profiles.split("@"))
                    m_name = m.get("common_name")
                    if m_name:
                        molecule_names.append(m_name)
                
                # 这里就是你刚才报错的地方，这次我已经帮你完整闭合了
                results.append({
                    "id": i,
                    "name": data.get("entity_alias_readable", "Unknown"),
                    "category": data.get("category_readable", "Unknown"),
                    "flavors": ", ".join(sorted(list(flavor_set))),
                    "molecules_count": len(molecules),
                    "sample_molecules": ", ".join(molecule_names[:10])
                })
                print(f"✅ ID {i}: {data.get('entity_alias_readable', '未知')} | 分子数: {len(molecules)}")
            
            elif response.status_code == 404:
                print(f"⏩ ID {i}: 数据库空缺 (404)")
            
        except Exception as e:
            print(f"❌ ID {i} 发生故障: {e}")
            break 

        # 自动存档
        if i % BATCH_SIZE == 0:
            pd.DataFrame(results).to_csv(SAVE_FILE, index=False)
            print(f"💾 进度已安全存盘 (ID {i})")
            time.sleep(1)

    pd.DataFrame(results).to_csv(SAVE_FILE, index=False)
    print(f"🏁 捕捉任务结束。")

if __name__ == "__main__":
    run_scraper()
