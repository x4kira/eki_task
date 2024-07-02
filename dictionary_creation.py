import requests
import json
import re

ekilex_api_base_url = "https://ekilex.ee/api/"
possible_compound_verbs = []
last_est_id = 1384169  # 1384169, 1384186 -> peaks 1384169 olema

testing_data = [
    {"wordId": 263219, "value": "ülekäigurada", "lang": "est", "morphExists": True},
    {"wordId": 524218, "value": "prurigo", "lang": "lat", "morphExists": False},
    {"wordId": 210889, "value": "ole lahke", "lang": "est", "morphExists": True},
    {"wordId": 154877, "value": "abstraktne kunst", "lang": "est", "morphExists": True},
    {"wordId": 154504, "value": "Aafrika elevant", "lang": "est", "morphExists": True},
    {"wordId": 1241409, "value": "slogan", "lang": "fra", "morphExists": False},
    {"wordId": 234992, "value": "solgiga üle valama", "lang": "est", "morphExists": True},
    {"wordId": 289477, "value": "abiks olema", "lang": "est", "morphExists": True},
    {"wordId": 155062, "value": "aega viitma", "lang": "est", "morphExists": True},
    {"wordId": 285490, "value": "aega võtma", "lang": "est", "morphExists": True},
    {"wordId": 263104, "value": "üle", "lang": "est", "morphExists": True},
    {"wordId": 156734, "value": "Alpid", "lang": "est", "morphExists": False},
    {"wordId": 1205479, "value": "amü", "lang": "est", "morphExists": False},
    {"wordId": 197328, "value": "luurama", "lang": "est", "morphExists": True},
    {"wordId": 162941, "value": "ei saa üle ega ümber", "lang": "est", "morphExists": True},
    {"wordId": 174976, "value": "jõuga üle sõitma", "lang": "est", "morphExists": True},
    {"wordId": 508974, "value": "üle aitama", "lang": "est", "morphExists": True},
    {"wordId": 155602, "value": "aitama", "lang": "est", "morphExists": True},
    {"wordId": 263295, "value": "üle minema", "lang": "est", "morphExists": True},
    {"wordId": 158017, "value": "armas", "lang": "est", "morphExists": True},
    {"wordId": 237939, "value": "suur", "lang": "est", "morphExists": True},
    {"wordId": 1620434, "value": "numinoosne", "lang": "est", "morphExists": True},
    {"wordId": 441341, "value": "demopoliitika", "lang": "est", "morphExists": True},
    {"wordId": 261075, "value": "õnnelik", "lang": "est", "morphExists": True}
]


def dictionary_creator(api_key: str):
    public_word_url = "public_word/eki"
    # get_last_est_id(api_key)

    # dynamically_write_est_word_to_json_file(api_key, public_word_url, "all_est_words_with_id", "all_est_compound_verbs")
    json_reader_writer_with_sorter_meaning_paradigm("all_est_words_with_id", "all_est_words_with_paradigms_meanings",
                                                    api_key)
    # add_compound_verbs_to_json_file("all_est_words_with_paradigms_meanings", "all_est_words_with_comp", "all_est_compound_verbs", api_key)
    # convert_json_to_xhtml("all_est_words_with_comp", "xhtml_dictionary")


def est_noncapitalized_single_words_sorter(data: dict):
    if data['lang'] == 'est' and data["value"].islower() and " " not in data["value"]:
        return data
    elif data["lang"] == "est" and " " in data["value"] and data["value"].islower() and len(
            data["value"].split(" ")) == 2 and str(data["value"][-2:]) == "ma":
        possible_compound_verbs.append(data)


