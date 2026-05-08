<div align="center">
  <img alt="logo" width="120" height="120" src="./src/common/assets/images/layouts/logo.png">
  <h1>Milkonomy（個人精簡版）</h1>
</div>

## 介紹

牛牛放置（Milky Way Idle）利潤計算工具。

本版本 fork 自 [luyh7/milkonomy](https://github.com/luyh7/milkonomy)，
僅保留 **首頁（利潤排行）**、**強化計算**、**強化分解** 三個頁面，
其餘功能（英靈殿、埋骨地、打賞、打野系列、繼承、分解、撿漏、製作煉金、超級強化系列、Demo）已移除。

## 開發

```bash
pnpm install
pnpm dev          # 啟動開發伺服器（公開版模式）
pnpm build        # 建置正式版
```

## 資料來源

- 遊戲基礎資料：`public/data/data.json`（v1.20250818.0；後續可手動 / Actions 更新）
- 市場行情：執行時直接打官方 API `https://www.milkywayidle.com/game_data/marketplace.json`

## 許可

[MIT](./LICENSE) License

- 原作者 © 2025 [luyh7](https://github.com/luyh7)
- 個人 fork 維護：[maluku1125](https://github.com/maluku1125)
