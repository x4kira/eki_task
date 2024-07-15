"""
Python 3.12 is mostly recommended, but versions >= 3.6 should work too or if any problems occur, then
only few adjustments should be needed.

****************************** !!! IMPORTANT !!! ******************************
*** Please do not use code (even with changes) publicly without addressing to author and/or EKI. ***
"""

import requests
import json

ekilex_api_base_url = "https://ekilex.ee/api/"
possible_compound_verbs = []
# testing_data = [] this global variable is for testing purposes (funstion test_write_to_json_file)
last_est_id = 1384169  # Must be manually set after calling out get_last_est_id_with_meaning()


def est_noncapitalized_single_words_sorter(data: dict):
    """Recommended sorter to sort out estonian words that are not capitalized single words.
    Can be given as parameter to dynamivally_write_all_est_word_to_json_file() and test_write_to_json_file()."""
    if data['lang'] == 'est' and data["value"].islower() and " " not in data["value"]:
        return data
    elif data["lang"] == "est" and " " in data["value"] and data["value"].islower() and len(
            data["value"].split(" ")) == 2 and str(data["value"][-2:]) == "ma":
        possible_compound_verbs.append(data)


def get_last_est_id_with_meaning(api_key: str):
    """Gets the last id of an estonian word that has meaning, useful when using public_word/eki API command
    because then the code won't iterate through all the words"""
    public_word_url = "public_word/eki"
    headers = {"ekilex-api-key": api_key}

    try:
        response = requests.get(ekilex_api_base_url + public_word_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        backwards_data = data[::-1]

        for word_dict in backwards_data:
            if word_dict["lang"] == "est" and get_word_meaning_paradigm_adjective_comparison(api_key,
                                                                                             word_dict["wordId"],
                                                                                             word_dict["value"]):
                last_est_id = word_dict["wordId"]
                print(f"Change manually global variable last_est_id to: {last_est_id}")
                break
    except Exception as e:
        print(f"Error occures while finding last est id with meaning: {e}")


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
    """This functon can be used to sort out words that have tag "ÕSi sõna" and/or "ÕSi liitsõna".
    Can be given as parameter to function get_word_meaning_paradigm_adjective_comparison()."""
    word = data["word"]
    lexemesTagNames = word["lexemesTagNames"]
    return "ÕSi sõna" in lexemesTagNames and "ÕSi liitsõna" not in lexemesTagNames  # "ÕSi liitsõna" in lexemesTagNames or


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
    est_meaning_dicts = [small_dict for small_dict in definitions if small_dict["lang"] == "est" and small_dict["public"] == True]
    meanings = [meaning["value"] for meaning in est_meaning_dicts]
    if meanings:
        return meanings


def get_paradigm_list(data):
    paradigms_whole_list = data["paradigms"]
    whole_paradigm_dict = paradigms_whole_list[0]
    forms = whole_paradigm_dict["forms"]
    forms_list = [form_dict["value"] for form_dict in forms if
                  form_dict["value"] != "-"]
    return forms_list


def dynamically_write_all_est_word_to_json_file(api_key: str, output_file_name: str,
                                                compound_verbs_list_file_name: str):
    """Creating a json file of all estonian words that aren't capitalized and are single words,
    possible compound verbs are written into other file. Filter can be removed."""
    public_command = "public_word/eki"
    url = ekilex_api_base_url + public_command
    headers = {"ekilex-api-key": api_key}

    with requests.get(url, headers=headers, stream=True) as response, open(output_file_name + '.json',
                                                                           'w') as file, open(
        compound_verbs_list_file_name + '.json', 'w') as file2:
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
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"Other error occurred while public request and: {e}")


def json_reader_writer_meaning_paradigm(input_file_name: str, output_file_name: str, api_key: str):
    """Adds detailed information to words like meaning, paradigm, comparison, word type (if these exist)."""
    with open(input_file_name + '.json', 'r') as input_file, open(output_file_name + '.json', 'w') as output_file:
        try:
            output_file.write('[\n')
            prev_data = None

            for line in input_file:
                word_dict = line_convertor_to_dict(line)
                if word_dict:
                    word_data = get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                               word_dict["value"])
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


