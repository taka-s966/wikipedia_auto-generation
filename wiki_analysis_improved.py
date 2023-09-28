import wikipedia
import json
import codecs

# 調査したい項目
wikititle = ['農州','蕩州']

wikipedia.set_lang("ja")

for wikit in wikititle:
    categories_dic = {}
    title = []
    wk_categories = []
    openfilepass = 'dataset' + '\\' + wikit + '.json'
    outputfilepass = 'analysis' + '\\' + wikit + '.txt'

    f = open(openfilepass, "r")
    data = json.load(f)

    for v in data["query"]["backlinks"]:
        title.append(v["title"])

    for t in title:
        try:
            if '利用者' in t:
                continue
            if 'Template' in t:
                continue
            if 'Portal' in t:
                continue
            if 'Wikipedia' in t:
                continue
            if 'ノート:' in t:
                continue
            print(t)
            wikipage = wikipedia.page(t)
            if wikipage.categories is not None:
                categories = [s for s in wikipage.categories if ('識別子' or '記事' or 'ページ') not in s]
                if len(categories) > 0:
                    for data in categories:
                        wk_categories.append(data)
        except wikipedia.exceptions.PageError as e:
            # "PageError" の場合は次のページに進む
            print(e)
            continue
        except wikipedia.exceptions.DisambiguationError as e:
            # "DisambiguationError" の場合は次のページに進む
            print(e)
            continue

    for category in wk_categories:
        #  ページのカテゴリと頻度を格納する
        if category in categories_dic:
            categories_dic[category] += 1
        else:
            categories_dic[category] = 1

    categories_dic_sorted = sorted(categories_dic.items(), key=lambda x:x[1], reverse=True)

    print(*categories_dic_sorted, sep="\n", file=codecs.open(outputfilepass, 'w', 'utf-8'))

    f.close()