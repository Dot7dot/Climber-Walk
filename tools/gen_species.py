#!/usr/bin/env python3
"""Generate the embedded 太平山圖鑑 species table for src/game.html.

Reads guide/species.json from Dot7dot/Creature-Collection-Guy-CCG (animals & insects only)
and rewrites the `const SPECIES=`...`;//@species` line in src/game.html.
Only factual fields are embedded (names, taxonomy, status, observation counts);
body plan, size and colours are assigned here for the procedural 3D models.

usage: python3 tools/gen_species.py /path/to/creature-collection-guy-ccg/guide/species.json
"""
import json, re, sys, hashlib, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'game.html'
sp = json.load(open(sys.argv[1], encoding='utf-8'))['species']
sp = [s for s in sp if s['category'] != 'plant']

GROUP = {'鳥類': 'b', '哺乳類': 'm', '爬蟲類': 'r', '兩棲類': 'a', '蜘蛛類': 's', '蝴蝶': 'u', '蛾': 'o',
         '甲蟲': 'c', '蜻蜓豆娘': 'd', '蟬與椿象': 'k', '蜂與螞蟻': 'h', '其他昆蟲': 'i', '蝗蟲與螽斯': 'i'}
STATUS = {'臺灣特有': 'E', '第一級保育類': '1', '第二級保育類': '2', '第三級保育類': '3', 'IUCN 易危': 'V',
          'IUCN 瀕危': 'N', '外來種': 'X', '國家易危': 'Y', '國家極危': 'Z'}

def arche(s):
    g, z = s['group'], s['zh']
    has = lambda *k: any(x in z for x in k)
    if g == '鳥類':
        if has('鴞', '鵂鶹', '夜鷹'): return 'Bo'
        if has('鷴', '雉', '竹雞', '鷓鴣'): return 'Bp'
        if has('鵰', '鷲', '鵟', '鷹'): return 'Br'
        if has('燕'): return 'Bs'
        if has('鷺'): return 'Bw'
        return 'B'
    if g == '哺乳類':
        if has('獼猴'): return 'Mm'
        if has('松鼠'): return 'Ms'
        if has('鼯鼠'): return 'Mf'
        if has('蝠'): return 'Mb'
        return 'M'
    if g == '爬蟲類': return 'L' if has('石龍子', '蜓蜥', '蝎虎') else 'S'
    if g == '兩棲類': return 'F'
    if g == '蜘蛛類': return 'R'
    return {'蝴蝶': 'U', '蛾': 'O', '甲蟲': 'C', '蜻蜓豆娘': 'D', '蟬與椿象': 'K', '蜂與螞蟻': 'A'}.get(g, 'P')

def night(s, a):
    z = s['zh']
    if a in ('Bo', 'Mf', 'Mb') or any(k in z for k in ('白鼻心', '鼬貛')): return 'n'
    if a == 'O': return 'd' if '斑蛾' in z else 'n'
    if a in ('F', 'S', 'R', 'M', 'C', 'L') and '石龍子' not in z: return 'b'
    return 'd'

