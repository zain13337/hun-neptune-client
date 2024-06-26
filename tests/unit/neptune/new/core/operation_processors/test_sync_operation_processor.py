#
# Copyright (c) 2024, Neptune Labs Sp. z o.o.
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
from unittest.mock import Mock
from uuid import uuid4

from mock import patch

from neptune.constants import NEPTUNE_DATA_DIRECTORY
from neptune.core.operation_processors.sync_operation_processor import SyncOperationProcessor
from neptune.core.typing.container_type import ContainerType
from neptune.core.typing.id_formats import UniqueId


@patch("neptune.core.operation_processors.utils.random.choice")
@patch("neptune.core.operation_processors.sync_operation_processor.Path.mkdir")
@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile")
@patch("neptune.core.operation_processors.utils.os.getpid", return_value=42)
def test_setup(_, __, operation_storage_mock, mkdir_mock, random_choice_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    random_choice_mock.side_effect = tuple("abcdefgh")

    # and
    op_storage = operation_storage_mock.return_value

    # and
    processor = SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # then
    mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)

    # and
    assert (
        processor.data_path
        == Path(NEPTUNE_DATA_DIRECTORY) / "sync" / f"{container_type.value}__{container_id}__42__abcdefgh"
    )

    # and
    assert processor.operation_storage == op_storage


@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile")
def test_flush(metadata_file_mock, operation_storage_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value

    # and
    processor = SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # and
    processor.start()

    # when
    processor.flush()

    # then
    metadata_file.flush.assert_called_once()
    operation_storage.flush.assert_called_once()


@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile")
def test_close(metadata_file_mock, operation_storage_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value

    # and
    processor = SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # and
    processor.start()

    # when
    processor.close()

    # then
    metadata_file.close.assert_called_once()
    operation_storage.close.assert_called_once()


@patch("neptune.core.operation_processors.sync_operation_processor.Path.rmdir")
@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile")
def test_stop(metadata_file_mock, operation_storage_mock, rmdir_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    metadata_file = metadata_file_mock.return_value
    operation_storage = operation_storage_mock.return_value

    # and
    processor = SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # and
    processor.start()

    # when
    processor.stop()

    # then
    metadata_file.flush.assert_called_once()
    operation_storage.flush.assert_called_once()

    # and
    metadata_file.close.assert_called_once()
    operation_storage.close.assert_called_once()

    # and
    operation_storage.cleanup.assert_called()
    metadata_file.cleanup.assert_called()

    # and
    rmdir_mock.assert_called_once()


@patch("neptune.core.operation_processors.sync_operation_processor.Path.rmdir", side_effect=OSError)
@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage", new=Mock)
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile", new=Mock)
def test_cleanup_oserror_not_raising_toplevel_exception(rmdir_mock):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # and
    processor = SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # when
    processor.cleanup()  # no exception raised

    # and
    rmdir_mock.assert_called_once()


@patch("neptune.core.operation_processors.sync_operation_processor.OperationStorage")
@patch("neptune.core.operation_processors.sync_operation_processor.MetadataFile")
def test_metadata(metadata_file_mock, _):
    # given
    container_id = UniqueId(str(uuid4()))
    container_type = ContainerType.RUN

    # when
    SyncOperationProcessor(container_id=container_id, container_type=container_type)

    # then
    metadata = metadata_file_mock.call_args_list[0][1]["metadata"]
    assert metadata["mode"] == "sync"
    assert metadata["containerType"] == ContainerType.RUN
    assert metadata["containerId"] == container_id
