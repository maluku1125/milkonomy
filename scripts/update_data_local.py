#!/usr/bin/env python3
"""
本地遊戲資料更新腳本（個人版）
不依賴 GitHub Actions / secrets，可直接在自己電腦執行。

用法（在專案根目錄）：
    python scripts/update_data_local.py

效果：
    從多個社群來源下載最新 Milky Way Idle 遊戲資料 JSON，
    寫入 public/data/data.json 與 public/data/market.json。
"""
import json
import os
import sys
import time
import urllib.request
from typing import Any, Optional

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "data")
GAME_DATA_TARGET = os.path.normpath(os.path.join(OUTPUT_DIR, "data.json"))
MARKET_DATA_TARGET = os.path.normpath(os.path.join(OUTPUT_DIR, "market.json"))

# 多源 fallback：依序嘗試，第一個成功就用
GAME_DATA_SOURCES = [
    # 官方端點（最即時；silent1b/MWIData 自 2025-08 起未再更新）
    "https://www.milkywayidle.com/game_data/init_client_info.json",
    # 多種可能的官方路徑（MWI 偶爾會微調命名）
    "https://www.milkywayidle.com/game_data/init_data.json",
    "https://www.milkywayidle.com/game_data/client_info.json",
    "https://www.milkywayidle.com/game_data/data.json",
    # 社群鏡像（fallback）
    "https://raw.githubusercontent.com/silent1b/MWIData/main/init_client_info.json",
    "https://raw.githubusercontent.com/holychikenz/MWIApi/main/milkyapi.json",
]

# 市場資料（官方端點 + 社群鏡像備援）
MARKET_DATA_SOURCES = [
    "https://www.milkywayidle.com/game_data/marketplace.json",
    "https://raw.githubusercontent.com/holychikenz/MWIApi/main/milkyapi.json",
]


def fetch(url: str, timeout: int = 30) -> Optional[dict[str, Any]]:
    """嘗試以 GET 抓取一個 JSON 資源；失敗時回傳 None。"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "milkonomy-personal/1.0 (local-update-script)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠ 失敗：{e}")
        return None


def fetch_first_ok(sources: list[str], label: str) -> Optional[dict[str, Any]]:
    """逐一嘗試 sources，回傳第一個成功的 JSON。"""
    for url in sources:
        print(f"  嘗試 {label}：{url}")
        t0 = time.time()
        data = fetch(url)
        if data is not None:
            elapsed = time.time() - t0
            size = len(json.dumps(data))
            print(f"    ✓ 成功（{elapsed:.1f}s, {size:,} bytes）")
            return data
    print(f"  ✗ 所有 {label} 來源都失敗")
    return None


def validate_game_data(data: dict[str, Any]) -> bool:
    """簡易 schema 驗證 game data。"""
    required = [
        "itemDetailMap",
        "actionDetailMap",
        "enhancementLevelSuccessRateTable",
        "communityBuffTypeDetailMap",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"  ✗ schema 不完整，缺少：{missing}")
        return False
    return True


def get_existing_version() -> str:
    if not os.path.exists(GAME_DATA_TARGET):
        return "(無舊版)"
    try:
        with open(GAME_DATA_TARGET, encoding="utf-8") as f:
            return json.load(f).get("gameVersion", "(未知)")
    except Exception:
        return "(舊版檔損毀)"


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    old_ver = get_existing_version()
    print(f"目前 public/data/data.json 版本：{old_ver}")
    print()

    print("[1/2] 抓取遊戲基礎資料…")
    game_data = fetch_first_ok(GAME_DATA_SOURCES, "game data")
    if game_data is None:
        print("\n失敗：無法取得遊戲基礎資料。請檢查網路或手動下載。")
        return 1
    if not validate_game_data(game_data):
        print("\n失敗：遊戲資料格式異常，未寫入。")
        return 1
    new_ver = game_data.get("gameVersion", "(未知)")
    print(f"  新版本：{new_ver}（舊：{old_ver}）")

    if new_ver == old_ver and "--force" not in sys.argv:
        print("  ↳ 版本相同，跳過寫入（如要強制覆寫，加 --force）")
    else:
        with open(GAME_DATA_TARGET, "w", encoding="utf-8") as f:
            json.dump(game_data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  ✓ 寫入 {GAME_DATA_TARGET}（{os.path.getsize(GAME_DATA_TARGET):,} bytes）")

    print()
    print("[2/2] 抓取市場行情資料…")
    market = fetch_first_ok(MARKET_DATA_SOURCES, "market")
    if market is None:
        print("  ⚠ 市場資料抓取失敗（不致命：執行時前端會直接打官方 API）")
    else:
        with open(MARKET_DATA_TARGET, "w", encoding="utf-8") as f:
            json.dump(market, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  ✓ 寫入 {MARKET_DATA_TARGET}（{os.path.getsize(MARKET_DATA_TARGET):,} bytes）")

    print()
    print("完成。下一步建議：")
    print("  1. pnpm dev 重新啟動，確認新物品有出現在排行")
    print("  2. 檢視 src/locales/lang/zh-tw.ts 是否有新增物品需要補翻譯")
    print("  3. git diff public/data/data.json | head 確認版本前進")
    return 0


if __name__ == "__main__":
    sys.exit(main())