def get_last_est_id_with_meaning(api_key: str):
    public_word_url = "public_word/eki"
    headers = {"ekilex-api-key": api_key}
    pattern = r"{\"wordId\": \d*, \"value\": \".*\", \"lang\": \"est\", \"morphExists\": .*}"
    last_id_pattern = r"(?<=\"wordId\": )\d+"
    value_pattern = r'\"value\": \"(.*?)\"'

    response = requests.get(ekilex_api_base_url + public_word_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        data_string = json.dumps(data, ensure_ascii=False)
        matches = list(re.finditer(pattern, data_string))
        if matches:
            for match in matches:
                backwards_index = -1
                last_match = matches[backwards_index]
                id_search = re.search(last_id_pattern, str(last_match))
                value_search = re.search(value_pattern, str(last_match))
                global last_est_id
                last_est_id = id_search.group()
                value = value_search.group(1)
                if get_word_meaning_paradigm_adjective_comparison(api_key, int(last_est_id), value, if_osi_word):
                    print(value)
                    return last_est_id
                else:
                    backwards_index -= 1
        else:
            print("No last est id found.")
    else:
        print("Something went wrong while trying to get last est id, status code: " + str(response.status_code))


def get_word_meaning_paradigm_adjective_comparison(api_key: str, word_id: int, word: str, osi_sorter=None):
    url = ekilex_api_base_url + "word/details/" + str(word_id)
    headers = {"ekilex-api-key": api_key}
    response = requests.get(url, headers=headers, )

    if response.status_code == 200:
        if empty_response_checker(response):
            data = response.json()
            if not osi_sorter or osi_sorter(data):
                type = get_word_type(data)
                word_dict = {"word": word, "wordId": word_id}

                if get_meanings_list(data):
                    word_dict["meaning"] = get_meanings_list(data)
                    if get_word_type(data):
                        word_dict["type"] = type
                    if check_if_paradigm_exists(data) and type == "omadussõna, adjektiiv":
                        forms = get_paradigm_list(data)
                        comparison = get_comparison(data, api_key)
                        forms += comparison
                        word_dict["forms"] = forms
                    if check_if_paradigm_exists(data) and type != "omadussõna, adjektiiv":
                        forms = get_paradigm_list(data)
                        word_dict["forms"] = forms
                    return word_dict

    else:
        return "Something went wrong while looking for meaning-paradigm-comparsion, status code: " + str(
            response.status_code)


def empty_response_checker(response):
    try:
        data = response.json()
        return data
    except Exception:
        return None


def if_osi_word(data: dict) -> bool:
    word = data["word"]
    lexemesTagNames = word["lexemesTagNames"]
    return "ÕSi liitsõna" in lexemesTagNames or "ÕSi sõna" in lexemesTagNames


def get_word_type(data: dict):
    lexemes = data["lexemes"]
    for info_dict in lexemes:
        if info_dict["pos"]:
            pos = info_dict["pos"]
            if len(pos) > 1:
                types = ""
                for i, type_dict in enumerate(pos):  # enumerate begins
                    if i == len(pos) - 1:
                        types += type_dict["value"]
                    else:
                        types += type_dict["value"] + ", "
                return types
            else:
                pos_dict = pos[0]
                return pos_dict["value"]


def get_comparison(data, api_key):
    comparison_list = []
    word_relation_details = data["wordRelationDetails"]
    secondary_word_relation_groups = word_relation_details["secondaryWordRelationGroups"]
    for comparison_dict in secondary_word_relation_groups:
        members_list = comparison_dict["members"]
        for word_dict in members_list:
            if "kõige" not in word_dict["wordValue"]:
                word_id = word_dict["wordId"]
                url = ekilex_api_base_url + "word/details/" + str(word_id)
                headers = {"ekilex-api-key": api_key}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    paradigms = data["paradigms"]
                    if paradigms:
                        forms = paradigms[0]["forms"]
                        paradigms_list = [paradigm_dict["value"] for paradigm_dict in forms if
                                          paradigm_dict["value"] != "-"]
                        comparison_list += paradigms_list
    return comparison_list


def check_if_paradigm_exists(data):
    if data["paradigms"]:
        return True
    else:
        return False


def get_meanings_list(data):
    lexemes_first_dict = data["lexemes"][0]
    meaning = lexemes_first_dict["meaning"]
    definitions = meaning["definitions"]
    est_meaning_dicts = [small_dict for small_dict in definitions if small_dict["lang"] == "est"]
    meanings = [meaning["value"] for meaning in est_meaning_dicts]
    if meanings:
        return meanings


def get_paradigm_list(data):
    paradigms_whole_list = data["paradigms"]
    whole_paradigm_dict = paradigms_whole_list[0]
    forms = whole_paradigm_dict["forms"]
    forms_list = [form_dict["value"] for form_dict in forms if
                  form_dict["value"] != "-"]  # non-existing forms aka "-" are sorted out right now
    return forms_list


def dynamically_write_est_word_to_json_file(api_key: str, api_command: str, output_file_name: str,
                                            compound_verbs_list_file_name: str):
    url = ekilex_api_base_url + api_command
    headers = {"ekilex-api-key": api_key}

    with requests.get(url, headers=headers, stream=True) as response, open(output_file_name + '.json', 'w') as file, open(compound_verbs_list_file_name + '.json', 'w') as file2:
        try:
            response.raise_for_status()
            file.write('[\n')

            for word_dict in response.json():
                if est_noncapitalized_single_words_sorter(word_dict) and word_dict["wordId"] == last_est_id:
                    file.write(json.dumps(word_dict, ensure_ascii=False))
                    file.write("\n")
                    file.write(']')
                    break
                if est_noncapitalized_single_words_sorter(word_dict):
                    file.write(json.dumps(word_dict, ensure_ascii=False))
                    file.write(",\n")
            file2.write(json.dumps(possible_compound_verbs, ensure_ascii=False))

        except requests.exceptions.HTTPError as e:
            return f"HTTP error occurred: {e}"
        except Exception as e:
            print(f"Other error occurred while public request and: {e}")


def json_reader_writer_with_sorter_meaning_paradigm(input_file_name: str, output_file_name: str, api_key: str):
    with open(input_file_name + '.json', 'r') as input_file, open(output_file_name + '.json', 'w') as output_file:
        try:
            output_file.write('[\n')
            prev_data = None

            for line in input_file:
                word_dict = line_convertor_to_dict(line)
                if word_dict:
                    word_data = get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                               word_dict["value"], if_osi_word)
                    if word_data:
                        print(word_data["word"])
                        if prev_data is not None:
                            output_file.write(json.dumps(prev_data, ensure_ascii=False))
                            output_file.write(",\n")
                        prev_data = word_data

            if prev_data is not None:
                output_file.write(json.dumps(prev_data, ensure_ascii=False))

            output_file.write('\n]')
        except Exception as e:
            print(f"Error occurred while reading-writing meaning-paradigms: {e}")


