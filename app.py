import csv

import pathfinder

def read_pid2oid(link_path):
    """
    :param link_path: str, path to link CSV file containing patient ids and original ids
    :return: dict with patient ids as keys and the values are the original ids
    """
    pid2oid = {}

    with open(link_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            pid2oid[row['patient_id']] = row['original_id']

    return pid2oid

def read_oid2pid(link_path):
    """
    :param link_path: str, path to link CSV file containing patient ids and original ids
    :return: dict with original ids as keys and the values are the patient ids
    """
    oid2pid = {}

    with open(link_path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            oid2pid[row['original_id']] = row['patient_id']

    return oid2pid




