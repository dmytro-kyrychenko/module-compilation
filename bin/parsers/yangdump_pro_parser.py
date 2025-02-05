# Copyright The IETF Trust 2021, All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Slavomir Mazur'
__copyright__ = 'Copyright The IETF Trust 2021, All Rights Reserved'
__license__ = 'Apache License, Version 2.0'
__email__ = 'slavomir.mazur@pantheon.tech'

import os


def _remove_duplicate_messages(result: str, module_name: str) -> str:
    """Same result messages are often found in the compilation result multiple times.
    This method filter out duplicate messages.
    """
    splitted_result = result.split('\n\n')
    unique_results_list = sorted(set(splitted_result), key=splitted_result.index)

    # NOTE - WORKAROUND: remove 'iana-if-type@2021-06-21.yang:128.3: warning(1054): Revision date has already been used'
    # from most compilation results
    # This can be removed in the future with the release of 'iana-if-type' revision
    # that will PASS the compilation.
    final_result = []
    for result in unique_results_list:
        if 'iana-if-type@2021-06-21' not in result and 'iana-if-type' not in module_name:
            final_result.append(result)

    return '\n\n'.join(final_result)


class YangdumpProParser:
    def __init__(self, debug_level: int = 0):
        self._debug_level = debug_level
        self._yangdump_exec = 'yangdump-pro'

    def run_yumadumppro(self, yang_file_path: str, workdir: str, allinclusive: bool = False):
        """
        Run yumadump-pro on the YANG model.

        Arguments:
            :param yang_file_path   (str) Full path to the yang model to parse
            :param workdir          (str) Root directory where to find the source YANG models
            :param allinclusive     (bool) Whether the 'yangpath' directory contains all imported YANG modules or not
        :return: the outcome of the yangdump-pro compilation.
        """
        workdir = os.path.dirname(yang_file_path)
        os.chdir(workdir)

        if allinclusive:
            config_command = '--config=/etc/yumapro/yangdump-pro-allinclusive.conf'
        else:
            config_command = '--config=/etc/yumapro/yangdump-pro.conf'

        bash_command = [self._yangdump_exec, config_command, yang_file_path, '2>&1']
        if self._debug_level > 0:
            print('DEBUG: running command {}'.format(' '.join(bash_command)))

        # Modify command output
        try:
            result_yumadump = os.popen(' '.join(bash_command)).read()
            result_yumadump = result_yumadump.strip()
            result_yumadump = result_yumadump.split('\n\n***')[0]

            final_result = _remove_duplicate_messages(result_yumadump, yang_file_path)
        except Exception:
            final_result = 'Problem occured while running command: {}'.format(' '.join(bash_command))

        return final_result
