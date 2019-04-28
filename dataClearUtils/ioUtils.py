import pandas as pd
import jieba.posseg as pseg
import jieba
import random


def gen_sents(df, columns):
    sentences = []
    for column in columns:
        sentences.extend(df[column].values.tolist())
    sentences = list(map(format_sentence, sentences))
    return sentences


def gen_word_dic(df, filter_entity, dict_path):
    df = df[~df['entity_name'].isin(filter_entity)]
    df = df.reset_index(drop=True)
    with open(dict_path, "w", encoding="utf8") as f:
        for i in range(df.shape[0]):
            f.write(str(df.loc[i, "entity_synonym"]) + " " + str(df.loc[i, "entity_name"]) + "\n")


def segment(sentences, seg_dict_path=None):
    """
    分词
    :param sentences:
    :return:
    """
    if seg_dict_path is not None:
        jieba.load_userdict(seg_dict_path)
    pseg_sentences = []
    for sentence in sentences:
        sentence = str(sentence)
        pseg_sentence = [words.word + "/" + words.flag for words in pseg.cut(sentence)]
        pseg_sentences.append(pseg_sentence)
    return pseg_sentences


def shuffle_data(list):
    random.shuffle(list)
    return list


def auto_tagging(pseg_sentences, entitys):
    """
    自动标注
    :param pseg_sentences:
    :return:
    """
    results = []
    for pseg_sentence in pseg_sentences:
        result = []
        for word_p in pseg_sentence:
            word = word_p.strip().split("/")[0]
            p = word_p.strip().split("/")[1]
            entity_cat = []
            if p not in entitys:
                entity_cat = ["O" for i in range(len(word))]
            else:
                if len(word) == 1:
                    entity_cat = ["S-" + p]
                elif len(word) == 2:
                    entity_cat = ["B-" + p, "E-" + p]
                elif len(word) > 2:
                    entity_cat = ["I-" + p for i in range(len(word))]
                    entity_cat[0] = "B-" + p
                    entity_cat[-1] = "E-" + p
            result.extend(entity_cat)
        results.append(result)
    return results


def format_sentence(sentence):
    sentence = str(sentence).strip()
    sentence = sentence.replace("/", "-")
    sentence = sentence.replace(" ", "，")
    sentence = sentence.replace("\u3000", "，")
    sentence = sentence.replace("\n", "，")
    sentence = sentence.replace("\xa0", "，")
    sentence = sentence.replace("\u2006", "，")
    sentence = sentence.replace("\t", "，")
    sentence = sentence.replace("\uf06c", "，")

    return sentence


def gen_char_list(sentences):
    return [[sentence[i] for i in range(len(sentence))] for sentence in sentences]


if __name__ == '__main__':
    SOURCE_DATA_PATH = "/home/luoxinyu/文档/语料/NER/chinese_medicine/gaoxueya_final_handler_final.xlsx"
    COLUMNS = ["question", "answer"]
    ALL_DATA_PATH = "all_data.txt"

    df1 = pd.read_excel(SOURCE_DATA_PATH)
    df1 = df1.sample(frac=1)
    print("ori_size:", df1.shape[0])
    df1 = df1.dropna()
    print("after_dropna_size:", df1.shape[0])
    df1 = df1.drop_duplicates()
    df1 = df1.reset_index(drop=True)
    print("after_drop_dup_size:", df1.shape[0])

    sentences = gen_sents(df1, COLUMNS)
    print("origin_size:", len(sentences))
    sentences = list(set(sentences))
    print("drop_dup_again_size:", len(sentences))
    char_lists = gen_char_list(sentences)
    print(sentences[0])

    DICT_PATH = "word_dict.txt"
    entitys = ['disease', 'medicine', 'symptoms', 'manufacturer', 'physiological', 'drinks',
               'meat', 'special_time', 'cosmetics', 'vegetables', 'cooked_food', 'snacks', 'sports',
               'staple_food', 'people', 'nutrient', 'surgical_item', 'physical_indicators',
               'mental_condition', 'treatment_method', 'fruit', 'check_item', 'condiment', 'milk',
               'intent_word', 'human_body_element', 'equipment', 'value', 'dietary_recommendation',
               'egg', 'sports_equipment', 'TCM', 'color', 'acupoint', 'city', 'pathogeny']
    a = segment(sentences, DICT_PATH)
    tag_lists = auto_tagging(a, entitys)  ## 每个句子的标注

    print(char_lists)
    print(tag_lists)
    features = [char_lists, tag_lists]

    with open(ALL_DATA_PATH, "w", encoding="utf8") as f:
        for i in range(len(char_lists)):
            for j in range(len(char_lists[i])):
                per_row = []
                for h in range(len(features)):
                    try:
                        per_row.append(features[h][i][j])
                    except(Exception):
                        print(features[0][i], features[1][i])
                        print(len(features[0][i]), len(features[1][i]))
                row_content = " ".join(per_row)
                f.write(row_content)
                f.write("\n")
            f.write("\n")
        print(len(char_lists))
    # ENTITY_DATA_PATH = "/home/luoxinyu/文档/语料/NER/chinese_medicine/entity_checkFinal0410.xlsx"
    # FILTER_ENTITY = ['lifestyle', 'sort', 'verb', 'period']
    # DICT_PATH = "word_dict.txt"

    # df2 = pd.read_excel(ENTITY_DATA_PATH)
    # gen_word_dic(df2, FILTER_ENTITY, DICT_PATH)

    # print (df[COLUMNS].value_counts())
