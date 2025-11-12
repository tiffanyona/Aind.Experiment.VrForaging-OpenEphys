import pandas as pd

import os
from pathlib import Path
from xml.dom import minidom

# STRING MANAGEMENT

def date_converter(datestring):
    """Accepts a date string in the format M(M)/D(D)/Y(YYY) and converts it to YYYY-MM-DD"""

    month = ""
    day = ""
    year = ""
    ticker = 0
    for i in str(datestring):
        if i != "/" and ticker == 0:
            month = month + str(i)
        elif i != "/" and ticker == 1:
            day = day + str(i)
        elif i != "/" and ticker == 2:
            year = year + str(i)
        else:
            ticker += 1
    while len(day) < 2:
        day = "0" + str(day)
    while len(month) < 2:
        month = "0" + str(month)
    while len(year) < 4:
        year = "0" + str(year)
    return str(year) + "-" + str(month) + "-" + str(day)

def date_converter_no_dashes(datestring):
    """Accepts a date string in the format M(M)/D(D)/Y(YYY) and converts it to YYYYMMDD"""

    month = ""
    day = ""
    year = ""
    ticker = 0
    for i in str(datestring):
        if i != "/" and ticker == 0:
            month = month + str(i)
        elif i != "/" and ticker == 1:
            day = day + str(i)
        elif i != "/" and ticker == 2:
            year = year + str(i)
        else:
            ticker += 1
    while len(day) < 2:
        day = "0" + str(day)
    while len(month) < 2:
        month = "0" + str(month)
    while len(year) < 4:
        year = "0" + str(year)
    return str(year) + str(month) + str(day)

# TIME MANAGEMENT

