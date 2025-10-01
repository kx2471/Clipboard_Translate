#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clipboard Image to Translated Text Converter
클립보드에 이미지가 복사되면 자동으로 OCR → 번역 → 텍스트 변환
"""

import time
import io
import os
import sys
from pathlib import Path
from PIL import ImageGrab, Image
import pytesseract
from googletrans import Translator
import pyperclip
import threading
import keyboard

# Tesseract 경로 자동 감지
def find_tesseract():
    """Tesseract 실행 파일 경로를 자동으로 찾기"""
    # 1. 실행 파일과 같은 폴더의 tesseract 폴더 확인
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        base_path = Path(sys.executable).parent
    else:
        # 일반 Python 스크립트로 실행된 경우
        base_path = Path(__file__).parent

    # 실행 파일 위치의 tesseract 폴더
    local_tesseract = base_path / "tesseract" / "tesseract.exe"
    if local_tesseract.exists():
        return str(local_tesseract)

    # 2. 환경 변수에서 tesseract 찾기
    tesseract_cmd = os.getenv('TESSERACT_CMD')
    if tesseract_cmd and Path(tesseract_cmd).exists():
        return tesseract_cmd

    # 3. Windows 기본 설치 경로들 확인
    default_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        Path.home() / "AppData" / "Local" / "Tesseract-OCR" / "tesseract.exe",
    ]

    for path in default_paths:
        if Path(path).exists():
            return str(path)

    # 4. PATH 환경 변수에서 tesseract 찾기
    import shutil
    tesseract_in_path = shutil.which("tesseract")
    if tesseract_in_path:
        return tesseract_in_path

    # 찾지 못한 경우
    return None

# Tesseract 경로 설정
tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✓ Tesseract 경로: {tesseract_path}")
else:
    print("❌ Tesseract를 찾을 수 없습니다!")
    print("다음 중 하나를 수행하세요:")
    print("1. 실행 파일과 같은 폴더에 'tesseract' 폴더를 만들고 Tesseract를 설치")
    print("2. https://github.com/UB-Mannheim/tesseract/wiki 에서 Tesseract 설치")
    print("3. 환경 변수 TESSERACT_CMD에 tesseract.exe 경로 설정")
    input("\n아무 키나 눌러 종료...")
    sys.exit(1)

class ClipboardTranslator:
    def __init__(self, source_lang='auto', target_lang='ko'):
        """
        Args:
            source_lang: 원본 언어 (auto=자동감지, en=영어, ja=일본어 등)
            target_lang: 번역 대상 언어 (ko=한국어, en=영어 등)
        """
        self.translator = Translator()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.last_image = None
        self.last_text = None
        self.running = True
        self.ocr_only_mode = False  # F7: OCR 전용 모드
        self.ocr_translate_mode = True  # F8: OCR + 번역 모드 (기본값)
        self.paused = False  # F9: 일시정지 모드

        print("=" * 60)
        print("📋 클립보드 자동 번역기 시작!")
        print("=" * 60)
        print(f"원본 언어: {source_lang} → 번역 언어: {target_lang}")
        print("이미지 또는 텍스트를 클립보드에 복사하면 자동으로 번역됩니다.")
        print("\n⌨️  단축키:")
        print("  F7: OCR 전용 모드 ON/OFF (번역 없이 원본 텍스트만)")
        print("  F8: OCR + 번역 모드 ON/OFF (기본 모드)")
        print("  F9: 일시정지 / 재개")
        print("  Ctrl+C: 종료")
        print("=" * 60)

        # 단축키 리스너 등록
        keyboard.on_press_key('f7', self.toggle_ocr_only_mode)
        keyboard.on_press_key('f8', self.toggle_ocr_translate_mode)
        keyboard.on_press_key('f9', self.toggle_pause)

    def toggle_ocr_only_mode(self, event=None):
        """F7 키로 OCR 전용 모드 ON/OFF"""
        self.ocr_only_mode = not self.ocr_only_mode

        if self.ocr_only_mode:
            self.ocr_translate_mode = False  # 번역 모드 끄기
            print("\n🔍 F7: OCR 전용 모드 ON (원본 텍스트만 추출)")
        else:
            print("\n🔍 F7: OCR 전용 모드 OFF")

    def toggle_ocr_translate_mode(self, event=None):
        """F8 키로 OCR + 번역 모드 ON/OFF"""
        self.ocr_translate_mode = not self.ocr_translate_mode

        if self.ocr_translate_mode:
            self.ocr_only_mode = False  # OCR 전용 모드 끄기
            print("\n🌐 F8: OCR + 번역 모드 ON")
        else:
            print("\n🌐 F8: OCR + 번역 모드 OFF")

    def toggle_pause(self, event=None):
        """F9 키로 일시정지/재개 토글"""
        self.paused = not self.paused
        if self.paused:
            print("\n⏸️  F9: 일시정지 (F9를 다시 눌러 재개)")
        else:
            print("\n▶️  F9: 재개")

    def extract_text_from_image(self, image):
        """이미지에서 텍스트 추출 (OCR)"""
        try:
            # Tesseract OCR 실행 (한국어+영어 인식)
            text = pytesseract.image_to_string(image, lang='kor+eng')
            return text.strip()
        except Exception as e:
            print(f"❌ OCR 오류: {e}")
            return None

    def smart_text_merge(self, text):
        """OCR 텍스트의 줄바꿈을 스마트하게 병합"""
        if not text:
            return text

        lines = text.split('\n')
        merged_paragraphs = []
        current_paragraph = []

        for line in lines:
            line = line.strip()

            # 빈 줄은 문단 구분자
            if not line:
                if current_paragraph:
                    merged_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                continue

            # 이전 줄이 문장 종결 부호로 끝나면 새 문단 시작
            if current_paragraph:
                last_line = current_paragraph[-1]
                # 문장 종결 부호: . ! ? 。 ! ? (영어/한국어/일본어)
                if last_line and last_line[-1] in '.!?。!?':
                    merged_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = [line]
                else:
                    # 같은 문단으로 병합
                    current_paragraph.append(line)
            else:
                current_paragraph.append(line)

        # 마지막 문단 추가
        if current_paragraph:
            merged_paragraphs.append(' '.join(current_paragraph))

        # 문단들을 두 줄바꿈으로 구분
        return '\n\n'.join(merged_paragraphs)

    def convert_to_formal_style(self, text):
        """번역된 텍스트를 명사형 종결(~확인, ~수정)로 변환"""
        if not text:
            return text

        # 존댓말 → 명사형 변환 규칙
        replacements = [
            # ~해야 합니다 → ~요망/필요
            ('해야 합니다', '요망'),
            ('해야 했습니다', '필요했음'),
            ('해야 함', '요망'),

            # ~을/를 확인합니다 → ~확인
            ('을 확인합니다', '확인'),
            ('를 확인합니다', '확인'),
            ('확인합니다', '확인'),
            ('확인해야 합니다', '확인 요망'),

            # ~을/를 제거합니다 → ~제거
            ('을 제거합니다', '제거'),
            ('를 제거합니다', '제거'),
            ('제거합니다', '제거'),
            ('제거해야 합니다', '제거 요망'),

            # ~을/를 수정합니다 → ~수정
            ('을 수정합니다', '수정'),
            ('를 수정합니다', '수정'),
            ('수정합니다', '수정'),
            ('수정해야 합니다', '수정 요망'),

            # ~을/를 추가합니다 → ~추가
            ('을 추가합니다', '추가'),
            ('를 추가합니다', '추가'),
            ('추가합니다', '추가'),
            ('추가해야 합니다', '추가 요망'),

            # ~을/를 삭제합니다 → ~삭제
            ('을 삭제합니다', '삭제'),
            ('를 삭제합니다', '삭제'),
            ('삭제합니다', '삭제'),

            # ~을/를 변경합니다 → ~변경
            ('을 변경합니다', '변경'),
            ('를 변경합니다', '변경'),
            ('변경합니다', '변경'),

            # ~을/를 업데이트합니다 → ~업데이트
            ('을 업데이트합니다', '업데이트'),
            ('를 업데이트합니다', '업데이트'),
            ('업데이트합니다', '업데이트'),

            # ~을/를 실행합니다 → ~실행
            ('을 실행합니다', '실행'),
            ('를 실행합니다', '실행'),
            ('실행합니다', '실행'),

            # ~을/를 사용합니다 → ~사용
            ('을 사용합니다', '사용'),
            ('를 사용합니다', '사용'),
            ('사용합니다', '사용'),

            # ~을/를 입력합니다 → ~입력
            ('을 입력합니다', '입력'),
            ('를 입력합니다', '입력'),
            ('입력합니다', '입력'),

            # ~을/를 선택합니다 → ~선택
            ('을 선택합니다', '선택'),
            ('를 선택합니다', '선택'),
            ('선택합니다', '선택'),

            # 일반 동사 패턴
            ('합니다.', '.'),
            ('합니다', ''),
            ('했습니다.', '했음.'),
            ('했습니다', '했음'),
            ('없었습니다.', '없음.'),
            ('없었습니다', '없음'),
            ('있었습니다.', '있었음.'),
            ('있었습니다', '있었음'),

            # ~됩니다 → ~됨
            ('됩니다.', '됨.'),
            ('됩니다', '됨'),
            ('되었습니다', '되었음'),
            ('됐습니다', '됐음'),

            # ~입니다 → ~임
            ('입니다.', '임.'),
            ('입니다', '임'),
            ('이었습니다', '이었음'),
            ('였습니다', '였음'),

            # ~있습니다 → ~있음
            ('있습니다', '있음'),
            ('없습니다', '없음'),

            # ~수 있습니다 → ~가능
            ('수 있습니다', '가능'),
            ('수 없습니다', '불가능'),
            ('할 수 있습니다', '가능'),
            ('할 수 없습니다', '불가능'),

            # 기타 일반 패턴
            ('ㅂ니다.', '.'),
            ('ㅂ니다', ''),
            ('습니다.', '.'),
            ('습니다', ''),
        ]

        result = text
        for old, new in replacements:
            result = result.replace(old, new)

        return result

    def translate_text(self, text):
        """텍스트 번역"""
        if not text:
            return None

        try:
            result = self.translator.translate(
                text,
                src=self.source_lang,
                dest=self.target_lang
            )

            # 격식체로 변환
            formal_text = self.convert_to_formal_style(result.text)
            return formal_text

        except Exception as e:
            print(f"❌ 번역 오류: {e}")
            return None

    def process_clipboard_text(self):
        """클립보드의 텍스트 처리"""
        try:
            # 클립보드에서 텍스트 가져오기
            clipboard_text = pyperclip.paste()

            if not clipboard_text or not clipboard_text.strip():
                return False

            # 같은 텍스트인지 확인 (중복 처리 방지)
            if self.last_text == clipboard_text:
                return False

            self.last_text = clipboard_text

            print("\n" + "─" * 60)
            print("📝 새 텍스트 감지!")
            print(f"\n원본 텍스트:\n{clipboard_text}")
            print("\n🌐 번역 중...")

            # 텍스트 번역
            translated_text = self.translate_text(clipboard_text)

            if translated_text:
                print(f"\n번역된 텍스트:\n{translated_text}")

                # 번역된 텍스트를 클립보드에 복사
                pyperclip.copy(translated_text)
                self.last_text = translated_text  # 번역 결과도 중복 방지에 추가
                print("\n✅ 번역된 텍스트가 클립보드에 복사되었습니다!")

            print("─" * 60)
            return True

        except Exception as e:
            # 조용히 실패 (텍스트가 없는 경우는 정상)
            return False

    def process_clipboard_image(self):
        """클립보드의 이미지 처리"""
        try:
            # 클립보드에서 이미지 가져오기
            image = ImageGrab.grabclipboard()

            if image is None:
                return False

            # 같은 이미지인지 확인 (중복 처리 방지)
            if self.last_image is not None:
                if self.images_are_equal(image, self.last_image):
                    return False

            self.last_image = image.copy()

            print("\n" + "─" * 60)
            print("🖼️  새 이미지 감지!")
            print("📝 텍스트 추출 중...")

            # OCR로 텍스트 추출
            extracted_text = self.extract_text_from_image(image)

            if not extracted_text:
                print("⚠️  텍스트를 찾을 수 없습니다.")
                return False

            # OCR 전용 모드 (F7)
            if self.ocr_only_mode:
                print(f"\n🔍 추출된 원본 텍스트:\n{extracted_text}")

                # 원본 텍스트를 클립보드에 복사
                pyperclip.copy(extracted_text)
                self.last_text = extracted_text
                print("\n✅ 원본 텍스트가 클립보드에 복사되었습니다!")
                print("─" * 60)
                return True

            # OCR + 번역 모드 (F8)
            if self.ocr_translate_mode:
                # 줄바꿈 스마트 병합
                merged_text = self.smart_text_merge(extracted_text)

                print(f"\n원본 텍스트 (OCR):\n{extracted_text}")
                print(f"\n정리된 텍스트:\n{merged_text}")
                print("\n🌐 번역 중...")

                # 텍스트 번역
                translated_text = self.translate_text(merged_text)

                if translated_text:
                    print(f"\n번역된 텍스트:\n{translated_text}")

                    # 번역된 텍스트를 클립보드에 복사
                    pyperclip.copy(translated_text)
                    self.last_text = translated_text  # 번역 결과도 중복 방지에 추가
                    print("\n✅ 번역된 텍스트가 클립보드에 복사되었습니다!")

                print("─" * 60)
                return True

            # 모든 모드가 OFF인 경우
            print("\n⚠️  모든 모드가 꺼져 있습니다. F7 또는 F8을 눌러 모드를 활성화하세요.")
            print("─" * 60)
            return False

        except Exception as e:
            print(f"❌ 처리 오류: {e}")
            return False

    def images_are_equal(self, img1, img2):
        """두 이미지가 같은지 비교"""
        try:
            return list(img1.getdata()) == list(img2.getdata())
        except:
            return False

    def monitor_clipboard(self):
        """클립보드 모니터링 (메인 루프)"""
        print("\n⏳ 클립보드 모니터링 중...\n")

        while self.running:
            try:
                # 일시정지 상태가 아닐 때만 처리
                if not self.paused:
                    # 이미지 먼저 확인
                    image_processed = self.process_clipboard_image()

                    # 이미지가 없으면 텍스트 확인
                    if not image_processed:
                        self.process_clipboard_text()

                time.sleep(0.5)  # 0.5초마다 체크
            except KeyboardInterrupt:
                print("\n\n👋 프로그램을 종료합니다.")
                self.running = False
                break
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(1)


def main():
    """메인 함수"""
    # 언어 설정 (필요시 변경)
    # source_lang: 'auto'(자동), 'en'(영어), 'ja'(일본어), 'zh-cn'(중국어 간체) 등
    # target_lang: 'ko'(한국어), 'en'(영어) 등

    translator = ClipboardTranslator(source_lang='auto', target_lang='ko')
    translator.monitor_clipboard()


if __name__ == "__main__":
    main()