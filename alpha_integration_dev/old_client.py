#
# Copyright (c) 2021, Neptune Labs Sp. z o.o.
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
#

"""Remember to set environment values:
* NEPTUNE_API_TOKEN
* NEPTUNE_PROJECT
"""
import sys
from datetime import datetime

import neptune
from common_client_code import ClientFeatures


class OldClientFeatures(ClientFeatures):
    def __init__(self):
        super().__init__()
        neptune.init()
        neptune.create_experiment(
            name='const project name',
            params=self.params,
            tags=['initial tag 1', 'initial tag 2'],
        )

    def modify_tags(self):
        neptune.append_tags('tag1')
        neptune.append_tag(['tag2_to_remove', 'tag3'])
        # neptune.remove_tag('tag2_to_remove')  # TODO: NPT-9222
        # neptune.remove_tag('tag4_remove_non_existing')  # TODO: NPT-9222

        exp = neptune.get_experiment()
        assert set(exp.get_tags()) == {'initial tag 1', 'initial tag 2', 'tag1', 'tag2_to_remove', 'tag3'}

    def modify_properties(self):
        neptune.set_property('prop', 'some text')
        neptune.set_property('prop_number', 42)
        neptune.set_property('nested/prop', 42)
        neptune.set_property('prop_to_del', 42)
        neptune.set_property('prop_list', [1, 2, 3])
        with open(self.text_file_path, mode='r') as f:
            neptune.set_property('prop_IO', f)
        neptune.set_property('prop_datetime', datetime.now())
        neptune.remove_property('prop_to_del')

        exp = neptune.get_experiment()
        properties = exp.get_properties()
        assert properties['prop'] == 'some text'
        assert properties['prop_number'] == '42'
        assert properties['nested/prop'] == '42'
        assert 'prop_to_del' not in properties
        assert properties['prop_IO'] == "<_io.TextIOWrapper name='alpha_integration_dev/data/text.txt'" \
                                        " mode='r' encoding='UTF-8'>"
        print(f'Properties: {properties}')

    def log_std(self):
        print('stdout text1')
        print('stdout text2')
        print('stderr text1', file=sys.stderr)
        print('stderr text2', file=sys.stderr)

    def log_series(self):
        # floats
        neptune.log_metric('m1', 1)
        neptune.log_metric('m1', 2)
        neptune.log_metric('m1', 3)
        neptune.log_metric('m1', 2)
        neptune.log_metric('nested/m1', 1)

        # texts
        neptune.log_text('m2', 'a')
        neptune.log_text('m2', 'b')
        neptune.log_text('m2', 'c')

        # images
        # `image_name` and `description` will be lost
        neptune.log_image('g_img', self.img_path, image_name='name', description='desc')
        neptune.log_image('g_img', self.img_path)

    def handle_files_and_images(self):
        """NPT-9207"""
        neptune.send_image('single_img', self.img_path, name='name', description='desc')
        neptune.send_image('single_img', self.img_path, name='name', description='desc')
        neptune.log_image('g_img', self.img_path, image_name='name', description='desc')
        # neptune.send_artifact(self.img_path, destination='single artifact')
        # neptune.log_artifact(self.img_path, destination='logged artifact')
        # neptune.log_artifact(self.img_path, destination='artifact to delete')
        # neptune.delete_artifacts('artifact to delete')

    def other(self):
        logs = neptune.get_experiment().get_logs()
        print(f'Logs: {logs}')

    def run(self):
        self.modify_tags()
        self.modify_properties()
        self.log_std()
        self.log_series()
        self.handle_files_and_images()

        self.other()


if __name__ == '__main__':
    OldClientFeatures().run()