def add_seconds_to_clock(sec, clock):
    """This function accepts any integer number of seconds (sec) and adds them to a 24-hour format time string (clock)\
    
    It will fail if the final answer should roll the clock over midnight"""

    clock_s = int(clock[-2:])
    clock_m = int(clock[-5:-3])
    clock_h = int(clock[-8:-6])

    converted_sum = (clock_h * 3600) + (clock_m * 60) + clock_s + sec

    hours = str(converted_sum // 3600)
    mins = str((converted_sum % 3600) // 60)
    secs = str(((converted_sum % 3600) % 60))

    while len(hours) < 2:
        hours = "0" + str(hours)
    while len(mins) < 2:
        mins = "0" + str(mins)
    while len(secs) < 2:
        secs = "0" + str(secs)

    return str(hours) + ":" + str(mins) + ":" + str(secs)

# FILE HANDLING

#FILE OPENING

def csv_opener(filepath):
    """Accepts file name and path as string and returns a dictionary"""

    data = pd.read_csv(filepath)
    return data.to_dict()

def get_insertion_details(csv_opener_output, setup_number):
    """Accepts an insertion or target dict (csv_opener output) & setup number and returns a dictionary where
    the keys are the column headings and the values are the appropriate data for that setup
    """

    new_dict = {}
    setup_index = None
    setup_number = str(setup_number)

    for i, j in csv_opener_output["Setup No"].items():
        #print(j)
        if str(j) == setup_number:
            setup_index = i
    assert setup_index is not None, "Setup number not found"
    for i in csv_opener_output.keys():
        new_dict[i] = csv_opener_output[i][setup_index]
    return new_dict

def xl_opener(filepath):
    """
    Turns an Excel spreadsheet into interpretable dicts
    
    Parameters
    ----------
    filename : str
                path of the .xlx file
    
    Returns
    -------
    Dictionary of dictionaries
    More specifically, of the form {sheet_index (int): dict}
    Where dict is of the form {column heading (str): list of values}
    """

    sheet_data = {}
    data = pd.ExcelFile(filepath)

    for sheet_index in range(len(data.sheet_names)):
        sheet_data[sheet_index] = (pd.read_excel(data, sheet_name=sheet_index)).to_dict()
    return sheet_data

def xml_opener(target_dict_list):
    """Accepts a list of target dictionaries and returns parsed settings.xml files in a two-element dictionary, with keys "recording" and
    "surface_finding". The values may be None if no data is found for either.
    """

    xml_bank = {"recording": None, "surface_finding": None}
    potential_folder_names = set()

    ### MAIN EPHYS RECORDING
    for i in range(len(target_dict_list)):
        potential_folder_names.add(str(target_dict_list[i]["OEPh Recording"]))

    options = os.listdir(os.path.abspath("D:/"))

    for j in potential_folder_names:
        #print("j: " + str(j))
        for k in options:
            #print("k: " + str(k))
            if j in k:
                # assert "settings_2.xml" not in os.listdir(
                #     os.path.abspath(
                #         "D:/" + str(k) + "/Record Node 101"
                #     )
                # ), "Multiple 'recording' settings.xml files found. To select one, comment out the assert statement in the xml_opener function and edit xml path."
                ### COMMENT ME OUT ^^^ AND EDIT THE PATH IN THE LINE BELOW TO REFLECT settings_2.xml OR SIMILAR
                xml_bank["recording"] = minidom.parse(
                    os.path.abspath(
                        "D:/"
                        + str(k)
                        + "/Record Node 101/settings.xml"
                    )
                )
    ### POSITIONAL / SURFACE FINDING

    potential_folder_names = set()
    for i in range(len(target_dict_list)):
        potential_folder_names.add(
            str(target_dict_list[i]["OEPh Positioning"])
        )
    
    for j in potential_folder_names:
        for k in options:
            if j in k:
                assert "settings_2.xml" not in os.listdir(
                    os.path.abspath(
                        "D:/" + str(k) + "/Record Node 101"
                    )
                ), "Multiple 'surface finding' settings.xml files found. To select one, comment out the assert statement in the xml_opener function and edit xml path."
                ### COMMENT ME OUT ^^^ AND EDIT THE PATH IN THE LINE BELOW TO REFLECT settings_2.xml OR SIMILAR
                xml_bank["surface_finding"] = minidom.parse(
                    os.path.abspath(
                        "D:/"
                        + str(k)
                        + "/Record Node 101/settings.xml"
                    )
                )

    return xml_bank

# FILE PARSING

def xml_attribute(xml, tag_name, index, attribute):
    """This function takes the following inputs:
    xml: an opened xml document object as input (use the output of xml_opener)
    tag_name: a tag name (e.g. NP_PROBE) as a string
    index: the integer index of the tag; index = 0 if you are trying to find the first probe (NP_PROBE) in the xml
    attribute: a desired attribute (e.g. probe_serial_number) as a string, whose value will be returned as an output
    """

    return (xml.getElementsByTagName(tag_name)[index]).getAttribute(attribute)

# MRI 

def mri_validation(subj_id):
    """
    Checks for relevant headframe registration files and returns their names
    
    Parameters
    ----------
    subj_id : str or int
    
    Returns
    -------
    Come back to this
    """

    gross_path = "Z:\ephys\persist\data\MRI\processed"
    subj_folder = os.path.abspath(str(gross_path) + "/" + str(subj_id))
    assert os.path.exists(subj_folder), "Folder for " + str(subj_id) + " not found in " + str(gross_path)
    
    possible_h5 = [
        str(subj_id) + "_com_plane.h5", 

    ]
    possible_npy = [
        str(subj_id) + "_ants_annotation_points.npy", 
        
    ]
    
    selections = []
    checkbox = [None, None]
    for item in os.listdir(subj_folder): 
        if item in possible_h5:
            selections.append(item)
            checkbox[0] = 1
        elif item in possible_npy:
            selections.append(item)
            checkbox[1] = 1

    assert checkbox[0] is not None, "Plane h5 file for " + str(subj_id) + " not found"
    assert checkbox[1] is not None, "Point annotations npy file for " + str(subj_id) + " not found"

    output_string = None
    for i in range(len(selections)):
        if i == 0:
            output_string = "." + str(selections[i])
        else:
            output_string = str(output_string) + "; ." + str(selections[i])
    
    return output_string
