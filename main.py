import xmltodict
import os
import json
import pandas as pd


def get_info(file_name, environment, values):
    print(f'get information from file {environment} {file_name}')
    with open(f'Configurations/config-{environment}/{file_name}', "rb") as file_xml:
        file_dict = xmltodict.parse(file_xml)
        # print(json.dumps(file_dict, indent=4))
        file_info = file_dict["standardizer"]
        organization = file_info["organization"]
        try:
            channel_list = file_info["channels"]["channel"]
            for channel in channel_list:
                channel_name = channel["@name"]
                channel_source = channel["@source"]
                channel_incremental = channel["@incremental"]
                channel_secondary = channel["@secondary"]
                channel_integration = channel["selectPayloads"]["integrationArtifactId"]
                try:
                    if "name" in channel["selectPayloads"]["annotation"]:
                        channel_annotation_name = channel["selectPayloads"]["annotation"]["name"]
                        # print(channel_annotation_name)
                    else:
                        channel_annotation_name_list = channel["selectPayloads"]["annotation"]
                        annotation_name_list = []
                        for name in channel_annotation_name_list:
                            if "name" in name:
                                annotation_name_list.append(name["name"])
                                # channel_annotation_name = name["name"]
                                # print (channel_annotation_name, "2")
                            else:
                                channel_annotation_name = "-"
                        channel_annotation_name = annotation_name_list
                except:
                    channel_annotation_name = "-"
                try:
                    if "@type" in channel["selectPayloads"]["annotation"]:
                        channel_annotation_type = channel["selectPayloads"]["annotation"]["@type"]
                        # print("1")
                    elif isinstance(channel["selectPayloads"]["annotation"], list):
                        channel_annotation_type_list = channel["selectPayloads"]["annotation"]
                        annotation_type_list = []
                        # print("2")
                        for type in channel_annotation_type_list:
                            if "@type" in type:
                                annotation_type_list.append(type["@type"])
                                # channel_annotation_type = type["@type"]
                                # print("3")
                            else:
                                channel_annotation_type = "-"
                        # print("4")
                        channel_annotation_type = annotation_type_list

                    else:
                        channel_annotation_type = "-"
                        # print("5")
                except:
                    channel_annotation_type = "-"
                try:
                    if "value" in channel["selectPayloads"]["annotation"]:
                        channel_annotation_value = channel["selectPayloads"]["annotation"]["value"]
                    else:
                        channel_annotation_value_list = channel["selectPayloads"]["annotation"]
                        annotation_value_list = []
                        for value in channel_annotation_value_list:
                            if "value" in value:
                                annotation_value_list.append(value["value"])
                                # channel_annotation_value = value["value"]
                            else:
                                channel_annotation_value = "-"
                        channel_annotation_value = annotation_value_list
                except:
                    channel_annotation_value = "-"
                if "parserHints" in channel:
                    channel_rowOffset = channel["parserHints"]["tableRowOffset"]
                else:
                    channel_rowOffset = "-"
                try:
                    if "transformerClass" in channel:
                        channel_transformerClass = channel["transformerClass"]
                    else:
                        channel_transformerClass = "-"
                except:
                    channel_transformerClass_list = channel["transformerClass"]
                    for form in channel_transformerClass_list:
                        channel_transformerClass = form
                values.append([environment, organization, channel_name, channel_source, channel_incremental, channel_secondary, channel_integration, channel_annotation_name,
                               channel_annotation_type, channel_annotation_value, channel_rowOffset, channel_transformerClass])

        except Exception as e:
            print(e)
            channel_name = "-"
            channel_source = "-"
            channel_incremental = "-"
            channel_secondary = "-"
            channel_integration = "-"
            channel_annotation_type = "-"
            channel_annotation_name = "-"
            channel_annotation_value = "-"
            channel_rowOffset = "-"
            channel_transformerClass = "-"
            values.append([environment, organization, channel_name, channel_source, channel_incremental, channel_secondary, channel_integration,
                           channel_annotation_type, channel_annotation_name, channel_annotation_value, channel_rowOffset, channel_transformerClass])


def list_to_string(df_column_list):
    for i, item in enumerate(df_column_list):
        if isinstance(item, list):
            item_string = ", ".join(item)
            df_column_list[i] = item_string


def transformer_class_cleaner(df_column_list):
    for i, string in enumerate(df_column_list):
        if isinstance(string, str) and "team.si.stan.core.transformers." in string:
            clean_string = string.replace("team.si.stan.core.transformers.", "")
            df_column_list[i] = clean_string


files_list_staging = os.listdir(r"Configurations/config-staging")
files_list_qa = os.listdir(r"Configurations/config-qa")

columns = ["environment", "organization", "channelName", "source", "incremental", "secondary",
           "integrationArtifactId", "annotationName", "annotationType", "annotationValue", "parserHints", "transformerClass"]
values = []

staging = "staging"
qa = "qa"
    
for file_staging in files_list_staging:
    get_info(file_staging, staging, values)

for file_qa in files_list_qa:
    get_info(file_qa, qa, values)

df = pd.DataFrame(columns=columns, data=values)

list_to_string(df["annotationName"])
list_to_string(df["annotationType"])
list_to_string(df["annotationValue"])

def clean_transformer_extended(row):
    transformer_classes = row['transformerClass']
    if isinstance(transformer_classes, list):
        new_rows = []
        for transformer_class in transformer_classes:
            transformer_class = transformer_class.replace("team.si.stan.core.transformers.", "") if isinstance(transformer_class, str) else transformer_class
            new_row = row.copy()
            new_row['transformerClass'] = transformer_class
            new_rows.append(new_row)
        return new_rows
    else:
        if isinstance(transformer_classes, str) and "team.si.stan.core.transformers." in transformer_classes:
            row['transformerClass'] = transformer_classes.replace("team.si.stan.core.transformers.", "")
        return [row]

expanded_rows = []
for _, row in df.iterrows():
    expanded_rows.extend(clean_transformer_extended(row))

expanded_df = pd.DataFrame(expanded_rows, columns=columns)

# Save the expanded DataFrame to an Excel file
expanded_df.to_excel("channels_config.xlsx", index=False)