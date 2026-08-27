import re
import unittest

from . import data_service
from . import gtm_agent


def _values(value):
    if isinstance(value, dict):
        for key, nested_value in value.items():
            yield key
            yield from _values(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _values(nested_value)
    else:
        yield str(value)


class ProspectToolTest(unittest.TestCase):
    def test_prospect_tools_exclude_billing_pii(self):
        data_service._PROFILES.clear()

        for prospect_id in data_service.PROSPECTS:
            results = [
                gtm_agent.get_prospect.invoke({"prospect_id": prospect_id}),
                gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id}),
                gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id}),
            ]
            for result in results:
                values = list(_values(result))
                self.assertNotIn("billing_qualification", values)
                self.assertFalse(any(re.fullmatch(r"\d{3}-\d{2}-\d{4}", value) for value in values))
                self.assertFalse(any(re.fullmatch(r"\d{16}", value) for value in values))