# [body, accent, extra] colours, optional size multiplier, wing/marking pattern
C = {
 # birds
 '臺灣噪眉': ('8a7f5c', 'd9a92e', '6e3b22'), '東方毛腳燕': ('1f2a44', 'f2f0ea', '1f2a44'), '白尾海鵰': ('5a4330', 'f4f0e6', 'e2c24a', 1.5),
 '東方灰林鴞': ('7a6a58', 'b8a68c', '4a3a2c'), '藍腹鷴': ('243a78', 'f2f2f2', 'd8262c', 1.2), '黑長尾雉': ('1c2240', 'f2f2f2', 'd8262c', 1.3),
 '冠羽畫眉': ('8c7458', 'e9e2d2', '5a4632'), '黃腹琉璃': ('2c4fa0', 'f2c230', '1d3070'), '紅尾鶲': ('7a6e60', 'c86a2c', 'e8e2d4'),
 '黃胸藪眉': ('6e7a40', 'e6b830', '3a3a30'), '白耳畫眉': ('4a4038', 'c87a3a', 'f2f2ee'), '棕面鶯': ('6a8040', 'e8d870', 'b06a30'),
 '紅頭山雀': ('6a7078', 'f2f0ea', 'c8502c'), '臺灣紫嘯鶇': ('2a2e6a', '4a5ab8', '15172e', 1.3), '巨嘴鴉': ('141416', '1e2028', '0c0c0e', 1.6),
 '白鶺鴒': ('3a3a3e', 'f4f4f2', '141416'), '紋翼畫眉': ('8a7050', 'd8ccb8', '3a3028'), '臺灣藍鵲': ('2a58b8', 'f2f2f2', '141418', 1.4),
 '小鶯': ('7a6a4a', 'd8ccaa', '6a5a40'), '大冠鷲': ('4a3426', 'e8e2d0', 'e8c032', 1.6), '棕噪眉': ('8a5a3a', 'c88a5a', '3a2a20'),
 '臺灣鷦眉': ('6a4a30', 'e8e0d0', '4a3424'), '五色鳥': ('3a8a3a', 'e8c830', 'd83a2a'), '山紅頭': ('8a7a50', 'e8d8a0', 'c8602c'),
 '樹鵲': ('6a4a3a', 'b8b8b8', '1a1a1a', 1.3), '黃胸青鶲': ('3a4a60', 'f2c030', '2a3048'), '小彎嘴': ('7a5a3a', 'f2f0ea', '3a2a20'),
 '灰鶺鴒': ('6a7078', 'f0d040', '2a2a2a'), '紅嘴黑鵯': ('2a2a2e', '3a3a40', 'd8262c'), '臺灣朱雀': ('b8384a', 'd86a7a', '6a3a3a'),
 '鵂鶹': ('6a503a', 'd8c8a8', 'f0d040', .8), '黃嘴角鴞': ('8a6a40', 'c8a870', 'f0d040', .9), '大彎嘴': ('7a5034', 'f2f0ea', '2a1a14', 1.2),
 '栗背林鴝': ('8a3a20', 'b8c0c8', '2a2a2e'), '火冠戴菊鳥': ('5a7038', 'e8d8a0', 'f0782a', .8), '灰頭黑臉鵐': ('6a7038', 'e8d870', '3a3a3a'),
 '白氏地鶇': ('6a5a40', 'e8dcc0', '2a2018', 1.3), '紅尾伯勞': ('8a6040', 'f0e8d8', '1a1a1a'), '綠畫眉': ('6a8a3a', 'f2f0ea', '3a3a3a'),
 '花雀': ('c87a3a', 'f0e0c0', '1a1a1a'), '褐鷽': ('8a6a50', 'c8a890', '2a2a2a'), '黃羽鸚嘴': ('c8a030', 'e8d080', '8a6a20'),
 '南亞夜鷹': ('6a5a48', 'a89878', '3a3028'), '大卷尾': ('141418', '1a1e2a', '0c0c0e', 1.2), '小卷尾': ('1a1e2a', '2a3048', '0c0c0e'),
 '大白鷺': ('f4f4f0', 'f4f4f0', 'e8c030', 1.5), '小白鷺': ('f4f4f0', 'f4f4f0', '1a1a1a', 1.1), '蒼鷺': ('8a9098', 'e8e8e8', '1a1a1a', 1.5),
 '朱鸝': ('c8202a', 'e83a3a', '1a1a1a', 1.2), '灰林鴿': ('6a6a78', '8a7a88', 'c8a0a0', 1.4), '野鴿': ('7a7a88', '6a8a7a', 'd88a8a', 1.4),
 '臺灣山鷓鴣': ('6a5a48', 'a8a8b0', 'e8d8c0', .7), '臺灣竹雞': ('6a5a40', 'c88a5a', '8a9098', .6), '藍尾鴝': ('3a5aa8', 'e8a050', 'f2f0ea'),
 '白尾鴝': ('2a3a6a', 'f2f2f2', '1a1a2a'), '鉛色水鶇': ('3a4a6a', 'c8402a', '2a3048'), '煤山雀': ('3a3a40', 'f2f2f0', '1a1a1a', .8),
 '繡眼畫眉': ('7a7a6a', 'e8e0d0', 'f2f2f2'), '虎斑地鶇': ('8a6a30', 'e8d8b0', '2a2018', 1.3), '烏灰鶇': ('4a4e58', 'f2f0ea', 'e8b030'),
 '金腰燕': ('1f2a44', 'e8c8b0', 'c8602a'), '歐洲小雨燕': ('2a2a2e', 'f2f2f2', '2a2a2e'), '灰面鵟鷹': ('6a4a36', 'e8e0d0', 'e8c030', 1.3),
 # mammals
 '臺灣獼猴': ('7a6a5a', 'a8988a', 'e8a090'), '臺灣山羌': ('8a4a28', 'c8805a', '2a1a14'), '條紋松鼠': ('6a5a44', 'e8dcc0', '2a2218'),
 '黃鼠狼': ('b8762a', 'e8c890', '6a3a1a'), '棕簑貓': ('6a5a4a', 'e8dcc0', '3a2e26'), '白面鼯鼠': ('6a4a34', 'f2eee6', '3a2a20'),
 '白鼻心': ('6a6058', 'f2f0ea', '1a1a1a'), '臺灣大蹄鼻蝠': ('5a4a3e', '7a6a5a', '3a2e26', 1.4), '臺灣小蹄鼻蝠': ('5a4a3e', '7a6a5a', '3a2e26'),
 '野豬': ('3a322c', '5a4a3e', '1a1614'), '鼬貛': ('6a6a62', 'f2f0ea', '2a2622'),
 # reptiles
 '麗紋石龍子': ('2a2a2e', 'e8d870', '3a6ad8'), '赤尾青竹絲': ('4aa040', 'e8e070', 'c8402a'), '玉斑錦蛇': ('8a8a8a', 'e8c030', '1a1a1a'),
 '白梅花蛇': ('2a2a2e', 'f2f2f0', '2a2a2e'), '呂賴氏蜓蜥': ('6a5a40', 'c8b080', '2a2a20'), '菊池氏龜殼花': ('6a5a40', 'a8885a', '2a2018'),
 '史丹吉氏斜鱗蛇': ('6a6a40', 'a8a060', '2a2a1a'), '標蛇': ('6a4a30', '8a6a4a', '2a1a14'), '紅竹蛇': ('a83a2a', 'e8d870', '2a1a14'),
 '過山刀': ('6a6a48', 'a89a6a', '2a2a1a', 1.3), '鉤盲蛇': ('2a2a2e', '4a4a52', '2a2a2e', .4), '大頭蛇': ('8a7a6a', 'c8b8a0', '3a2e26'),
 '斯文豪氏華珊瑚蛇': ('c84a2a', '1a1a1a', 'f2f0e0'), '無疣蝎虎': ('b8b0a0', 'd8d0c0', '8a8070'), '瑪家山龜殼花': ('6a5a40', 'a8885a', '2a2018'),
 '紅斑蛇': ('6a3a2a', 'c84a3a', '2a1a14'), '雨傘節': ('141416', 'f2f2f0', '141416'),
 # amphibians
 '太田樹蛙': ('7a6a3a', 'c8b878', '3a2e1a'), '莫氏樹蛙': ('3aa040', 'e8d870', 'c84a2a'), '周氏樹蛙': ('4aa84a', 'f2f0e0', '2a6a2a'),
 '盤古蟾蜍': ('6a5a40', '8a7a5a', '3a2e20', 1.4), '梭德氏赤蛙': ('8a6a40', 'c8a870', '3a2a1a'), '艾氏樹蛙': ('6a5a3a', 'a89a6a', '2a2a1a', .8),
 '拉都希氏赤蛙': ('6a6040', 'a89a6a', '3a3020'), '斯文豪氏赤蛙': ('4a6a3a', '8a8a5a', '2a2a1a'), '腹斑蛙': ('5a7a40', 'e8e0d0', '2a2a1a'),
 '面天樹蛙': ('8a7a5a', 'c8b890', '3a2e20', .7), '褐樹蛙': ('7a5a3a', 'c89a6a', '3a2a1a'),
 # butterflies
 '夸父璀灰蝶': ('3a8a7a', 'a8e0c8', '2a2a2a', 1, 'p'), '臺灣寬尾鳳蝶': ('1a1a1e', 'f2f0ea', 'd83a3a', 1.4, 'bt'), '深山黛眼蝶': ('6a5a44', 'c8b890', '1a1a1a', 1, 'e'),
 '木蘭青鳳蝶': ('1a1a1e', '7ad8a0', 'd83a3a', 1, 's'), '白帶波眼蝶': ('7a6a54', 'f2f0ea', '1a1a1a', .8, 'be'), '青鳳蝶': ('1a1a1e', '4ab8c8', '1a1a1e', 1, 'b'),
 '黑鳳蝶': ('141418', '2a2a3a', 'c83a3a', 1.4, 't'), '斐豹蛺蝶': ('e08a2a', '1a1a1a', 'f2f2f2', 1, 's'), '流星絹粉蝶': ('f2f0ea', '1a1a1a', 'e8e0b0', 1, 'v'),
 '玉帶黛眼蝶': ('5a4a38', 'f2f0ea', '1a1a1a', 1, 'be'), '眉眼蝶': ('7a6a54', 'c8b890', '1a1a1a', .8, 'e'), '密紋波眼蝶': ('8a7a60', 'd8c8a0', '1a1a1a', .7, 'e'),
 '東方喙蝶': ('6a4a2a', 'e08a2a', '2a1a14', .8, 'b'), '紅邊黃小灰蝶': ('e8b020', 'c83a2a', '2a2a2a', .6, 's'), '翠鳳蝶': ('1a2a2a', '3ac888', 'c83a5a', 1.5, 'bt'),
 '苧麻細蝶': ('e0802a', '1a1a1a', 'e8c050', .9, 'v'), '大紅蛺蝶': ('2a2018', 'e8502a', 'f2f2f2', 1, 'bs'), '琉璃蛺蝶': ('1a1a2a', '3a8ae0', 'f2f2f2', 1, 'b'),
 '細邊琉灰蝶': ('6a8ae0', 'c8d8f0', '2a2a2a', .6, 'p'), '緣點白粉蝶': ('f2f2ec', '2a2a2a', 'e8e0a0', 1, 's'), '台灣鳳蝶': ('1a1a1e', 'f2f0ea', 'c83a3a', 1.4, 'bt'),
 '異紋帶蛺蝶': ('2a2018', 'f2f0ea', 'e08a2a', 1, 'b'), '臺灣赭弄蝶': ('8a5a2a', 'e8a040', '2a1a14', .6, 's'), '寬帶青鳳蝶': ('1a1a1e', '6ac8d8', '1a1a1e', 1, 'b'),
 '青眼蛺蝶': ('2a3a6a', '3a7ae0', 'e08a2a', .9, 'e'), '青雀斑灰蝶': ('3a6ac8', 'f2f2f2', '2a2a2a', .6, 's'), '黃豹盛蛺蝶': ('e8a02a', '1a1a1a', 'e8d070', 1, 's'),
 '黛眼蝶': ('6a5a44', 'c8b890', '1a1a1a', 1, 'e'), '劍青鳳蝶': ('f2f0e0', '1a1a1e', '7ad8c0', 1, 'vt'), '大流星弄蝶': ('5a4a3a', 'e8a040', '2a1a14', .8, 's'),
 '布氏蔭眼蝶': ('6a5a44', 'c8b890', '1a1a1a', 1, 'e'), '散紋盛蛺蝶': ('2a2018', 'e8a02a', 'f2f2f2', 1, 's'), '美鳳蝶': ('1a1a1e', 'c83a3a', 'f2f0ea', 1.5, 's'),
 '霓彩燕灰蝶': ('3a6ac8', 'e08a2a', '2a2a2a', .6, 'st'), '異紋紫斑蝶': ('2a1e3a', '6a3ab8', 'f2f2f2', 1.1, 's'), '箭環蝶': ('c88a3a', 'e8c070', '3a2a1a', 1.3, 'e'),
 '藍紋鋸眼蝶': ('1a1a2a', '4a7ad8', 'f2f2f2', 1, 'b'), '大紅紋鳳蝶': ('1a1a1e', 'd83a4a', 'f2f0ea', 1.4, 'st'), '大絹斑蝶': ('f2f0ea', '2a2a2a', '8ab8d8', 1.3, 'v'),
 '斷線環蛺蝶': ('2a2018', 'f2f0ea', 'e08a2a', .9, 'b'), '枯葉蝶': ('8a5a2a', 'e08a2a', '3a8ae0', 1.2, 'b'), '玉帶鳳蝶': ('1a1a1e', 'f2f0ea', 'c83a3a', 1.2, 'bt'),
 '異色尖粉蝶': ('f2f0ea', 'e8c030', '2a2a2a', 1, 'v'), '袖弄蝶': ('3a3a2a', 'f2f0ea', '2a2a2a', .7, 's'), '豆環蛺蝶': ('2a2018', 'f2f0ea', 'e08a2a', .8, 'b'),
 '黃星弄蝶': ('5a4a2a', 'e8c040', '2a1a14', .6, 's'),
 # notable moths
 '臺灣黃豹天蠶蛾': ('e8b030', '8a5a2a', '1a1a1a', 1.8, 'e'), '長尾水青蛾': ('b8e0c0', 'e8f0d8', 'a83a4a', 2.0, 'et'), '大黃豹天蠶蛾': ('e8a830', '8a5a2a', '1a1a1a', 2.0, 'e'),
 '綠目天蠶蛾': ('c8a070', '6aa070', '2a2a2a', 1.6, 'e'), '王氏眉紋天蠶蛾': ('8a5a3a', 'e8c8a0', '2a2a2a', 1.8, 'e'), '山繭蛾/天蠶蛾': ('a87a50', 'e8d0b0', '2a2a2a', 1.8, 'e'),
 '寬緣杜鵑斑蛾': ('1a1a2a', 'e8c030', '3a6ad8', 1, 'b'), '雅倩亮腹狹翅螢斑蛾': ('1a1a2a', 'e8502a', '3a6ad8', .8, 'p'), '福山透翅碩斑蛾': ('2a2a3a', 'c8d8e8', 'e8c030', 1, 'v'),
 '後雪裳蛾': ('6a6a6a', 'f2f2f2', '2a2a2a', 1.2, 'b'), '魔目裳蛾': ('6a5a4a', 'c8a070', '2a2a2a', 1.4, 'e'), '落葉裳蛾': ('8a6a40', 'e8a030', '2a2a2a', 1.3, 'b'),
 '鋸翅天蛾': ('8a7a5a', 'c8b890', '3a3028', 1.3, 'v'), '全緣缺角天蛾': ('7a6a4a', 'c8a070', '3a3028', 1.3, 'v'), '綠茶蠶蛾': ('7aa060', 'c8d8a0', '3a3a2a', 1, 'v'),
 '烏麗燈蛾': ('1a1a1a', 'e8e0d0', 'e8502a', 1, 's'), '大麗燈蛾': ('1a1a2a', 'f2f0ea', 'e8a030', 1.3, 's'), '粉蝶燈蛾': ('f2f0ea', '2a2a2a', 'e8c030', 1, 's'),
 '青枯葉蛾': ('8aa070', 'c8d8a0', '3a3a2a', 1.2, 'v'), '橙帶藍尺蛾': ('3a5ab8', 'e8802a', '1a1a2a', 1, 'b'), '綠翅茶斑尺蛾': ('6aa060', 'e8e0c0', '2a2a2a', 1, 's'),
 # beetles
 '眼鍬甲': ('8a3a1a', 'c84a2a', '1a1a1a', 1.2, 'm'), '平頭大鍬形蟲': ('141414', '2a2a2a', '0a0a0a', 1.4, 'm'), '臺灣扁鍬形蟲': ('1a1614', '2a2420', '0a0a0a', 1.3, 'm'),
 '臺灣八星虎甲蟲': ('2a6a4a', 'e8e0b0', '6a2a6a', 1, 's'), '白斑突眼虎甲蟲': ('3a3a2a', 'f2f0ea', '2a2a2a', 1, 's'), '大黑艷蟲': ('101012', '2a2a3a', '0a0a0a', 1.2, 'p'),
 '鹿角鍬形蟲': ('8a4a20', 'c86a2a', '1a1a1a', 1.2, 'm'), '小十三星瓢蟲': ('e8702a', '141414', '141414', .6, 's'), '豔細身赤鍬形蟲': ('c83a1a', 'e86a2a', '1a1a1a', 1.1, 'm'),
 '刀鍬形蟲': ('141414', '2a2a2a', '0a0a0a', 1.2, 'm'), '夜叉大鍬形蟲': ('141414', '2a2a2a', '0a0a0a', 1.3, 'm'), '安松凹翅螢金花蟲': ('2a3a8a', 'e8a030', '1a1a1a', .7, 'p'),
 '微獨角仙': ('3a2014', '5a3a24', '1a1a1a', 1, 'h'), '皺細身赤鍬形蟲': ('a8301a', 'e86a2a', '1a1a1a', 1.1, 'm'), '紅圓翅鍬形蟲': ('a8301a', 'c84a2a', '1a1a1a', 1, 'm'),
 '蓬萊凹翅螢金花蟲': ('2a3a8a', 'e8a030', '1a1a1a', .7, 'p'), '大琉璃擬守瓜': ('2a3ab8', '4a6ae0', '1a1a1a', .8, 'p'), '琉璃突眼虎甲蟲': ('2a4ab8', '3a8ae0', '1a1a1a', 1, 'p'),
 '鬼艷鍬形蟲': ('e8a020', '1a1a1a', '1a1a1a', 1.2, 'm'), '四斑麗大偽瓢蟲': ('1a1a2a', 'e8502a', '1a1a1a', .8, 's'), '榕四星螢金花蟲': ('e8a020', '1a1a1a', '1a1a1a', .7, 's'),
 '雲紋虎甲蟲': ('6a5a3a', 'e8e0c0', '2a2a2a', 1, 's'),
 # dragonflies & others
 '白痣珈蟌': ('2a8a5a', '1a1a1a', 'f2f2f2'), '金黃蜻蜓': ('e8b020', 'f2e0a0', '3a2a1a'), '樂仙蜻蜓': ('2a3a5a', '8ab8d8', '1a1a1a'),
 '芽痣蹣蟌': ('3a6ab8', '1a1a1a', 'e8e8e8'), '青紋絲蟌': ('2a8a6a', '1a1a1a', 'e8e8e8'), '鼎脈蜻蜓': ('c83a2a', 'e88a6a', '3a1a14'),
 '侏儒蜻蜓': ('c84a2a', 'e8a080', '3a1a14'), '赤褐灰蜻（中印亞種）': ('a84a2a', 'c88a6a', '3a1a14'), '黃基蜻蜓': ('c8a030', 'e8d080', '3a2a1a'),
 '中華珈蟌': ('1a5a4a', 'c84a2a', 'e8e8e8'), '短腹幽蟌': ('3a3a2a', 'e8c030', '1a1a1a'), '薄翅蜻蜓': ('e8a030', 'f2e0b0', '3a2a1a'),
 '紅紋沫蟬': ('1a1a1a', 'c83a2a', '1a1a1a'), '紋翅暮蟬': ('6a5a3a', 'c8b890', '2a2a1a', 1.3), '黑翅草蟬': ('2a3a1a', '6a8a3a', '1a1a1a'),
 '可禮大蟬': ('3a4a2a', '8a8a5a', '1a1a1a', 1.5), '眼紋疏廣蠟蟬': ('6a5a4a', 'f2f0ea', '2a2a2a'), '橙條大葉蟬': ('e8802a', '1a1a1a', 'e8c030', .7),
 '臺灣騷蟬': ('4a5a2a', '8a9a5a', '1a1a1a', 1.4), '四斑紅蝽': ('c83a2a', '1a1a1a', '1a1a1a'), '齒緣刺獵蝽': ('3a2a1a', 'c8a030', '1a1a1a'),
 '中華蜜蜂': ('6a4a20', 'e8b030', '1a1a1a'), '楚南熊蜂': ('1a1a1a', 'e8c030', 'e8702a', 1.3), '赭褐長腳蜂': ('8a4a20', 'e8b030', '3a1a10', 1.2),
 '雙色熊蜂': ('1a1a1a', 'e8c030', 'f2f0ea', 1.3), '精選熊蜂': ('1a1a1a', 'e8a030', 'e8502a', 1.3),
 '帶紋紺蠊': ('2a2a3a', 'e8c030', '1a1a1a'), '綠大齒螳': ('5a9a3a', '8ac060', '3a5a2a', 1.3), '臺灣巨斧螳': ('6aa040', '9ad060', '3a5a2a', 1.5),
 '魏氏奇葉螳螂': ('7a8a4a', 'a8b870', '3a3a2a', 1.2), '棕污斑螳': ('7a5a3a', 'a88a5a', '3a2a1a', 1.2), '黑翅細斯': ('3a6a3a', '1a1a1a', '6a9a4a'),
 # spiders
 '卓氏裂腹蛛': ('6a5a40', 'c8b080', '2a2018'), '中形金蛛': ('1a1a1a', 'e8c030', 'f2f0ea', 1.4), '西里銀腹蛛': ('c8c8c0', '3a4a3a', 'e8c030'),
 '梭德氏棘蛛': ('1a1a1a', 'e8c030', 'c83a2a'), '白額高腳蛛': ('6a5a40', 'f2f0ea', '3a2a1a', 1.6), '地衣鬼蛛': ('8a9a7a', 'c8c8b0', '3a3a2a'),
 '三角鬼蛛': ('c8a030', 'e8d080', '3a2a1a'), '小形金蛛': ('1a1a1a', 'e8c030', 'f2f0ea'), '泉字雲斑蛛': ('8a7a6a', 'f2f0ea', '2a2a2a'),
 '血紅扇頭蜱': ('8a3a1a', 'a85a3a', '3a1a10', .5),
}

