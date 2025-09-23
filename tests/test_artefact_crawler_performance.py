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

import os
import shutil
import statistics
import tempfile
import time
import unittest
from pathlib import Path

import avid.common.artefact.defaultProps as ArtefactProps
from avid.common.artefact import similarityRelevantProperties
from avid.common.artefact.crawler import (
    DirectoryCrawler,
    _scan_directories,
    crawl_filter_by_filename,
    crawl_property_by_filename,
    crawl_property_by_path,
)
from avid.common.console_abstraction import Progress

similarityRelevantProperties.extend(["study_id", "series_id"])


def probe_func_performance(func, times=5, *args, **kwargs):
    """
    Run func(*args, **kwargs) n times and returns  a tuple of last results and basic stats.
    """
    results = []
    for _ in range(times):
        start = time.perf_counter()
        func_results = func(*args, **kwargs)
        end = time.perf_counter()
        results.append(end - start)

    return (
        func_results,
        {
            "runs": times,
            "mean": statistics.mean(results),
            "min": min(results),
            "max": max(results),
        },
    )


class TestCrawlerPerformance(unittest.TestCase):
    """Performance tests for the DirectoryCrawler. Also used for report."""

    @classmethod
    def setUpClass(cls):
        """Create a large test directory structure for performance testing."""
        cls.temp_dir = tempfile.mkdtemp(prefix="avid_crawler_perf_test_")
        cls.test_root = Path(cls.temp_dir)

        # Create a realistic medical imaging directory structure
        cls.num_patients = 30
        cls.num_studies_per_patient = 5
        cls.num_series_per_study = 10
        cls.num_files_per_series = 50

        cls.total_dirs_expected = (
            (cls.num_patients * cls.num_studies_per_patient * cls.num_series_per_study)
            + (cls.num_patients * cls.num_studies_per_patient)
            + cls.num_patients
            + 1
        )  # + patient dirs + root

        cls.total_files_expected = (
            cls.num_patients
            * cls.num_studies_per_patient
            * cls.num_series_per_study
            * cls.num_files_per_series
        )

        print(
            f"Creating test structure with {cls.total_dirs_expected} directories "
            f"and {cls.total_files_expected} files..."
        )

        # Create directory structure: Patient -> Study -> Series -> Files
        for patient_id in range(1, cls.num_patients + 1):
            patient_dir = cls.test_root / f"Patient_{patient_id:03d}"
            patient_dir.mkdir()

            for study_id in range(1, cls.num_studies_per_patient + 1):
                study_dir = patient_dir / f"Study_{study_id:02d}"
                study_dir.mkdir()

                for series_id in range(1, cls.num_series_per_study + 1):
                    series_dir = study_dir / f"Series_{series_id:03d}"
                    series_dir.mkdir()

                    # Create files with realistic medical imaging naming patterns
                    for file_id in range(1, cls.num_files_per_series + 1):
                        # Mix of file types: DICOM, NIFTI, text reports
                        if (
                            file_id <= 0.9 * cls.num_files_per_series
                        ):  # Most files are DICOM
                            filename = f"IMG_{file_id:04d}.dcm"
                        else:  # Some text reports
                            filename = f"Report_{file_id:04d}.txt"

                        file_path = series_dir / filename
                        # Create small files with minimal content to speed up creation
                        file_path.write_text(
                            f"Test file {file_id} for patient {patient_id}"
                        )

    @classmethod
    def tearDownClass(cls):
        """Clean up the test directory structure."""
        if cls.temp_dir and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    @staticmethod
    @crawl_property_by_path(
        property_map={0: ArtefactProps.CASE, 1: "study_id", 2: "series_id"}
    )
    @crawl_property_by_filename(
        extraction_rules={ArtefactProps.TIMEPOINT: (r"_(\d+).", 0)}
    )
    @crawl_filter_by_filename(ext_exclude=(".tmp", ".log"))
    def performance_test_function(artefact_candidate, full_path, **kwargs):
        """Test function that simulates realistic artefact processing."""
        artefact_candidate[ArtefactProps.URL] = full_path
        artefact_candidate[ArtefactProps.INVALID] = False

        return artefact_candidate

    @staticmethod
    def dicom_break_delegate(entry_path: os.DirEntry) -> bool:
        """Stop scanning subdirs once we find a DICOM file."""
        return entry_path.is_file() and entry_path.name.endswith(".dcm")

    def test_process_performance(self):
        """Test crawling performance in different scenarios."""
        print(
            f"\nTesting single-process crawling of {self.total_files_expected} files "
            f"in {self.total_dirs_expected} directories..."
        )

        crawler = DirectoryCrawler(
            root_path=self.test_root,
            file_functor=self.performance_test_function,
            n_processes=1,
            replace_existing_artefacts=False,
        )

        artefacts, probe_single = probe_func_performance(crawler.getArtefacts)

        # Verify results
        self.assertEqual(len(artefacts), self.total_files_expected)
        self.assertEqual(crawler.number_of_last_irrelevant, 0)
        self.assertEqual(crawler.number_of_last_dropped, 0)

        # Performance metrics
        files_per_second_single = self.total_files_expected / probe_single["mean"]
        dirs_per_second_single = self.total_dirs_expected / probe_single["mean"]

        ###################################################
        # Test crawling performance with multiple processes.
        num_processes = min(4, os.cpu_count() or 1)
        print(f"\nTesting multi-process crawling with {num_processes} processes...")

        crawler = DirectoryCrawler(
            root_path=self.test_root,
            file_functor=self.performance_test_function,
            n_processes=num_processes,
            replace_existing_artefacts=False,
        )

        artefacts, probe_multi = probe_func_performance(crawler.getArtefacts)

        # Verify results
        self.assertEqual(len(artefacts), self.total_files_expected)
        self.assertEqual(crawler.number_of_last_irrelevant, 0)
        self.assertEqual(crawler.number_of_last_dropped, 0)

        # Performance metrics
        files_per_second_multi = self.total_files_expected / probe_multi["mean"]
        dirs_per_second_multi = self.total_dirs_expected / probe_multi["mean"]

        print(f"Single-process results:")
        print(
            f"  Total time (mean (min, max)): {probe_single['mean']:.2f} ({probe_single['min']:.2f},"
            f"{probe_single['max']:.2f}) seconds"
        )
        print(f"  Files per second (mean): {files_per_second_single:.1f}")
        print(f"  Directories per second (mean): {dirs_per_second_single:.1f}")

        print(f"Multi-process results ({num_processes} processes):")
        print(
            f"  Total time (mean (min, max)): {probe_multi['mean']:.2f} ({probe_multi['min']:.2f},"
            f"{probe_multi['max']:.2f}) seconds"
        )
        print(f"  Files per second (mean): {files_per_second_multi:.1f}")
        print(f"  Directories per second (mean): {dirs_per_second_multi:.1f}")
        print(
            f"  Speedup achieved (mean): {(probe_single['mean']/probe_multi['mean']):.1f}x"
        )

        # Basic performance assertion (should process at least 5000 files/sec on modern hardware)
        self.assertGreater(
            files_per_second_single,
            5000,
            "Crawler performance is unexpectedly slow (< 5000 files/sec)",
        )
        # Multi-process should generally be faster, but file I/O can be limiting factor
        self.assertGreater(
            files_per_second_multi,
            10000,
            "Multi-process crawler performance is unexpectedly slow",
        )

    def test_process_performance_scan_dir(self):
        """Test dir scanning performance in different scenarios."""

        print(f"\nTesting scan directory processes...")

        def scan_wo_break():
            with Progress(transient=True) as progress:
                directory_scanning = progress.add_task("Found folders to scan")
                for target_dir in _scan_directories(dir_path=self.test_root):
                    progress.update(directory_scanning, advance=1)

        artefacts, probe_wo_break = probe_func_performance(scan_wo_break)
        dirs_per_second = self.total_dirs_expected / probe_wo_break["mean"]

        print(f"\nTesting scan directory processes with break...")

        def scan_w_break():
            with Progress(transient=True) as progress:
                directory_scanning = progress.add_task("Found folders to scan")
                for target_dir in _scan_directories(
                    dir_path=self.test_root,
                    break_checker_delegate=TestCrawlerPerformance.dicom_break_delegate,
                ):
                    progress.update(directory_scanning, advance=1)

        artefacts, probe_w_break = probe_func_performance(scan_w_break)
        dirs_per_second_break = self.total_dirs_expected / probe_w_break["mean"]

        print(f"Scan directory results:")
        print(f"  Total time (mean): {probe_wo_break['mean']:.2f} seconds")
        print(f"  Directories per second: {dirs_per_second:.1f}")
        print(f"Scan directory results with break check:")
        print(f"  Total time (mean): {probe_w_break['mean']:.2f} seconds")
        print(f"  Directories per second: {dirs_per_second_break:.1f}")

        # Basic performance assertion (should process at least 100 files/sec on modern hardware)
        self.assertGreater(
            dirs_per_second,
            5000,
            "Scan performance is unexpectedly slow (< 5000 files/sec)",
        )
        self.assertGreater(
            dirs_per_second_break,
            20000,
            "Scan performance is unexpectedly slow (< 20000 files/sec)",
        )
        self.assertGreater(
            dirs_per_second_break,
            dirs_per_second,
            "Scan performance with break is unexpectedly slower",
        )


if __name__ == "__main__":
    unittest.main()
