# P07 綁帶綁定 — 交接狀態（2026-09-04）

## 目前狀態：綁定完成並已存回 `膠體內部_OPENING_P01_P03_v034.blend`（存回原檔，未另存）

## 待辦（下一個 session 第一件事）
1. 看 `VScode/tmp/p07_strap_rig/SHEET_belt_0.png` ~ `SHEET_belt_4.png`（共 60 格，來自
   `footages/R1 腰帶素材/R1 Belt.mp4`，1920x1080 / 734 frames）。
   原始影格在 `ref_belt60/`。運鏡概念參考在 `SHEET_dm1..5.png`（AI 生成，對應 P08 隧道段，非機構參考）。
2. 使用者回饋：**「機構做動還是有錯」**。要從 R1 Belt.mp4 確認真實機構：
   - 帶子從哪一端穿入？
   - 穿過哪一個孔／槽？
   - 卡扣如何咬合／鎖定？
   - 收緊的方向與行程？
3. 預期會改動的兩個決定（改動需重建，約 3 秒）：
   - **切口角度** `SPECS[0]["cutpt"]`（目前世界座標 (-0.248, -1.560)，換算成 116.2 度）
   - **哪一端是自由端**：目前 root = 切口，自由端 = 繞完一圈後回到切口前的那段（BUCKLE/ENTRY/END 控制）
4. 然後才做 1:16–1:24（frames 1824–2016）的機構動畫。使用者說第一幕先只有帶子，人體後面再結合。

## 場景
`05_SCN_P07_STRAP_RIG`，frames 1632–2160（1:08–1:30 @24fps）
markers: 1632 `P07_1_08_ROTATE_IN` / 1824 `P07_1_16_TWIST_LOCK_STRAP_THREAD` / 2016 `P07_1_24_HANDS_FREE` / 2160 `P07_1_30_END`
測試 pose A–D 在 frame 1–200（200 格回 REST，所以正式區間停在靜置）。
`P07_BODY_REF` 已 exclude + hide_render（第一幕只有帶子；人體整合時再打開）。

## 綁定內容
- 綁定基底＝**乾淨產品原型** `64.002` / `65.002`（不是貼身版 `P01_STRAP_*`；貼身版半徑差最大 0.164，
  把臀形烤進靜置造型，單獨一條帶子會很怪）。原始物件完全未修改。
- 上帶 `P07_STRAP_UPPER`：封閉環，在 116.2 度（卡扣蓋板 `60.002` 底下）切開。58 骨 = 24 DEF + 26 CP + 7 CTRL + MASTER。
- 下帶 `P07_STRAP_LOWER`：本來就是開口帶（自由端 68.5 / 111.0 度）。48 骨 = 24 DEF + 16 CP + 7 CTRL + MASTER。
- 語意控制：`ROOT / SIDE_A / MID / SIDE_B / BUCKLE / ENTRY / END`（每個底下掛數根 CP 骨）
- Spline IK：`y_scale_mode='BONE_ORIGINAL'`, `xz_scale_mode='NONE'`（不拉長、不縮寬）
- 全部 parent 到 `NITE_Strap_Rig_ROOT` 空物件。

## 重建指令（照順序）
```
cd VScode/tmp/p07_strap_rig
py -3 bmcp.py build_all2.py 1800   # 幾何 + 曲線 + 骨架 + 權重
py -3 bmcp.py b6b.py 1800          # 控制器外型 + 顏色 + parent
py -3 bmcp.py poses2.py 1800       # 測試 pose A-D
py -3 bmcp.py q11.py 1800          # 靜置還原驗證（應 < 0.0002）
py -3 bmcp.py qa2.py 1800          # 變形/拉伸/寬度/穿模/干涉
py -3 bmcp.py r2.py 1800           # QA 算圖
```

## 現況數據（乾淨原型版）
靜置還原 max 0.0001 ／ 拉直 pose 最大拉伸 20.2%、平均 0.66% ／ 帶寬 0.2323 固定 ／
裝置干涉在所有 pose 都低於靜置值。

## 已知陷阱（詳見記憶 project-p07-strap-rig）
- Bezier 一定要用 `AUTO` handle，`FREE` 會在擺 pose 時爆出尖點（曲率 78819 vs 70）。
- 切口接縫的頂點要用**網格連通性**分邊，不能用角度（角度只差浮點誤差 → 撕裂，平均拉伸 294%）。
- CAD 網格有無面的 wire edge，`split_edges` 對它們無效；量拉伸前要先濾掉。
- 變形骨 6–10 根不夠（扇貝狀波紋），用 24 根。
