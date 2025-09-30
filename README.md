# 📋 클립보드 이미지 자동 번역기

클립보드에 이미지를 복사하면 자동으로 **OCR → 번역 → 텍스트 변환**을 수행하는 프로그램입니다.

## ✨ 기능

- 📸 클립보드 이미지 자동 감지
- 🔍 OCR로 텍스트 추출 (한국어 + 영어)
- 🌐 자동 번역 (자동 언어 감지 → 한국어)
- 📋 번역 결과를 다시 클립보드에 복사

## 📦 설치 방법

### 1. Tesseract OCR 설치

1. [Tesseract OCR 다운로드](https://github.com/UB-Mannheim/tesseract/wiki)
2. Windows 설치 파일 다운로드: `tesseract-ocr-w64-setup-v5.x.x.exe`
3. 설치 시 **한국어(Korean) 언어 팩 포함** 선택
4. 기본 경로에 설치: `C:\Program Files\Tesseract-OCR\`

**또는 직접 다운로드:**
```
https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
```

### 2. Python 패키지 설치

```bash
pip install -r requirements.txt
```

## 🚀 사용 방법

### 방법 1: Python으로 직접 실행
```bash
python clipboard_translator.py
```

### 방법 2: 배치 파일로 실행
```bash
start.bat
```

## 💡 사용 예시

1. 프로그램 실행
2. 스크린샷을 찍거나 이미지를 복사 (Ctrl+C)
3. 자동으로 텍스트 추출 및 번역
4. 번역된 텍스트가 클립보드에 복사됨
5. 원하는 곳에 붙여넣기 (Ctrl+V)

## ⚙️ 설정 변경

`clipboard_translator.py` 파일의 `main()` 함수에서 언어 설정 가능:

```python
# 영어 → 한국어 번역
translator = ClipboardTranslator(source_lang='en', target_lang='ko')

# 일본어 → 한국어 번역
translator = ClipboardTranslator(source_lang='ja', target_lang='ko')

# 자동 감지 → 영어 번역
translator = ClipboardTranslator(source_lang='auto', target_lang='en')
```

### 지원 언어 코드
- `auto`: 자동 감지
- `ko`: 한국어
- `en`: 영어
- `ja`: 일본어
- `zh-cn`: 중국어 (간체)
- `zh-tw`: 중국어 (번체)
- `es`: 스페인어
- `fr`: 프랑스어
- `de`: 독일어

## 🛠️ 문제 해결

### "Tesseract를 찾을 수 없습니다" 오류

`clipboard_translator.py` 파일에서 Tesseract 경로 수정:

```python
# 경로 확인 후 수정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 한국어 인식이 안 됨

Tesseract 설치 시 한국어 언어 팩이 설치되지 않았을 수 있습니다.
[한국어 데이터 파일](https://github.com/tesseract-ocr/tessdata/blob/main/kor.traineddata) 다운로드 후
`C:\Program Files\Tesseract-OCR\tessdata\` 폴더에 복사하세요.

### 번역이 안 됨

인터넷 연결을 확인하세요. 번역은 Google Translate API를 사용하므로 인터넷이 필요합니다.

## 📝 요구사항

- Python 3.7 이상
- Windows 10/11
- 인터넷 연결 (번역 기능)
- Tesseract OCR 5.x

## 📄 라이선스

MIT License