def h(s, n):
    return int(hashlib.md5(s.encode()).hexdigest()[:6], 16) % n

FALLBACK = {
 'B': [('7a6a4a', 'd8ccaa', '4a3a2a'), ('6a7a40', 'e8d870', '3a3a2a'), ('6a6a70', 'e8e4dc', '2a2a2a')],
 'O': [('c8b890', 'e8e0c8', '6a5a40'), ('8a7a60', 'c8b890', '3a3028'), ('f2f0ea', 'c8a030', '3a3a3a'), ('e8c030', 'f2f0ea', '3a3a3a'), ('6a6a6a', 'c8c8c0', '2a2a2a')],
}

def colors(s, a):
    z = s['zh']
    if z in C: return C[z]
    if a == 'O':
        if '苔蛾' in z: return (('e8c030', 'f2f0ea', '2a2a2a'), ('f2f0ea', 'e8a030', '2a2a2a'), ('e8802a', 'f2e0a0', '2a2a2a'))[h(z, 3)] + (.9, 's')
        if '尺蛾' in z: return (('f2f0ea', 'c8b890', '6a5a40'), ('e8d880', 'f2f0ea', '8a6a3a'))[h(z, 2)] + (1.1, 'v')
        if '天蛾' in z: return ('8a7a5a', 'c8b890', '3a3028', 1.3, 'v')
        if '燈蛾' in z: return ('f2f0ea', '1a1a1a', 'e8802a', 1, 's')
        if '枯葉蛾' in z: return ('8a5a30', 'c88a50', '3a2a1a', 1.2, 'v')
        if '斑蛾' in z: return ('1a1a2a', 'e8c030', '3a6ad8', 1, 'b')
        if '帶鉤蛾' in z or '帶蛾' in z: return ('c8905a', 'f2e0c0', '6a4a2a', 1.1, 'b')
        return FALLBACK['O'][h(z, 5)] + (1, 'v')
    if a == 'B': return FALLBACK['B'][h(z, 3)]
    return ('7a6a50', 'c8b890', '3a2e20')

