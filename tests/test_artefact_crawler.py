# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from pathlib import Path

import avid.common.artefact.defaultProps as ArtefactProps
from avid.common.artefact import Artefact, ArtefactCollection
from avid.common.artefact.crawler import (DirectoryCrawler,
                                          crawl_filter_by_filename,
                                          crawl_property_by_filename,
                                          crawl_property_by_path)


class TestFileFunctorFactory:
    def __init__(self):
        self._special_prop = -1 #start at -1 as factory test of crwaler also invoke __call__

    class Functor:
        def __init__(self, special_prop):
            self._special_prop = special_prop

        @crawl_property_by_path(property_map={0: ArtefactProps.CASE})
        @crawl_property_by_filename(extraction_rules={ArtefactProps.ACTIONTAG: (r"^([^_]+)", 'UNKNOWN'),
                                                      ArtefactProps.TIMEPOINT: (r"_TP(\d+)", 0)})
        def __call__(self, artefact_candidate, full_path, **kwargs):
            artefact_candidate[ArtefactProps.URL] = full_path
            artefact_candidate[ArtefactProps.INVALID] = False
            artefact_candidate["special_prop"] = str(self._special_prop)
            return artefact_candidate

    def __call__(self):
        self._special_prop += 1
        return TestFileFunctorFactory.Functor(special_prop=self._special_prop)

