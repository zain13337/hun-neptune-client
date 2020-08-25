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

from .experiment import Experiment
from .internal.async_operation_processor import AsyncOperationProcessor
from .internal.containers.disk_queue import DiskQueue
from .internal.neptune_backend_mock import NeptuneBackendMock
from .internal.operation import VersionedOperation
from .internal.sync_operation_processor import SyncOperationProcessor


def init(connection_mode: str = "async", flush_period: float = 5) -> Experiment:
    backend = NeptuneBackendMock()
    exp_uuid = backend.create_experiment()

    if connection_mode == "async":
        operation_processor = AsyncOperationProcessor(
            DiskQueue(".neptune/{}".format(exp_uuid),
                      "operations",
                      VersionedOperation.to_dict,
                      VersionedOperation.from_dict),
            backend,
            sleep_time=flush_period)
    elif connection_mode == "sync":
        operation_processor = SyncOperationProcessor(backend)
    elif connection_mode == "offline":
        operation_processor = SyncOperationProcessor(backend)
    else:
        raise ValueError('connection_mode should be on of ["async", "sync", "offline"]')

    return Experiment(exp_uuid, backend, operation_processor)
