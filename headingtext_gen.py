import xml.etree.ElementTree as ET
import numpy as np
import re
import codecs

# 調査したいカテゴリ
#categories = ['Android端末 (シャープ)','COVID-19ワクチン','NFLのシーズン','UFCの大会','アメリカ合衆国の野球選手','インドの文化','ガンダムシリーズ漫画作品','ギリシア神話の人物','ニュースポーツ']
#categories = ['バスケットボール欧州選手権','フジテレビの特別番組','プロレスリング・ノアの関係者','ポケットモンスターのスピンオフゲーム','岡崎市の町・字','屋根','下着','活火山','寺院建築','自動車部品']
#categories = ['新潟県道','宋朝の行政区分','増支部','男役','東宝の人物','特撮スタッフ','日本の考古学','日本の女性声優','日本の男性声優','宝塚歌劇団の演出家']
categories = ['増支部']

for category in categories:
    fwd_dic = {}
    heading_text_dic = {}
    openfilepath = 'headingtext_dataset' + '\\' + category + '.txt'
    heading_text = []
    length = 5

    with open(openfilepath, encoding="utf-8", mode="r") as f:
        for h_line in f:
            # 行の分割
            split_line = h_line.split("\n")
            for line in split_line:
                # 参照部分を削除
                line = re.sub('<ref.*?/ref>', '', line)
                line = re.sub('^\'\'\'\{\{.*?\}\}\'\'\'', '＠', line)
                if line != '' and ('[[' in line) and not ('＠' in line):
                    heading_text_dic[line] = len(line)

    with open(openfilepath, encoding="utf-8", mode="r") as f:
        for h_line in f:
            h_list = re.findall(r'\[\[[^\]]+\]\]', h_line)
            if h_list is not None:
                heading_text.append(h_list)

    for feature_wds in heading_text:
        for feature_wd in feature_wds:
            # 文字変換
            feature_wd = feature_wd.translate(str.maketrans({'[': None, ']': None}))
            # ページのカテゴリと頻度を格納する
            if feature_wd in fwd_dic:
                fwd_dic[feature_wd] += 1
            else:
                fwd_dic[feature_wd] = 1

    # fwd_dicをvalueでソートしたときの上位5個を取得
    new_fwd_dic = {}
    lists = sorted(fwd_dic.items(), key=lambda x: x[1], reverse=True)
    if len(lists) < length:
        length = len(lists)
    for i in range(length):
        new_fwd_dic[lists[i][0]] = lists[i][1]

    length = 7

    # heading_text_dicをvalueで昇順ソートしたときの上位7個を取得
    new_heading_text_dic = {}
    lists = sorted(heading_text_dic.items(), key=lambda x: x[1])
    if len(lists) < length:
        length = len(lists)
    for i in range(length):
        new_heading_text_dic[lists[i][0]] = lists[i][1]

    #print('heading_text : {0}'.format(heading_text))
    #print('--------------------------------------------------------------')
    #print('heading_text_dic : {0}'.format(heading_text_dic))
    print('--------------------------------------------------------------')
    print('new_fwd_dic : {0}'.format(new_fwd_dic))
    print('--------------------------------------------------------------')
    print('new_heading_text_dic : {0}'.format(new_heading_text_dic))
    print('--------------------------------------------------------------')

    heading = '（なし）'
    # リンク語
    link_word = ''
    for fwd_dic_key in new_fwd_dic.keys():
        for heading_text_key in new_heading_text_dic.keys():
            if fwd_dic_key in heading_text_key:
                heading = heading_text_key
                if heading != '（なし）':
                    link_word = fwd_dic_key
                    break
        if heading != '（なし）':
            break

    print('heading : {0}'.format(heading))
    # -------------------------------見出し文の穴埋め化-------------------------------
    # 項目名、読み仮名、数字、その他固有名詞を置換
    heading = re.sub('\'\'\'.*?\'\'\'', '【項目名】', heading)
    heading = re.sub('（.*?）', '（【読み仮名】）', heading)
    heading = re.sub('[0-9]+?', '【数字】', heading)
    heading = re.sub('\[\[' + link_word + '\]\]', link_word , heading)
    heading = re.sub('\[\[.*?\]\]', '【編集してください】' , heading)
    heading = re.sub('【項目名】', 'SHV38' , heading)
    print('link_word : {0}'.format(link_word))

    # -------------------------------節構成の生成-------------------------------
    structure_dic = {}
    title_list = []
    rank = 0
    openfilepass = 'xml_dataset' + '\\' + category + '.xml'
    #outputfilepass = 'structure_dataset' + '\\' + category + '.txt'

    # XMLファイルを解析
    tree = ET.parse(openfilepass) 

    # XMLを取得
    root = tree.getroot()

    namespace= {"": "http://www.mediawiki.org/xml/export-0.10/"}

    # 要素「text」のデータを1つずつ取得
    for i in root.iterfind("./page/revision/text", namespace):
        for line in i.text.splitlines():
            m = re.match(r'^\'\'\'.*\'\'\'.*?。|^『\'\'\'.*\'\'\'』.*?。', line)
            if m is not None:
                title_list.append(m.group())
                rank = 0
            macth_word = re.findall(r'^\=\=.*\=\=', line)
            if len(macth_word) != 0:
                for wd in macth_word:
                    wd = wd.replace('=','').replace(' ','')
                    if '脚注' in wd:
                        continue
                    if '外部リンク' in wd:
                        continue
                    if '参考文献' in wd:
                        continue
                    if '出典' in wd:
                        continue
                    if '注釈' in wd:
                        continue
                    if '出典・参考文献' in wd:
                        continue
                    if '出典（リンク）' in wd:
                        continue
                    if '関連項目' in wd:
                        continue
                    #構成と頻度を格納する
                    if wd in structure_dic:
                        rank += 1
                        structure_dic[wd][0] += 1
                        structure_dic[wd][1] += rank
                    else:
                        rank += 1
                        structure_dic[wd] = [1 , rank]

    for v in structure_dic.values():
        # v[0]:構成の出現頻度 → 節構成の出現割合
        # v[1]:構成の順位合計 → 節構成の平均順位
        # 一項目あたりの節構成の平均順位を求める
        v[1] = v[1] / v[0]
        v[1] = np.around(v[1], 3)
        # 節構成の出現割合を求める
        v[0] = v[0] / len(heading_text)
        v[0] = np.around(v[0], 3)

    print(category + ' : ' + str(len(heading_text)))
    # 節構成の出現割合を基準として降順にソート（※確認用）
    new_structure_list = sorted(structure_dic.items(), key=lambda x: x[1], reverse=True)
    print('structure_dic : {0}'.format(new_structure_list))

    # 出現割合の基準値
    st_value = 0.3

    # structure_dicから出現割合が基準値以上の節構成を取得
    new_structure = []
    for k, v in structure_dic.items():
        if v[0] >= st_value:
            new_structure.append([k,v[1]])
            new_structure = sorted(new_structure, key=lambda x: x[1], reverse=False)

    print('--------------------------------------')
    print(heading)
    print('--------------------------------------')
    for str_list in new_structure:
        print(str_list[0])
    print('--------------------------------------')
    # print(*new_structure_dic, sep="\n", file=codecs.open(outputfilepass, 'w', 'utf-8'))

