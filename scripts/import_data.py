#!/usr/bin/env python3
"""
匯入手動從遊戲 WebSocket 攔截到的 init_client_info 到 public/data/data.json。

操作步驟（在 Chrome 內，登入後執行）：
  1. 開 https://www.milkywayidle.com 並登入
  2. F12 開啟 DevTools → 切到 Network 分頁
  3. 上方篩選器點 "WS"（WebSocket）
  4. 重新整理頁面（Ctrl+R）
  5. 點開那條 WebSocket 連線（通常名字像 game / connect.ws）
  6. 切到 "Messages" 子分頁
  7. 找第一筆「↓ 綠色箭頭」的 server 訊息（會是很長一串 JSON）
     - 內容開頭通常是 {"type":"init_client_data","gameVersion":"v1.2026...
  8. 右鍵 → Copy message → 貼到記事本
  9. 另存為 init.json（任何位置即可）
  10. 跑：python scripts/import_data.py 路徑\to\init.json

腳本會：
  - 驗證 JSON schema
  - 顯示新舊版本差異
  - 印出新增的 itemHrid / actionHrid
  - 詢問是否覆寫，確認後寫入 public/data/data.json
"""
import json
import os
import sys
from typing import Any

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "public", "data", "data.json")

REQUIRED_KEYS = [
    "itemDetailMap",
    "actionDetailMap",
    "enhancementLevelSuccessRateTable",
    "enhancementLevelTotalBonusMultiplierTable",
    "communityBuffTypeDetailMap",
]


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(data: dict[str, Any]) -> tuple[bool, list[str]]:
    errors = []
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        errors.append(f"缺少必要欄位：{missing}")
    if "itemDetailMap" in data:
        sample = next(iter(data["itemDetailMap"].values()), None)
        if sample is None or "name" not in sample or "hrid" not in sample:
            errors.append("itemDetailMap 結構異常（單一 item 缺 name/hrid）")
    return (not errors, errors)


def diff_summary(old: dict[str, Any] | None, new: dict[str, Any]) -> None:
    print()
    print(f"新版本：{new.get('gameVersion', '(未知)')}")
    if old is None:
        print("  （無舊版可比對）")
        return
    print(f"舊版本：{old.get('gameVersion', '(未知)')}")
    print()

    for label, key in [
        ("物品 (itemDetailMap)", "itemDetailMap"),
        ("動作 (actionDetailMap)", "actionDetailMap"),
        ("社群增益 (communityBuffTypeDetailMap)", "communityBuffTypeDetailMap"),
    ]:
        old_keys = set(old.get(key, {}).keys())
        new_keys = set(new.get(key, {}).keys())
        added = new_keys - old_keys
        removed = old_keys - new_keys
        print(f"{label}: 舊 {len(old_keys)} → 新 {len(new_keys)} (+{len(added)}/-{len(removed)})")
        if added and len(added) <= 30:
            print("   新增：")
            for k in sorted(added):
                name = new[key][k].get("name", "")
                print(f"     - {k}  {name}")
        elif added:
            print(f"   新增：（共 {len(added)} 個，前 15 個）")
            for k in sorted(added)[:15]:
                name = new[key][k].get("name", "")
                print(f"     - {k}  {name}")


def confirm(prompt: str) -> bool:
    try:
        return input(prompt + " [y/N] ").strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 1
    src_path = sys.argv[1]
    if not os.path.exists(src_path):
        print(f"找不到檔案：{src_path}")
        return 1

    print(f"讀取 {src_path}…")
    try:
        new_data = load_json(src_path)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗：{e}")
        print()
        print("提示：如果您是從 WebSocket Messages 複製的，貼到記事本時可能多了一層")
        print("     {\"type\":\"init_client_data\",\"data\":{...}} — 把外層拆掉只留 data 內容")
        return 1

    # 自動拆殼：若是 {type, data} 結構，取 data
    if isinstance(new_data, dict) and "type" in new_data and "data" in new_data and isinstance(new_data["data"], dict):
        if "itemDetailMap" in new_data["data"]:
            print("  ↳ 偵測到外殼結構 {type, data}，取出內層 data")
            new_data = new_data["data"]

    ok, errors = validate(new_data)
    if not ok:
        print("Schema 驗證失敗：")
        for e in errors:
            print(f"  - {e}")
        print("\n常見原因：複製的不是完整 init_client_data，可能只是某個子訊息")
        return 1
    print("  ✓ schema 驗證通過")

    old_data = None
    if os.path.exists(TARGET):
        try:
            old_data = load_json(TARGET)
        except Exception:
            pass

    diff_summary(old_data, new_data)

    print()
    if not confirm(f"確認寫入 {TARGET}？"):
        print("已取消，未寫入。")
        return 0

    with open(TARGET, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(TARGET)
    print(f"  ✓ 已寫入 {TARGET}（{size:,} bytes）")
    print()
    print("下一步：")
    print("  python scripts/sync_translations.py     # 自動補繁中翻譯")
    print("  pnpm dev                                # 重啟開發伺服器看新物品")
    return 0


if __name__ == "__main__":
    sys.exit(main())
