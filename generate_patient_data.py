import json
from datetime import datetime


def read_psv(psv_file):
    """
    Read psv files.
    :param psv_file: a psv txt file. The target psv file that needs to be read.
    :return: a list. Contains the content in the psv_file.
    """

    content = []
    with open(psv_file, "r") as file:
        for line in file:
            file_fields = line.split("|")
            file_fields[-1] = str.strip(file_fields[-1])
            content.append(file_fields)

    return content


def generate_evt_dict(evt_list):
    """
    Convert the list of events into a dictionary.
    :param evt_list: a list. It contains one event for a patient.
    :return: a dictionary. It has three keys, which are date, system, and code, recording a patient's all
        valid diagosis information.
    """

    patient_evt_dict = {"date": evt_list[0], "code": evt_list[2]}
    if evt_list[1] == "9":
        patient_evt_dict["system"] = "http://hl7.org/fhir/sid/icd-9-cm"
    if evt_list[1] == "10":
        patient_evt_dict["system"] = "http://hl7.org/fhir/sid/icd-10"

    return patient_evt_dict


def generate_info_dict(demo_list, evts_list):
    """
    Generate a dictionary which is ready for JSON generation, and contains all valid info.
    :param demo_list: a list. It contains demographic information for a patient.
    :param evts_list: a list of lists. It contains all events for a patient.
    :return: a nested dictionary. It has three keys, birth_date, gender, and events. Contains all valid
        demographic information and event data for a patient. And the value for the key events is a list of
        dictionaries.
    """

    patient_dict = {"birth_date": demo_list[0], "gender": demo_list[1], "events": []}
    for evt in evts_list:
        patient_dict["events"].append(generate_evt_dict(evt))

    return patient_dict


def demographic_filter(d):
    """
    Filter out the invalid demographic data to make sure all the saved data have complete demograpic info.
    :param d: a list. It records a patient's id, birth_date and gender.
    :return: Bool. If the data is valid, return True. Otherwise, return False.
    """

    if "" not in d[1:] and len(d[1:]) == 2:
        return True

    return False


def event_filter(e):
    """
    Filter out the invalid event data to make sure all the saved data have complete event info.
    :param e: a list. It records one event for a patient.
    :return: Bool. If the data is valid, return True. Otherwise, return False.
    """

    if "" not in e[1:] and len(e[1:]) == 3:
        return True

    return False

# read demo.psv data, which contains patients' demographic data
demo = read_psv("demo.psv")

# read events.psv data, which contains patients' diagnosis data.
events = read_psv("events.psv")

# save patients' demographic data as a dictionary: demo_dict
# The key is patient_id, values are the birth_dates and gender.
demo_dict = {}
for d in demo[1:]:  # The first element of demo is the header.
    if demographic_filter(d):  # Only the patients have complete demographic info can be saved.
        demo_dict[d[0]] = d[1:]

# save patients' diagnosis data as a dictionary: events_dict
# The key is patient_id, values are the date, icd_version, and icd_code
events_dict = {}
for e in events[1:]:
    if event_filter(e):  # Only the events have complete event info can be saved.
        if e[0] in events_dict:
            events_dict[e[0]].append(e[1:])
        else:
            events_dict[e[0]] = [e[1:]]

# Merge demo_dict and events_dict into one dictionary, merged_dict, by using patient_id
# Merged_dict contains both demographic and event data of patients who appear in both demo_dict and events_dict.
merged_dict = {}
for k in demo_dict.keys() & events_dict.keys():
    merged_dict[k] = [demo_dict[k], events_dict[k]]

# Create one JSON file per patient. The file name is the patient_id.
for k, v in merged_dict.items():
    combine_dict = generate_info_dict(v[0], v[1])
    with open("patient/%s.json" % k, "w") as outfile:
        json.dump(combine_dict, outfile, indent=4)

# Statistics computation:
# The following code is used to compute the following statistics:
# - Total number of valid patients
# - Maximum/Minimun/Median length of patient time-lines in days
# - Count of males and females
# - Maximum/Minimum/Median age of patient as calculated between birthdate and last event in timeline.


def cal_timeline(p):
    """
    Calculate the time-line, which is the time span between the first event and the last event, for a patient.
    :param p: a list. It contains all valid info for a patient.
    :return: a int. The number of days between the first event and the last evnet.
    """
    event_dates = []
    for evt in p[1]:
        event_datetime = datetime.strptime(evt[0], "%Y-%m-%d")
        event_dates.append(event_datetime)
        timeline = (max(event_dates) - min(event_dates)).days

    return timeline


def cal_age(p):
    """
    Calculate the age for a patient. It is the number of years between the last event and birth date.
    :param p: a list. It contains all valid info for a patient.
    :return: a int. The age for a patient.
    """
    event_years = []
    birth_year = datetime.strptime(p[0][0], "%Y-%m-%d").year
    for e in p[1]:
        event_years.append(datetime.strptime(e[0], "%Y-%m-%d").year)
        last_year = max(event_years)
    age = last_year - birth_year

    return age


def cal_median(my_list):
    """
    Calculate median in a list of numbers.
    :param my_list: a list. A list of numbers.
    :return: a int or float. The median of the list.
    """
    if not my_list:
        return None

    my_list = sorted(my_list)
    if len(my_list) % 2 == 0:
        median = (my_list[int(len(my_list) / 2)] + my_list[int(len(my_list) / 2 - 1)]) / 2
    else:
        median = my_list[int(len(my_list) / 2)]

    return median


# Total number of patients.
num_patients = len(merged_dict)

# A list storing lengths of patient time-lines in days.
len_timelines = []
for v in merged_dict.values():
    len_timelines.append(cal_timeline(v))
median_timelines = cal_median(len_timelines)

# Number of males and females
num_males = 0
num_females = 0

for v in merged_dict.values():
    if str.lower(v[0][1]) == "m":
        num_males += 1
    if str.lower(v[0][1]) == "f":
        num_females += 1

# A list of ages of patients.
ages = []
for v in merged_dict.values():
    ages.append(cal_age(v))
median_age = cal_median(ages)

# Write the statistics into statistics.txt
with open("statistics.txt", "w") as file:
    print("Reset statistics.txt.")

with open("statistics.txt", "a") as outfile:
    outfile.write("The total number of valid patients is %d.\n" % num_patients)
    # The maximum length of patient timelines in days
    outfile.write("The maximum length of patient timelines is %d days.\n" % (max(len_timelines)))

    # The minimum length of patient timelines in days
    outfile.write("The minimum length of patient timelines is %d days.\n" % (min(len_timelines)))

    # The median length of patient timelines in days
    outfile.write("The median length of patient timelines is %d days.\n" % median_timelines)

    # Number of males and females
    outfile.write("The number of males is %d.\n" % num_males)
    outfile.write("The number of females is %d.\n" % num_females)

    # The maximum age of patient.
    outfile.write("The maximum age of patient is %d.\n" % (max(ages)))

    # The minimum age of patient.
    outfile.write("The minimum age of patient is %d.\n" % (min(ages)))

    # The median age of patient.
    outfile.write("The median age of patient is %d.\n" % median_age)