out = []
for s in sp:
    a = arche(s)
    c = colors(s, a)
    size = c[3] if len(c) > 3 else 1
    pat = c[4] if len(c) > 4 else ''
    st = ''.join(STATUS[x] for x in s['status'] if x in STATUS)
    mon = ''.join('0123456789abcdefghijklmnopqrstuvwxyz'[min(35, m)] for m in (s['months'] or [0]*12))
    iid = s['id'].split('-')[1]
    rec = [iid, s['zh'], s['sci'], GROUP[s['group']], s['family'], st, '1' if s['featured'] else '', str(s['obs']), mon,
           a, night(s, a), ('%g' % size) if size != 1 else '', ''.join(c[:3]), pat]
    assert not any('|' in x or '`' in x or '\n' in x for x in rec), rec
    out.append('|'.join(rec))

order = 'bmrasuocdkhi'
out.sort(key=lambda r: (order.index(r.split('|')[3]), -int(r.split('|')[7])))
data = '\n'.join(out)
html = SRC.read_text(encoding='utf-8')
new, n = re.subn(r'const SPECIES=`[\s\S]*?`;//@species', lambda m: 'const SPECIES=`' + data + '`;//@species', html)
assert n == 1, 'marker not found'
SRC.write_text(new, encoding='utf-8')
print(f'{len(out)} species, {len(data.encode())} bytes')
