import xml.etree.ElementTree as ET
import codecs
import re

# 調査したい項目
#wikititle = ['Android端末 (シャープ)','COVID-19ワクチン','NFLのシーズン','UFCの大会','アメリカ合衆国の野球選手','インドの文化','ガンダムシリーズ漫画作品','ギリシア神話の人物','ニュースポーツ']
#wikititle = ['バスケットボール欧州選手権','フジテレビの特別番組','プロレスリング・ノアの関係者','ポケットモンスターのスピンオフゲーム','岡崎市の町・字','屋根','下着','活火山','寺院建築','自動車部品']
wikititle = ['新潟県道','宋朝の行政区分','増支部','男役','東宝の人物','特撮スタッフ','日本の考古学','日本の女性声優','日本の男性声優','宝塚歌劇団の演出家']
#wikititle = ['Android端末 (シャープ)']

for wikit in wikititle:
    openfilepass = 'xml_dataset' + '\\' + wikit + '.xml'
    outputfilepass = 'headingtext_dataset' + '\\' + wikit + '.txt'
    heading_text = []
    # XMLファイルを解析
    tree = ET.parse(openfilepass) 

    # XMLを取得
    root = tree.getroot()

    namespace= {"": "http://www.mediawiki.org/xml/export-0.10/"}

    # 要素「text」のデータを1つずつ取得
    for i in root.iterfind("./page/revision/text", namespace):
        for line in i.text.splitlines():
            # 参照部分を削除
            line = re.sub('<ref.*?/ref>', '', line)
            m = re.match(r'^\'\'\'.*?\'\'\'.*?。|^『\'\'\'.*?\'\'\'』.*?。', line)
            if m is not None:
                heading_text.append(m.group())

    print(wikit + ' : ' + str(len(heading_text)))
    print(*heading_text, sep="\n", file=codecs.open(outputfilepass, 'w', 'utf-8'))