class TestArtefactCrawler(unittest.TestCase):
    def setUp(self):
        self.dummy_path_parts = ["partA", "partB"]
        self.dummy_filename = "Case_A_TS1.txt"
        self.dummy_full_path = "/partA/partB/Case_A_TS1.txt"
        self.artefact_candidate = Artefact()
        self.artefact_candidate[ArtefactProps.CASE] = "dummy"
        self.artefact_candidate[ArtefactProps.TIMEPOINT] = 1
        self.artefact_candidate[ArtefactProps.ACTIONTAG] = "test"
        self.artefact_candidate["custom2"] = 'my value'
        self.crawl_root_dir = Path(__file__).parent.parent / "examples" / "data"

    def test_filter_by_filename_exclude(self):
        @crawl_filter_by_filename(filename_exclude="badfile.txt")
        def func(**kwargs): return "CALLED"

        result = func(filename="badfile.txt")
        self.assertIsNone(result)

        result = func(filename="good.txt")
        self.assertEqual(result, "CALLED")

    def test_filter_by_filename_ext_include(self):
        @crawl_filter_by_filename(ext_include=(".txt",))
        def func(**kwargs): return "CALLED"

        result = func(filename="file.txt")
        self.assertEqual(result, "CALLED")

        result = func(filename="excluded.png")
        self.assertIsNone(result)

    def test_filter_by_filename_ext_exclude(self):
        @crawl_filter_by_filename(ext_exclude=(".bad",))
        def func(**kwargs): return "CALLED"

        result = func(filename="file.txt")
        self.assertEqual(result, "CALLED")

        result = func(filename="excluded.bad")
        self.assertIsNone(result)

    def test_filter_by_filename_ext_include_and_exclude(self):
        @crawl_filter_by_filename(ext_include=(".txt",), ext_exclude=(".bad",))
        def func(**kwargs): return "CALLED"

        result = func(filename="file.txt")
        self.assertEqual(result, "CALLED")

        result = func(filename="undefined.png")
        self.assertIsNone(result)

        result = func(filename="excluded.bad")
        self.assertIsNone(result)

    def test_property_by_path_add_none(self):
        @crawl_property_by_path({-1: ArtefactProps.CASE, 0: ArtefactProps.TIMEPOINT, 1: "custom", 4: "unkown"}, add_none=True)
        def func(**kwargs): return kwargs["artefact_candidate"]

        artefact = func(path_parts=self.dummy_path_parts)
        self.assertEqual(artefact[ArtefactProps.CASE], self.dummy_path_parts[-1])
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], self.dummy_path_parts[0])
        self.assertEqual(artefact['custom'], self.dummy_path_parts[1])
        self.assertIsNone(artefact['unkown'])

        #check with candidate already passed
        artefact = func(path_parts=self.dummy_path_parts, artefact_candidate=self.artefact_candidate)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "test")
        self.assertEqual(artefact[ArtefactProps.CASE], self.dummy_path_parts[-1])
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], self.dummy_path_parts[0])
        self.assertEqual(artefact['custom'], self.dummy_path_parts[1])
        self.assertEqual(artefact['custom2'], 'my value')
        self.assertIsNone(artefact['unkown'])


    def test_property_by_path(self):
        @crawl_property_by_path({-1: ArtefactProps.CASE, 0: ArtefactProps.TIMEPOINT, 1: "custom", 4: "unkown"}, add_none=False)
        def func(**kwargs): return kwargs["artefact_candidate"]

        artefact = func(path_parts=self.dummy_path_parts)
        self.assertEqual(artefact[ArtefactProps.CASE], self.dummy_path_parts[-1])
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], self.dummy_path_parts[0])
        self.assertEqual(artefact['custom'], self.dummy_path_parts[1])
        self.assertNotIn('unkown', artefact)

        #check with candidate already passed
        artefact = func(path_parts=self.dummy_path_parts, artefact_candidate=self.artefact_candidate)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "test")
        self.assertEqual(artefact[ArtefactProps.CASE], self.dummy_path_parts[-1])
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], self.dummy_path_parts[0])
        self.assertEqual(artefact['custom'], self.dummy_path_parts[1])
        self.assertEqual(artefact['custom2'], 'my value')
        self.assertNotIn('unkown', artefact)

    def test_property_by_filename_with_regex(self):
        rules = {
            ArtefactProps.CASE: (r"Case_(\w+)_", "unknown"),
            ArtefactProps.TIMEPOINT: (r"TS(\d+)", 99),
            "custom2": (r"NO_MATCH(\d+)", None),
        }

        @crawl_property_by_filename(rules, add_none=False)
        def func(**kwargs): return kwargs["artefact_candidate"]

        artefact = func(filename=self.dummy_filename)
        self.assertEqual(artefact[ArtefactProps.CASE], "A")
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], 1)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "unknown_tag")
        self.assertNotIn('custom2', artefact)

        artefact = func(filename=self.dummy_filename, artefact_candidate=self.artefact_candidate)
        self.assertEqual(artefact[ArtefactProps.CASE], "A")
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], 1)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "test")
        self.assertEqual(artefact['custom2'], "my value")

    def test_property_by_filename_with_regex_add_none(self):
        rules = {
            ArtefactProps.CASE: (r"Case_(\w+)_", "unknown"),
            ArtefactProps.TIMEPOINT: (r"TS(\d+)", 99),
            "custom2": (r"NO_MATCH(\d+)", None),
        }

        @crawl_property_by_filename(rules, add_none=True)
        def func(**kwargs): return kwargs["artefact_candidate"]

        artefact = func(filename=self.dummy_filename)
        self.assertEqual(artefact[ArtefactProps.CASE], "A")
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], 1)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "unknown_tag")
        self.assertEqual(artefact['custom2'], None)

        artefact = func(filename=self.dummy_filename, artefact_candidate=self.artefact_candidate)
        self.assertEqual(artefact[ArtefactProps.CASE], "A")
        self.assertEqual(artefact[ArtefactProps.TIMEPOINT], 1)
        self.assertEqual(artefact[ArtefactProps.ACTIONTAG], "test")
        self.assertEqual(artefact['custom2'], None)

    @staticmethod
    @crawl_property_by_path(property_map={0: ArtefactProps.CASE})
    @crawl_property_by_filename(extraction_rules={ArtefactProps.ACTIONTAG: (r"^([^_]+)", 'UNKNOWN'),
                                                  ArtefactProps.TIMEPOINT: (r"_TP(\d+)", 0)})
    def simple_crawl_function(artefact_candidate, full_path, **kwargs):
        artefact_candidate[ArtefactProps.URL] = full_path
        artefact_candidate[ArtefactProps.INVALID] = False
        return artefact_candidate

    def test_directory_crawler(self):
        crawler = DirectoryCrawler(self.crawl_root_dir, self.simple_crawl_function, n_processes=1)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(6, len(artefacts))
        self.assertEqual(0, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(6, crawler.number_of_last_added)

    @staticmethod
    @crawl_property_by_filename(extraction_rules={ArtefactProps.ACTIONTAG: (r"^([^_]+)", 'UNKNOWN'),
                                                  ArtefactProps.TIMEPOINT: (r"_TP(\d+)", 0)})
    def duplicating_crawl_function(artefact_candidate, full_path, **kwargs):
        """this function will create dublicate artefacts, as we omitted the decoration that sets the case id.
        # so all artefacts will have the same case id.
        """
        artefact_candidate[ArtefactProps.URL] = full_path
        artefact_candidate[ArtefactProps.INVALID] = False
        return artefact_candidate

    def test_directory_crawler_with_duplicates(self):
        crawler = DirectoryCrawler(self.crawl_root_dir, self.duplicating_crawl_function, n_processes=1)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(4, len(artefacts))
        self.assertEqual(2, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(4, crawler.number_of_last_added)

        crawler = DirectoryCrawler(self.crawl_root_dir, self.duplicating_crawl_function, n_processes=1,
                                   replace_existing_artefacts=False)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(4, len(artefacts))
        self.assertEqual(2, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(4, crawler.number_of_last_added)

        crawler = DirectoryCrawler(self.crawl_root_dir, self.duplicating_crawl_function, n_processes=1,
                                   replace_existing_artefacts=True)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(4, len(artefacts))
        self.assertEqual(0, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(2, crawler.number_of_last_overwites)
        self.assertEqual(4, crawler.number_of_last_added)

    @staticmethod
    @crawl_filter_by_filename(ext_exclude=('txt',))
    def excluding_crawl_function(artefact_candidate, full_path, **kwargs):
        artefact_candidate[ArtefactProps.URL] = full_path
        artefact_candidate[ArtefactProps.INVALID] = False
        return artefact_candidate

    def test_directory_crawler_irrelevant(self):
        crawler = DirectoryCrawler(self.crawl_root_dir, self.excluding_crawl_function, n_processes=1)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(1, len(artefacts))
        self.assertEqual(0, crawler.number_of_last_dropped)
        self.assertEqual(5, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(1, crawler.number_of_last_added)

    def test_directory_crawler_with_function_factory(self):
        class Factory:
            def __call__(self):
                return TestArtefactCrawler.simple_crawl_function

        crawler = DirectoryCrawler(self.crawl_root_dir, Factory(), n_processes=1)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(6, len(artefacts))
        self.assertEqual(0, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(6, crawler.number_of_last_added)

    def test_directory_crawler_with_functor_factory(self):
        crawler = DirectoryCrawler(self.crawl_root_dir, TestFileFunctorFactory(), n_processes=1)
        artefacts = crawler.getArtefacts()
        self.assertIsInstance(artefacts, ArtefactCollection)
        self.assertEqual(6, len(artefacts))
        self.assertEqual(0, crawler.number_of_last_dropped)
        self.assertEqual(0, crawler.number_of_last_irrelevant)
        self.assertEqual(0, crawler.number_of_last_overwites)
        self.assertEqual(6, crawler.number_of_last_added)

        #check if there were different factories used per directory
        for artefact in artefacts:
            correct_factory_per_path = (artefact[ArtefactProps.CASE] is None and artefact['special_prop'] == '1')\
                                       or (artefact[ArtefactProps.CASE] == 'pat1' and artefact['special_prop'] == '3')\
                                       or (artefact[ArtefactProps.CASE] == 'pat2' and artefact['special_prop'] == '2')
            self.assertTrue(correct_factory_per_path)



if __name__ == "__main__":
    unittest.main()