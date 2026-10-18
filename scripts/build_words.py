"""끝말잇기 게임용 단어 파일(words.json)을 만든다.

사용법: python scripts/build_words.py
- data/stdict/*.xml   : 표준국어대사전 전체 내려받기 (일반어)
- data/opendict/*.xml : 우리말샘 전체 내려받기 (방언·북한어·옛말만 골라 씀)
- ../202610 korean word/words.json   : 기초 어휘 등급(1~4)과 쉬운 뜻
- ../202610 korean word/data/krdict  : 한국어기초사전 전체 내려받기

words.json 은 [단어, AI 단계, 뜻] 목록이다.
AI 단계: 1=기초 1~2등급, 2=3등급, 3=4등급, 4=한국어기초사전, 5=표준국어대사전,
         0=사람만 쓸 수 있음(고유명사·방언·북한어·옛말). 뜻은 기초 어휘에만 있다.
"""
import glob
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT.parent / "202610 korean word"
OUT = ROOT / "words.json"
PROPER = {"인명", "지명", "책명"}  # 표준국어대사전에서 고유명사로 보는 분야
OLD_TYPES = {"방언", "북한어", "옛말"}


def clean(word):
    """사전 표제어 표기 정리: '도매^물가-지수02' → '도매물가지수'. 두 글자 이상 현대 한글만 남긴다."""
    w = re.sub(r"[\-\^\s]|\d+$", "", word or "")
    return w if re.fullmatch(r"[가-힣]{2,}", w) else ""


def load_stdict():
    """표준국어대사전 명사를 {단어: 고유명사뿐인지} 로 모은다."""
    words = {}
    for path in sorted(glob.glob(str(ROOT / "data/stdict/*.xml"))):
        for _, el in ET.iterparse(path):
            if el.tag != "item":
                continue
            info = el.find("word_info")
            w = clean(info.findtext("word"))
            for pos in info.findall("pos_info"):
                if w and pos.findtext("pos") == "명사":
                    cats = [s.findtext("cat_info/cat") or "" for s in pos.iter("sense_info")]
                    proper = all(c in PROPER for c in cats)
                    words[w] = words.get(w, True) and proper
            el.clear()
    return words


def load_opendict():
    """우리말샘에서 방언·북한어·옛말 명사만 모은다."""
    words = set()
    for path in sorted(glob.glob(str(ROOT / "data/opendict/*.xml"))):
        for _, el in ET.iterparse(path):
            if el.tag != "item":
                continue
            sense = el.find("senseInfo")
            if sense is not None and sense.findtext("pos") == "명사" and sense.findtext("type") in OLD_TYPES:
                w = clean(el.findtext("wordInfo/word"))
                if w:
                    words.add(w)
            el.clear()
    return words


def load_krdict():
    """한국어기초사전 명사 목록."""
    words = set()
    for path in sorted(glob.glob(str(DICT / "data/krdict/*.xml"))):
        # 원본 일부 번역 문장에 XML에서 허용하지 않는 제어 문자가 섞여 있어 지우고 읽는다.
        data = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", Path(path).read_bytes())
        for _, el in ET.iterparse(io.BytesIO(data)):
            if el.tag != "LexicalEntry":
                continue
            lemma = el.find("Lemma/feat[@att='writtenForm']")
            pos = el.find("feat[@att='partOfSpeech']")
            if lemma is not None and pos is not None and pos.get("val") == "명사":
                w = clean(lemma.get("val"))
                if w:
                    words.add(w)
            el.clear()
    return words


def main():
    std = load_stdict()
    print("표준국어대사전 명사", len(std), flush=True)
    old = load_opendict()
    print("우리말샘 방언·북한어·옛말 명사", len(old), flush=True)
    kr = load_krdict()
    print("한국어기초사전 명사", len(kr), flush=True)
    basic = {w: (g, m) for w, g, m in json.loads((DICT / "words.json").read_text(encoding="utf-8"))}

    out = {}
    for w in old:
        out[w] = [w, 0, ""]
    for w, proper in std.items():
        out[w] = [w, 0 if proper else 5, ""]
    for w in kr:
        if not std.get(w):  # 표준국어대사전에 고유명사로만 실린 단어는 AI가 쓰지 않는다
            out[w] = [w, 4, ""]
    for w, (g, m) in basic.items():
        out[w] = [w, {1: 1, 2: 1, 3: 2, 4: 3}[g], m]

    rows = [out[w] for w in sorted(out)]
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    count = [sum(r[1] == lv for r in rows) for lv in range(6)]
    print("저장", len(rows), "단계별", count)


if __name__ == "__main__":
    main()
