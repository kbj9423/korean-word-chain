"""낱말 뜻 묶음 파일(meanings/*.json)을 만든다.

사용법: python scripts/build_meanings.py  (words.json 을 먼저 만든 뒤)
- words.json 에 뜻이 없는 낱말의 뜻을 표준국어대사전에서, 없으면 우리말샘에서 가져온다.
- 낱말마다 bucket() 으로 정한 번호의 파일(meanings/번호.json, {낱말: 뜻})에 나눠 담는다.
  게임은 화면에 낱말이 나올 때 같은 계산으로 그 파일 하나만 받는다(index.html 의 bucket 과 같아야 함).
"""
import glob
import html
import json
import re
import xml.etree.ElementTree as ET

from build_words import ROOT, clean

OUT = ROOT / "meanings"
BUCKETS = 509  # 소수로 해야 파일마다 낱말 수가 고르게 나뉜다


def bucket(word):
    h = 0
    for ch in word:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % BUCKETS


def tidy(text):
    """사전 편집용 표시(<sp_no>, <sub>, &#x..; 등)를 걷어 내고 글자만 남긴다. <현악 영산회상> 같은 한글 꺾쇠는 둔다."""
    text = re.sub(r"<(sp_no|each_sense_no)>.*?</\1>", "", text)
    text = re.sub(r"</?[A-Za-z][^>]*>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def main():
    need = {w for w, lv, m in json.loads((ROOT / "words.json").read_text(encoding="utf-8")) if not m}
    defs = {}
    for path in sorted(glob.glob(str(ROOT / "data/stdict/*.xml"))):
        for _, el in ET.iterparse(path):
            if el.tag != "item":
                continue
            info = el.find("word_info")
            w = clean(info.findtext("word"))
            if w in need and w not in defs:
                for pos in info.findall("pos_info"):
                    d = pos.findtext(".//sense_info/definition") if pos.findtext("pos") == "명사" else None
                    if d and tidy(d):
                        defs[w] = tidy(d)
                        break
            el.clear()
    print("표준국어대사전에서", len(defs), flush=True)
    for path in sorted(glob.glob(str(ROOT / "data/opendict/*.xml"))):
        for _, el in ET.iterparse(path):
            if el.tag != "item":
                continue
            sense = el.find("senseInfo")
            if sense is not None and sense.findtext("pos") == "명사":
                w = clean(el.findtext("wordInfo/word"))
                d = tidy(sense.findtext("definition") or "")
                if w in need and w not in defs and d:
                    defs[w] = d
            el.clear()
    print("뜻 찾음", len(defs), "/", len(need), flush=True)

    groups = [{} for _ in range(BUCKETS)]
    for w in sorted(defs):
        groups[bucket(w)][w] = defs[w]
    OUT.mkdir(exist_ok=True)
    for i, g in enumerate(groups):
        (OUT / f"{i}.json").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    sizes = [len(g) for g in groups]
    print("저장", BUCKETS, "개 파일, 파일당 낱말", min(sizes), "~", max(sizes))


if __name__ == "__main__":
    main()
