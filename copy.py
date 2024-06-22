# def test_dynamic_reader_from_flat_json(input_file_name: str):
#     with open(input_file_name + ".json", "r") as input_file:
#         try:
#             for line in input_file:
#                 if line[0] == "{":
#                     if line[-2] == ",":
#                         cut_dict = line[:-2]
#                         converted_dict = json.loads(cut_dict)
#                     else:
#                         cut_dict = line[:-1]
#                         converted_dict = json.loads(cut_dict)
#         except Exception as e:
#             return f"Error occurred while reading file: {e}"



# def convert_xml_to_xhtml(input_file, output_file):
#     parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
#     tree = etree.parse(input_file, parser)
#
#     xhtml_root = etree.Element("html", nsmap={
#         None: "http://www.w3.org/1999/xhtml",
#         "math": "http://www.w3.org/1998/Math/MathML",
#         "svg": "http://www.w3.org/2000/svg",
#     })
#
#     head = etree.SubElement(xhtml_root, "head")
#     body = etree.SubElement(xhtml_root, "body")
#
#     for element in tree.getroot():
#         body.append(element)
#
#     xhtml_str = etree.tostring(xhtml_root, pretty_print=True, xml_declaration=True, encoding='utf-8',
#                                doctype='<!DOCTYPE html>')
#
#     with open(output_file, 'wb') as xhtml_file:
#         xhtml_file.write(xhtml_str)