def line_convertor_to_dict(line: str):  # -> dict | None
    if line[0] == "{":
        if line[-2] == ",":
            cut_dict = line[:-2]
            return json.loads(cut_dict)
        else:
            cut_dict = line[:-1]
            return json.loads(cut_dict)


def test_write_to_json_file(output_file_name: str, compound_verbs_list_file_name: str, sorter_func=None):
    with open(output_file_name + '.json', 'w') as file, open(compound_verbs_list_file_name + '.json', 'w') as file2:
        try:
            file.write('[\n')
            prev_data = None

            for line in testing_data:
                if sorter_func is None or sorter_func(line):
                    if prev_data is not None:
                        file.write(json.dumps(prev_data, ensure_ascii=False))
                        file.write(",\n")
                    prev_data = line

            if prev_data is not None:
                file.write(json.dumps(prev_data, ensure_ascii=False))

            file.write('\n]')

            file2.write(json.dumps(possible_compound_verbs, ensure_ascii=False))

        except Exception as e:
            print(f"Other error occurred: {e}")


def compound_verbs_sorter(list_file_name: str, api_key: str):
    compound_verbs = {}
    headers = {"ekilex-api-key": api_key}

    try:
        with open(list_file_name + '.json', 'r') as file:
            for line in file:
                data_line = json.loads(line)
                for word_dict in data_line:
                    word = word_dict["value"]
                    print(word)
                    word_id = word_dict["wordId"]
                    url = ekilex_api_base_url + "word/details/" + str(word_id)
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if data["wordTypes"]:
                            word_type = data["wordTypes"]
                            if word_type[0]["value"] == "ühendverb":
                                word_list = word.split(" ")
                                verb = word_list[1]
                                if verb in compound_verbs.keys():
                                    compound_verbs[verb].add(word)
                                if verb not in compound_verbs.keys():
                                    compound_verbs[verb] = {word}
            print(compound_verbs)
            return compound_verbs
    except Exception as e:
        print(f"Error occurred while handling compound verbs file: {e}")


def add_compound_verbs_to_json_file(input_file_name: str, output_file_name: str, list_file_name: str, api_key):
    compound_verbs_dict = compound_verbs_sorter(list_file_name, api_key)

    with open(input_file_name + '.json', 'r') as input_file, open(output_file_name + '.json', 'w') as output_file:
        try:
            output_file.write('[\n')
            for line in input_file:
                if line_convertor_to_dict(line):
                    word_dict = line_convertor_to_dict(line)
                    print(word_dict["word"])
                    if word_dict["word"] in compound_verbs_dict.keys():
                        word_dict["compound verbs"] = compound_verbs_dict[word_dict["word"]]
                        output_file.write(json.dumps(word_dict, ensure_ascii=False) + ",\n")
                    elif word_dict["wordId"] == last_est_id:
                        print(word_dict["word"])
                        output_file.write(json.dumps(word_dict, ensure_ascii=False) + "\n")
                    else:
                        output_file.write(json.dumps(word_dict, ensure_ascii=False) + ",\n")
            output_file.write(']')
        except Exception as e:
            print(f"Error occurred while reading-writing compound verbs: {e}")


def dynamically_write_any_api_data_to_json_file(api_key: str, api_command: str, output_file_name: str,
                                                sorter_func=None):
    url = ekilex_api_base_url + api_command
    headers = {"ekilex-api-key": api_key}

    with requests.get(url, headers=headers, stream=True) as response, open(output_file_name + '.json', 'w') as file:
        try:
            response.raise_for_status()
            file.write('[\n')
            first = True

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    if not sorter_func or sorter_func(data):
                        if not first:
                            file.write(',\n')
                        json.dump(data, file, indent=4, ensure_ascii=False)
                        first = False
            file.write('\n]')

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"Other error occurred while public request and: {e}")


