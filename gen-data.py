#!/usr/bin/env python3
"""実践5アプリのVault索引データを再生成する。

  python3 gen-data.py

出力:
  unchiku-data.js  … うんちくDB一覧(🗣️うんちく枠の出題元)
  notes-data.js    … Books/D-Lab/TAKAHIRO のノート一覧(学びメモの出典ピッカー用)

ノートを増やしたら再実行し、sw.js の版数を上げて git push する。
"""
import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parent
RESEARCH = APP.parents[2] / "02_Research"   # うるトトの思考/02_Research

GROUPS = [
    ("Books/2_読書メモ", "読書メモ"),
    ("Books/01_読書", "読書"),
    ("Books/読書法", "読書法"),
    ("Books", "Books"),
    ("D-Lab/メンタルブログ", "メンタルブログ"),
    ("D-Lab/動画", "Dラボ動画"),
    ("D-Lab/つっしー", "つっしー"),
    ("D-Lab/パレオ", "パレオ"),
    ("D-Lab/🔻成功ルート🐈", "成功ルート"),
    ("D-Lab", "D-Lab"),
    ("TAKAHIRO", "TAKAHIRO"),
]


def clean_title(stem: str) -> str:
    """ファイル名を出典として読みやすいタイトルに整える。

    連番は「12 【書名】…」「56_…」の形のときだけ外す。
    「1.45倍モテるLINEの使い方」のように数字で始まる本文タイトルは削らない。
    """
    t = stem.strip()
    t = re.sub(r"^【本文】", "", t)
    m = re.match(r"^[\d\s　、,\.]+(?=【書名】)", t)   # 「5、6  【書名】…」の連番
    if m:
        t = t[m.end():]
    t = re.sub(r"^【書名】", "", t)
    t = re.sub(r"^\d+_", "", t)                      # 「56_バレットジャーナル」の連番
    t = t.strip()
    t = re.sub(r"^[『「]", "", t)
    t = re.sub(r"[』」]$", "", t)
    return t.strip() or stem


def group_of(rel: str) -> str:
    for prefix, label in GROUPS:
        if rel == prefix or rel.startswith(prefix + "/"):
            return label
    return ""


def gen_unchiku() -> int:
    d = RESEARCH / "うんちくDB"
    items = [{"t": p.stem, "p": f"02_Research/うんちくDB/{p.stem}"}
             for p in sorted(d.glob("*.md"))]
    (APP / "unchiku-data.js").write_text(
        "const UNCHIKU = " + json.dumps(items, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8")
    return len(items)


def gen_notes() -> int:
    items, seen = [], set()
    for folder in ("Books", "D-Lab", "TAKAHIRO"):
        root = RESEARCH / folder
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            rel_dir = p.parent.relative_to(RESEARCH).as_posix()
            path = "02_Research/" + p.relative_to(RESEARCH).with_suffix("").as_posix()
            if path in seen:
                continue
            seen.add(path)
            items.append({"t": clean_title(p.stem), "p": path, "g": group_of(rel_dir)})
    items.sort(key=lambda x: x["t"])
    (APP / "notes-data.js").write_text(
        "/* 出典ピッカー用のVaultノート索引。gen-data.py で再生成する。 */\n"
        "const SRCNOTES = " + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    return len(items)


if __name__ == "__main__":
    print(f"unchiku-data.js: {gen_unchiku()} 件")
    print(f"notes-data.js  : {gen_notes()} 件")
