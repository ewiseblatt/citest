# Copyright 2015 Google Inc. All Rights Reserved.
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


"""Specifies test cases using BaseAgents."""

import os
from ..base import JsonSnapshotableEntity


DEFAULT_PRUNE_OPERATION_CONTRACT_ON_SUCCESS=os.environ.get(
    'CITEST_PRUNE_OPERATION_CONTRACT_ON_SUCCESS', False)


class OperationContract(JsonSnapshotableEntity):
  """Specifies a testable operation and contract to verify it.

  This is essentially a "test case" using  BaseAgents.
  """
  @property
  def title(self):
    """The name of the test case."""
    return self.__operation.title

  @property
  def operation(self):
    """The AgentOperation to perform."""
    return self.__operation

  @property
  def contract(self):
    """The json.Contract to verify the operation."""
    return self.__contract

  @property
  def prune_snapshot_on_success(self):
    """Governs how this test (and executiosn of it) should be snapsshotted.

    If True then only include the proof of success, if in fact it succeeds.
    This can eliminate a substantial amount of superfluous data making
    reports more concise when success is typically not that interesting
    to consider further.
    """
    return self.__prune_snapshot_on_success

  @property
  def status_extractor(self):
    """The callable(OperationStatus, ExecutionContext) if any was bound.

    The status extractor can be used to observe the operation status
    and collect any information from it to populate the execution context with
    values obtained from the operation's result status. This is only useful
    if the contract contains clauses that use callable parameters that need
    information from result status, such as the identity of resources that
    were created.

    Typically this function is called by AgentTestCase fixture.run_test_case
    after the operation status completed and before the contract is verified.
    The AgentTestCase will populate the context with 'OperationStatus'.
    """
    return self.__status_extractor

  @property
  def cleanup(self):
    """An option cleanup method for the AgentTestCase to call when done.

    If not null, this is a callable(ExecutionContext). The
    AgentTestCase.run_test_case will add an 'OperationStatus' and
    'ContractVerifyResults' to the context before calling the cleanup.

    The cleanup can be used to perform any post-operation cleanup
    after the contract has been verified. It is called regardless of
    success or failure.
    """
    return self.__cleanup

  def export_to_json_snapshot(self, snapshot, entity):
    """Implements JsonSnapshotableEntity interface."""
    snapshot.edge_builder.make(entity, 'Operation', self.__operation)
    snapshot.edge_builder.make(entity, 'Contract', self.__contract)

  def __init__(self, operation, contract,
               status_extractor=None, cleanup=None,
               prune_snapshot_on_success=None):
    """Construct instance.

    Args:
      operation: [AgentOperation] To be performed.
      contract: [JsonContract] To verify operation.
      status_extractor: [Callable(OperationStatus, ExecutionContext)]
         See the status_extractor property for more information.
      cleanup: [Callable(ExecutionContext)]
         Perform any post-test cleanup.
      prune_snapshot_on_success: [bool] If True then attempt to remove
         superfluous failures and retry detail when journaling them.
         This includes removing justifications of why paths through the
         result were rejected as long as the overall predicate succeeded
         under the assumption there is no reason to consider them. This
         could reduce the size of the reporting analysis substantially,
         making it more concise.

         if None then use DEFAULT_PRUNE_OPERATION_CONTRACT_ON_SUCCESS
    """
    if prune_snapshot_on_success is None:
      prune_snapshot_on_success = DEFAULT_PRUNE_OPERATION_CONTRACT_ON_SUCCESS
    self.__operation = operation
    self.__contract = contract
    self.__status_extractor = status_extractor
    self.__cleanup = cleanup
    self.__prune_snapshot_on_success = prune_snapshot_on_success
