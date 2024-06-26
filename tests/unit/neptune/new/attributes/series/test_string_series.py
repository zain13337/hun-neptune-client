#
# Copyright (c) 2020, Neptune Labs Sp. z o.o.
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
import pytest
from mock import (
    MagicMock,
    patch,
)

from neptune.attributes.series.string_series import StringSeries
from neptune.exceptions import NeptuneUnsupportedFunctionalityException
from tests.unit.neptune.new.attributes.test_attribute_base import TestAttributeBase


@patch("time.time", new=TestAttributeBase._now)
class TestStringSeries(TestAttributeBase):
    def test_assign_type_error(self):
        values = [55, "string", None]
        for value in values:
            with self.assertRaises(Exception):
                StringSeries(MagicMock(), MagicMock()).assign(value)

    @pytest.mark.xfail(reason="fetch_last disabled", strict=True, raises=NeptuneUnsupportedFunctionalityException)
    def test_get(self):
        with self._exp() as exp:
            var = StringSeries(exp, self._random_path())
            var.log("asdfhadh")
            var.log("hej!")
            self.assertEqual("hej!", var.fetch_last())

    @pytest.mark.xfail(reason="fetch_last disabled", strict=True, raises=NeptuneUnsupportedFunctionalityException)
    def test_log(self):
        with self._exp() as exp:
            var = StringSeries(exp, self._random_path())
            var.log([str(val) for val in range(0, 5000)])
            self.assertEqual("4999", var.fetch_last())
            values = list(var.fetch_values()["value"].array)
            expected = list(range(0, 5000))
            self.assertEqual(len(set(expected)), len(set(values)))
