# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# This test suite validates the scanners by running queries against ALL file formats and
# their permutations (e.g. compression codec/compression type). This works by exhaustively
# generating the table format test vectors for this specific test suite. This way, other
# tests can run with the normal exploration strategy and the overall test runtime doesn't
# explode.

from tests.common.impala_test_suite import ImpalaTestSuite

class TestTimeZones(ImpalaTestSuite):
  @classmethod
  def get_workload(cls):
    return 'functional-query'

  @classmethod
  def add_test_dimensions(cls):
    super(TestTimeZones, cls).add_test_dimensions()

    cls.ImpalaTestMatrix.add_constraint(lambda v:\
        v.get_value('table_format').file_format == 'text' and\
        v.get_value('table_format').compression_codec == 'none')

  def test_timezones(self, vector):
    result = self.client.execute("select timezone, utctime, localtime, \
        from_utc_timestamp(utctime,timezone) as impalaresult from functional.alltimezones \
        where localtime != from_utc_timestamp(utctime,timezone)")
    assert(len(result.data) == 0)

  def test_invalid_aliases(self, vector):
    """ Test that conversions from/to invalid timezones return the timestamp
        without change and add a warning.

        IMPALA-7060 removed many abbreviations, aliases and some timezones,
        because these timezone names are not supported by Hive and Spark.
    """
    timestamp = '2018-04-19 13:07:48.891829000'
    for function in ['from_utc_timestamp', 'to_utc_timestamp']:
      for timezone in ['invalid timezone', 'CEST', 'Mideast/Riyadh87']:
        result = self.execute_query_expect_success(self.client,
            "select {0}('{1}', '{2}');".format(function, timestamp, timezone))
        assert "UDF WARNING: Unknown timezone '%s'" % timezone == result.log.strip()
        assert timestamp == result.get_data()