def continuing_after_error(original_data_file_name: str, with_error_file_name: str, api_key: str):
    try:
        last_id = 0
        with open(with_error_file_name + '.json', 'r') as file:
            for line in file:
                if line_convertor_to_dict(line):
                    word_dict = line_convertor_to_dict(line)
                    last_id = word_dict["wordId"]
        with open(with_error_file_name + '.json', 'a') as writing_file, open(original_data_file_name + '.json',
                                                                             'r') as reading_file:
            passed_error = False
            for line in reading_file:
                if line_convertor_to_dict(line):
                    word_dict = line_convertor_to_dict(line)
                    if word_dict["wordId"] == last_id and not passed_error:
                        passed_error = True
                        continue
                    elif passed_error:
                        if get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                          word_dict["value"], if_osi_word):
                            if word_dict["wordId"] == last_est_id:
                                writing_file.write(json.dumps(
                                    get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                                   word_dict["value"], if_osi_word),
                                    ensure_ascii=False) + "\n")
                                writing_file.write(']')
                                print("file written!")
                                break
                            else:
                                print(word_dict["value"])
                                writing_file.write(json.dumps(
                                    get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                                   word_dict["value"], if_osi_word),
                                    ensure_ascii=False) + ",\n")
    except Exception as e:
        if "Caused by ConnectTimeoutError" in str(e):
            continuing_after_error(original_data_file_name, with_error_file_name, api_key)
        print(f"Error occurred while continuing after error: {e}")


def convert_json_to_xhtml(input_file_name: str, output_file_name: str):
    with open(input_file_name + '.json', 'r') as input_file, open(output_file_name + '.html', 'w') as output_file:
        try:
            output_file.write(
                '<html xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"' + "\n"
                + 'xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"' + "\n"
                + 'xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"' + "\n"
                + '<section id="glossary">' + "\n"
                + '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head> <body>' + "\n"
                + "<mbp:frameset>")
            for line in input_file:
                if line_convertor_to_dict(line):
                    word_dict = line_convertor_to_dict(line)
                    word = word_dict["word"]
                    word_id = word_dict["wordId"]
                    word_html = (f'<idx:entry name="estonian" scriptable="yes" spell="yes" id="{word_id}">\n<idx:short'
                                 f'><a id="{word_id}"></a>') + f"\n" + f'<idx:orth value="{word}"><b>{word}</b><idx:infl>' + f"\n"
                    if "forms" in word_dict:
                        forms_html = f''
                        forms = list(set(word_dict["forms"]))
                        for form in forms:
                            forms_html += f'<idx:iform value="{form}"></idx:iform> '
                        word_html += forms_html
                    word_html += f'</idx:infl>\n</idx:orth>'
                    if "type" in word_dict:
                        type = word_dict["type"]
                        word_html += f'<i><br>[{type}]</i>\n'
                    if "meaning" in word_dict.keys():
                        meanings = word_dict["meaning"]
                        if len(meanings) == 1:
                            word_html += f'<p> {meanings[0]}</p>'
                        else:
                            meaning_counter = 1
                            for separated_meaning in meanings:
                                word_html += f'<p> {meaning_counter}. {separated_meaning} </p>\n'
                                meaning_counter += 1
                            meaning_counter = 1
                    if "compound verbs" in word_dict:
                        compound_verbs_string = ""
                        compound_verbs = word_dict["compound verbs"]
                        for verb in compound_verbs:
                            if verb == compound_verbs[-1]:
                                compound_verbs_string += f'{verb}'
                            else:
                                compound_verbs_string += f'{verb}, '
                        word_html += f'<p> Ühendtegusõnad: {compound_verbs_string} </p>'
                    word_html += f'</idx:short>\n</idx:entry><br><br>\n\n'
                    print(word)
                    output_file.write(word_html)
            output_file.write("</mbp:frameset>" + "\n" + '<section/>' + "\n" + "</body>" + "\n" + "</html>")
        except Exception as e:
            print(f"Error occur while converting json file to xhtml: {e}")


if __name__ == '__main__':
    # print(get_last_est_id_with_meaning("2b209545d7654ce99c995994ac8aef1f"))
    # json_reader_writer_with_sorter_meaning_paradigm("all_est_words_with_id", "all_est_words_with_p_m_osi_filtriga", "2b209545d7654ce99c995994ac8aef1f")
    # dynamically_write_est_word_to_json_file("2b209545d7654ce99c995994ac8aef1f", "public_word/eki", "all_est_words_with_id", "all_est_compound_verbs_list")
    # add_compound_verbs_to_json_file("all_est_words_with_p_m_osi_filtriga", "all_est_words_with_comp", "all_est_compound_verbs_list", "2b209545d7654ce99c995994ac8aef1f")
    convert_json_to_xhtml("all_est_words_with_p_m_osi_filtriga", "xhtml_osi_dictionary")
