import unittest
from generate_patient_data import read_psv, generate_evt_dict, generate_info_dict, demographic_filter, event_filter, \
    cal_timeline, cal_age, cal_median


class TestGeneratePatientData(unittest.TestCase):

    def test_read_psv(self):
        self.assertEqual(read_psv("unittest.psv"),
                         [["patient_id", "birth_date", "gender"],
                          ["id-771", "1981-12-20", "M"],
                          ["id-2477", "1948-06-21", "F"]])

    def test_generate_evt_dict(self):
        self.assertEqual(generate_evt_dict(["2014-03-11", "10", "E43"]),
                         {"date": "2014-03-11", "system": "http://hl7.org/fhir/sid/icd-10", "code": "E43"})
        self.assertEqual(generate_evt_dict(["1997-12-11", "9", "3"]),
                         {"date": "1997-12-11", "system": "http://hl7.org/fhir/sid/icd-9-cm", "code": "3"})

    def test_generate_info_dict(self):
        test_demo_list = ["1959-10-09", "M"]
        test_evt_list = [["2015-04-17", "9", "V72.0"], ["2015-09-15", "9", "367.4"]]
        self.assertEqual(generate_info_dict(test_demo_list, test_evt_list),
                         {"birth_date": "1959-10-09", "gender": "M", "events": [{
                             "date": "2015-04-17",
                             "system": "http://hl7.org/fhir/sid/icd-9-cm",
                             "code": "V72.0"
                         }, {"date": "2015-09-15",
                             "system": "http://hl7.org/fhir/sid/icd-9-cm",
                             "code": "367.4"}]})

    def test_demographic_filter(self):
        test_demo1 = ["id-1234", "2015-07-01", "F"]
        test_demo2 = ["id_2345", "", "M"]
        test_demo3 = ["id_435"]
        self.assertEqual(demographic_filter(test_demo1), True)
        self.assertEqual(demographic_filter(test_demo2), False)
        self.assertEqual(demographic_filter(test_demo3), False)

    def test_event_filter(self):
        test_event1 = ["id-2398", "2016-01-27", "10", "V45.2"]
        test_event2 = ["id-28", "10", "V45.2"]
        test_event3 = ["id-2398", "2016-01-27", "", "V45.2"]
        self.assertEqual(event_filter(test_event1), True)
        self.assertEqual(event_filter(test_event2), False)
        self.assertEqual(event_filter(test_event3), False)

    def test_cal_timeline(self):
        test_data1 = [['1949-12-03', 'F'], [['2015-01-07', '9', 'V72.0']]]
        test_data2 = [['1949-12-03', 'F'], [['2015-01-07', '9', 'V72.0'], ['2017-01-07', '9', 'V72.0']]]
        self.assertEqual(cal_timeline(test_data1), 0)
        self.assertEqual(cal_timeline(test_data2), 731)

    def test_cal_age(self):
        test_data1 = [['1945-03-04', 'F'], [['2015-02-13', '9', '367.4']]]
        self.assertEqual(cal_age(test_data1), 70)
        test_data2 = [['1945-03-04', 'F'], [['2015-02-13', '9', '367.4'], ['2018-02-13', '9', '367.4']]]
        self.assertEqual(cal_age(test_data2), 73)

    def test_cal_median(self):
        test_data1 = []
        self.assertEqual(cal_median(test_data1), None)
        test_data2 = [3, 1, 2]
        self.assertEqual(cal_median(test_data2), 2)
        test_data3 = [3, 1, 2, 4]
        self.assertEqual(cal_median(test_data3), 2.5)

if __name__ == '__main__':
    unittest.main()

