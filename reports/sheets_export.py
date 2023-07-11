import os
import csv

REPORT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./kg_cypher_report.csv")
ANNOTATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./cluster_annotation_CS202210140.tsv")

OLS_URL = "https://www.ebi.ac.uk/ols4/ontologies/cl/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F"


def read_csv_to_dict(csv_path, id_column=0, id_column_name="", delimiter=",", id_to_lower=False, generated_ids=False):
    """
    Reads tsv file content into a dict. Key is the first column value and the value is dict representation of the
    row values (each header is a key and column value is the value).
    Args:
        csv_path: Path of the CSV file
        id_column: Id column becomes the keys of the dict. This column should be unique. Default is the first column.
        id_column_name: Alternative to the numeric id_column, id_column_name specifies id_column by its header string.
        delimiter: Value delimiter. Default is comma.
        id_to_lower: applies string lowercase operation to the key
        generated_ids: If 'True', uses row number as the key of the dict. Initial key is 0.

    Returns:
        Function provides two return values: first; headers of the table and second; the CSV content dict. Key of the
        content is the first column value and the values are dict of row values.
    """
    records = dict()

    headers = []
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        row_count = 0
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()
            if generated_ids:
                _id = row_count

            if row_count == 0:
                headers = row
                if id_column_name and id_column_name in headers:
                    id_column = headers.index(id_column_name)
            else:
                row_object = dict()
                for column_num, column_value in enumerate(row):
                    row_object[headers[column_num]] = column_value
                records[_id] = row_object

            row_count += 1

    return headers, records


headers, annotated_data = read_csv_to_dict(ANNOTATION_PATH, delimiter="\t")
print(headers)
records = list()
with open(REPORT_PATH) as fd:
    rd = csv.reader(fd, quotechar='"')
    for row in rd:
        records.append(row)

with open(REPORT_PATH.replace(".csv", "_sheets.csv"), mode='w') as out:
    writer = csv.writer(out, quotechar='"')
    writer.writerow(["accession_id", "PCL_id", "label", "Class auto-annotation", "cl_parent_1", "cl_parent_2", "cl_parent_3", "cl_parent_4", "definition", "definition_ref", "brain_region", "brain_region_curie", "brain_region_evidence", "markers", "marker_fbeta_score"])

    line_num = 0
    for row in records:
        # skip first line
        if line_num > 0:
            accession_id = row[0]
            annot_table_cluster_id = int(accession_id.split("_")[1]) - 1
            class_annotation = annotated_data[str(annot_table_cluster_id)]["Class auto-annotation"]

            head_columns = row[:3]
            tail_columns = row[5:]

            new_row = head_columns
            new_row.append(class_annotation)

            cl_parent_names = row[3].split(",")
            cl_parents = row[4].split(",")
            for i in range(4):
                if len(cl_parent_names) > i:
                    ols_link = OLS_URL + cl_parents[i].strip().replace(":", "_")
                    new_row.append("=HYPERLINK(\""+ols_link+"\";\""+cl_parent_names[i].strip()+"\")")
                else:
                    new_row.append("")

            new_row.extend(tail_columns)
            writer.writerow(new_row)
        line_num = line_num + 1
