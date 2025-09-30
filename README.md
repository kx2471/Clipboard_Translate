# 📋 클립보드 자동 번역기

클립보드에 **이미지 또는 텍스트**를 복사하면 자동으로 번역하는 프로그램입니다.

## ✨ 주요 기능

- 📸 **이미지 자동 번역**: 클립보드 이미지를 OCR로 텍스트 추출 후 번역
- 📝 **텍스트 자동 번역**: 클립보드에 복사된 텍스트를 즉시 번역
- 🔍 **OCR 전용 모드**: F7 키로 번역 없이 원본 텍스트만 추출
- 🔗 **스마트 병합**: OCR 결과의 줄바꿈을 지능적으로 병합하여 자연스러운 문장 생성
- 📋 **명사형 출력**: 기술 문서 스타일의 간결한 명사형 종결 (~확인, ~수정, ~요망)
- ⌨️ **다중 모드 지원**: F7(OCR 전용), F8(OCR+번역), F9(일시정지)
- 🌐 **다국어 지원**: 자동 언어 감지 및 다양한 언어 번역

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

### 이미지 번역
1. 프로그램 실행
2. 스크린샷 찍기 (Win+Shift+S) 또는 이미지 복사
3. 자동으로 OCR → 번역
4. 번역된 텍스트가 클립보드에 복사됨
5. Ctrl+V로 붙여넣기

### 텍스트 번역
1. 프로그램 실행
2. 영어 텍스트 복사 (Ctrl+C)
3. 자동으로 번역
4. 번역된 텍스트가 클립보드에 복사됨
5. Ctrl+V로 붙여넣기

### 단축키
- **F7**: OCR 전용 모드 ON/OFF (번역 없이 원본 텍스트만 추출)
- **F8**: OCR + 번역 모드 ON/OFF (기본 모드)
- **F9**: 일시정지 / 재개
- **Ctrl+C**: 프로그램 종료

#### 모드 설명
- **F7 모드**: 이미지에서 추출한 원본 텍스트를 그대로 클립보드에 복사 (번역 안 함)
- **F8 모드**: 이미지에서 텍스트 추출 후 자동으로 번역 (기본값)
- **F9 모드**: 클립보드 모니터링을 일시정지 (F7/F8 설정은 유지됨)
- F7과 F8은 상호 배타적 (하나 켜면 다른 하나 자동으로 꺼짐)
- 두 모드 모두 OFF 가능 (아무 동작도 안 함)

### 번역 예시
```
원본: "Check that unused input/output driver shall be removed"
번역: "사용하지 않는 입출력 드라이버 제거 요망"
```

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

## 🔧 기술 스택

- **OCR**: Tesseract OCR (한국어 + 영어)
- **번역**: Google Translate API
- **클립보드**: pyperclip, PIL ImageGrab
- **단축키**: keyboard 라이브러리

## 📄 라이선스

MIT License