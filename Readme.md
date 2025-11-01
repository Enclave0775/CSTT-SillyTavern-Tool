# CSTT - SillyTavern 角色卡簡繁轉換工具

CSTT (Chinese Simplified to Traditional) 是一個專為 [SillyTavern](https://github.com/SillyTavern/SillyTavern) 用戶設計的 Python 命令列工具，用於批量將角色卡（PNG 檔）和對話記錄（JSON 檔）從簡體中文轉換為繁體中文。

此工具的核心功能是處理 SillyTavern 的角色卡，它能智慧地解析 PNG 檔中包含的角色資料。

- **JSON 文件**: 遞迴轉換檔中所有的字串值。
- **SillyTavern 角色卡 (PNG)**: 智慧識別並轉換圖片中繼資料（通常是 `tEXt` chunk）中的 Base64 編碼文本。程式會解碼 Base64 資料，將其中包含的簡體中文角色設定轉換為繁體中文，然後重新編碼回 Base64 並注入到新的 PNG 檔中。

## 功能特性

- **批量處理**: 自動處理 `original` 資料夾下的所有支援檔。
- **智慧角色卡轉換**: 專為 SillyTavern 角色卡優化。它能準確地從 PNG 中繼資料中提取 Base64 編碼的角色資料，進行簡繁轉換，然後安全地寫回新檔，同時保持圖片格式的完整性。
- **深度 JSON 轉換**: 遍歷整個 JSON 結構，無論是字典還是清單，將所有字串從簡體轉換為繁體。
- **Base64 支持**: 在處理 PNG 中繼資料時，能自動檢測並處理 Base64 編碼的文本。
- **簡單易用**: 只需將檔放入指定資料夾，運行一個命令即可完成所有轉換。

## 環境要求

- Python 3.x

## 安裝

1.  克隆或下載此項目。
2.  打開終端或命令列，進入專案根目錄。
3.  安裝所需的依賴庫：
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

1.  **準備文件**: 將需要轉換的 `.png` 或 `.json` 檔放入專案根目錄下的 `original` 資料夾中。如果該資料夾不存在，程式在首次運行時會自動創建。

2.  **運行腳本**: 在專案根目錄下打開終端或命令列，執行以下命令：
    ```bash
    python CSTT.py
    ```

3.  **獲取結果**: 轉換完成後，所有處理過的檔將以相同的檔案名保存在 `translated` 資料夾中。

## 資料夾結構

```
.
├── original/         # 存放待轉換的原始檔
├── translated/       # 存放轉換後的檔
├── CSTT.py           # 主程序腳本
├── requirements.txt  # 依賴庫列表
└── Readme.md         # 本說明文件
```

---