def line_convertor_to_dict(line: str):
    if line[0] == "{":
        if line[-2] == ",":
            cut_dict = line[:-2]
            return json.loads(cut_dict)
        else:
            cut_dict = line[:-1]
            return json.loads(cut_dict)


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
                        word_dict["compound verbs"] = list(compound_verbs_dict[word_dict["word"]])
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
    """Making a json file of any api command, great for making example files.
    (https://ekilex.ee/api/ part of command is added from ekilex_api_base_url)
    Example API commands:
    word/search/{word}
    word/details/{wordId}...
    more commands: https://github.com/keeleinstituut/ekilex/wiki/Ekilex-API"""
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
    """Function can be changed according to your needs, depends on what process error occurred."""
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
                                                                          word_dict["value"]):
                            if word_dict["wordId"] == last_est_id:
                                writing_file.write(json.dumps(
                                    get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                                   word_dict["value"]),
                                    ensure_ascii=False) + "\n")
                                writing_file.write(']')
                                print("file written!")
                                break
                            else:
                                print(word_dict["value"])
                                writing_file.write(json.dumps(
                                    get_word_meaning_paradigm_adjective_comparison(api_key, word_dict["wordId"],
                                                                                   word_dict["value"]),
                                    ensure_ascii=False) + ",\n")
    except Exception as e:
        if "Caused by ConnectTimeoutError" in str(e):
            continuing_after_error(original_data_file_name, with_error_file_name, api_key)
        print(f"Error occurred while continuing after error: {e}")


def custom_json_file_copyer(input_file_name: str, output_file_name: str):
    """Function can be freely changed if copying until certain wordId is needed."""
    with open(input_file_name + '.json', 'r') as input_file, open(output_file_name + '.json', 'w') as output_file:
        try:
            output_file.write('[\n')
            for line in input_file:
                if line_convertor_to_dict(line):
                    word_dict = line_convertor_to_dict(line)
                    if word_dict["wordId"] == 172630:
                        output_file.write(json.dumps(word_dict, ensure_ascii=False) + "\n")
                        output_file.write(']')
                        break
                    else:
                        output_file.write(json.dumps(word_dict, ensure_ascii=False) + ",\n")
        except Exception as e:
            print(f"Error occurred while reading-writing compound verbs: {e}")


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
                            forms_html += f'<idx:iform value="{form}" exact="yes"/> </idx:iform> '
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
                    output_file.write(kindlegen_recommended_replacements(word_html))
            output_file.write("</mbp:frameset>" + "\n" + '<section/>' + "\n" + "</body>" + "\n" + "</html>")
        except Exception as e:
            print(f"Error occur while converting json file to xhtml: {e}")


# def test_write_to_json_file(output_file_name: str, compound_verbs_list_file_name: str, sorter_func=None):
#     """Can be used to write to json file list of dicts as a global variable called testing_data. Good for testing
#     purposes. It also creates by default other json file for possible compound verbs. Can be freely modified."""
#     with open(output_file_name + '.json', 'w') as file, open(compound_verbs_list_file_name + '.json', 'w') as file2:
#         try:
#             file.write('[\n')
#             prev_data = None
#
#             for line in testing_data:
#                 if sorter_func is None or sorter_func(line):
#                     if prev_data is not None:
#                         file.write(json.dumps(prev_data, ensure_ascii=False))
#                         file.write(",\n")
#                     prev_data = line
#
#             if prev_data is not None:
#                 file.write(json.dumps(prev_data, ensure_ascii=False))
#
#             file.write('\n]')
#
#             file2.write(json.dumps(possible_compound_verbs, ensure_ascii=False))
#
#         except Exception as e:
#             print(f"Other error occurred: {e}")


def kindlegen_recommended_replacements(word_html: str):
    new_word_html = word_html.replace("<eki-foreign>", "<i>").replace("</eki-foreign>", "</i>").replace(
        "<eki-highlight>", "<b>").replace("</eki-highlight>", "</b>").replace("<eki-sup>", "<sup>").replace(
        "</eki-sup>", "</sup>").replace("<eki-link", "<b").replace("</eki-link>", "</b>").replace('<idx:iform value=""></idx:iform>', "").replace("<idx:infl>\n</idx:infl>", "")
    return new_word_html


if __name__ == '__main__':
    #  It's recommended to use main block to call out functions one-by-one, so it's easier to debug and/or adjust code.
