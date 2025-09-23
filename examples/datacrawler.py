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

import avid.common.artefact.defaultProps as ArtefactProps
from avid.common.artefact.crawler import (crawl_filter_by_filename,
                                          crawl_property_by_filename,
                                          crawl_property_by_path,
                                          runCrawlerScriptMain)


@crawl_filter_by_filename(filename_exclude="README.md")
@crawl_property_by_path(property_map={0: ArtefactProps.CASE})
@crawl_property_by_filename(extraction_rules={ArtefactProps.ACTIONTAG: (r"^([^_]+)", 'UNKNOWN'),
                                              ArtefactProps.TIMEPOINT: (r"_TP(\d+)", 0)})
def fileFunction(full_path, artefact_candidate, **kwargs):
    """
    Functor to generate an artefact for a file found by the crawler.
    Most of the work is already done be the decorators that ensure that the artefact_candidate is already populated
    based on information encoded in the file and name.
    """
    artefact_candidate[ArtefactProps.URL] = full_path
    artefact_candidate[ArtefactProps.TYPE] = ArtefactProps.TYPE_VALUE_RESULT
    return artefact_candidate


if __name__ == "__main__":
    runCrawlerScriptMain(fileFunction)