#
# Copyright (c) 2023, Neptune Labs Sp. z o.o.
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
from pathlib import Path
from uuid import uuid4

from mock import (
    MagicMock,
    patch,
)

from neptune.constants import NEPTUNE_DATA_DIRECTORY
from neptune.core.operation_processors.offline_operation_processor import OfflineOperationProcessor
from neptune.internal.container_type import ContainerType
from neptune.internal.id_formats import UniqueId


@patch("neptune.internal.operation_processors.utils.random.choice")
@patch("neptune.core.operation_processors.offline_operation_processor.Path.mkdir")
@patch("neptune.core.operation_processors.offline_operation_processor.DiskQueue")
@patch("neptune.core.operation_processors.offline_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.offline_operation_processor.MetadataFile")
@patch("neptune.internal.operation_processors.utils.os.getpid", return_value=42)
def test_setup(_, __, ___, ____, mkdir_mock, random_choice_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    random_choice_mock.side_effect = tuple("abcdefgh")

    # and
    processor = OfflineOperationProcessor(container_id=container_id, container_type=container_type, lock=MagicMock())

    # then
    mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)

    # and
    assert (
        processor.data_path
        == Path(NEPTUNE_DATA_DIRECTORY) / "offline" / f"{container_type.value}__{container_id}__42__abcdefgh"
    )


@patch("neptune.core.operation_processors.offline_operation_processor.DiskQueue")
@patch("neptune.core.operation_processors.offline_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.offline_operation_processor.MetadataFile")
def test_flush(metadata_file_mock, operation_storage_mock, disk_queue_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value
    disk_queue = disk_queue_mock.return_value

    # and
    processor = OfflineOperationProcessor(container_id=container_id, container_type=container_type, lock=MagicMock())

    # and
    processor.start()

    # when
    processor.flush()

    # then
    disk_queue.flush.assert_called_once()
    operation_storage.flush.assert_called_once()
    metadata_file.flush.assert_called_once()


@patch("neptune.core.operation_processors.offline_operation_processor.DiskQueue")
@patch("neptune.core.operation_processors.offline_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.offline_operation_processor.MetadataFile")
def test_close(metadata_file_mock, operation_storage_mock, disk_queue_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value
    disk_queue = disk_queue_mock.return_value

    # and
    processor = OfflineOperationProcessor(container_id=container_id, container_type=container_type, lock=MagicMock())

    # and
    processor.start()

    # when
    processor.close()

    # then
    disk_queue.close.assert_called_once()
    operation_storage.close.assert_called_once()
    metadata_file.close.assert_called_once()


@patch("neptune.core.operation_processors.offline_operation_processor.DiskQueue")
@patch("neptune.core.operation_processors.offline_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.offline_operation_processor.MetadataFile")
def test_stop(metadata_file_mock, operation_storage_mock, disk_queue_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value
    disk_queue = disk_queue_mock.return_value

    # and
    processor = OfflineOperationProcessor(container_id=container_id, container_type=container_type, lock=MagicMock())

    # and
    processor.start()

    # when
    processor.stop()

    # then
    disk_queue.flush.assert_called_once()
    operation_storage.flush.assert_called_once()
    metadata_file.flush.assert_called_once()

    # and
    disk_queue.close.assert_called_once()
    operation_storage.close.assert_called_once()
    metadata_file.close.assert_called_once()

    # and
    operation_storage.cleanup.assert_not_called()
    disk_queue.cleanup.assert_not_called()
    metadata_file.cleanup.assert_not_called()


@patch("neptune.core.operation_processors.offline_operation_processor.DiskQueue")
@patch("neptune.core.operation_processors.offline_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.offline_operation_processor.MetadataFile")
def test_metadata(metadata_file_mock, _, __):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # when
    OfflineOperationProcessor(container_id=container_id, container_type=container_type, lock=MagicMock())

    # then
    metadata = metadata_file_mock.call_args_list[0][1]["metadata"]
    assert metadata["mode"] == "offline"
    assert metadata["containerType"] == ContainerType.RUN
    assert metadata["containerId"] == container_id
