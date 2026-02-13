import requests
import pandas as pd
import time
import os

# --- 配置区 ---
BASE_URL = "https://cosylab.iiitd.edu.in/flavordb/entities_json?id="
SAVE_FILE = "flavordb_data.csv"
MAX_ID = 2600  # 设定一个较大的上限
BATCH_SIZE = 20 # 每抓20个存一次档

def get_last_id():
    """检查已保存的文件，获取最后一个 ID"""
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
    
    # 读取已有数据，如果没有则创建空列表
    if os.path.exists(SAVE_FILE):
        results = pd.read_csv(SAVE_FILE).to_dict('records')
    else:
        results = []

    print(f"🔄 检查进度：已完成至 ID {last_id}。准备从 {start_id} 开始...")

    if start_id > MAX_ID:
        print("✨ 所有数据已抓取完毕！")
        return

    for i in range(start_id, MAX_ID + 1):
        try:
            # 增加 headers 模拟浏览器，更安全
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(f"{BASE_URL}{i}", timeout=10, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # 核心字段提取
                results.append({
                    "id": i,
                    "name": data.get("entity_alias_readable", "Unknown"),
                    "category": data.get("category_readable", "Unknown"),
                    "flavors": ", ".join(set(m.get("flavor_profile", "") for m in data.get("molecules", []) if m.get("flavor_profile")))
                })
                print(f"✅ ID {i}: {data.get('entity_alias_readable', '未知食材')} 抓取成功！")
            elif response.status_code == 404:
                print(f"⏩ ID {i} 空缺 (404)")
            
        except Exception as e:
            print(f"❌ ID {i} 错误: {e}")
            break # 遇到严重错误（如断网）先停止，下次运行会自动重连

        # 分段保存
        if i % BATCH_SIZE == 0:
            pd.DataFrame(results).to_csv(SAVE_FILE, index=False)
            print(f"💾 进度已保存至 ID {i}")
            time.sleep(0.5) # 给服务器喘口气

    pd.DataFrame(results).to_csv(SAVE_FILE, index=False)
    print("🏁 本次抓取结束。")

if __name__ == "__main__":
    run_scraper()
