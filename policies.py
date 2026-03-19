#!/usr/bin/env python3
import json
from py_abac import Policy

POLICY_FILE = "policies.json"


def load_policies(storage):
    """
    Load policies from JSON file into ABAC memory storage
    """

    try:
        with open(POLICY_FILE, "r") as f:
            policies = json.load(f)

        for p in policies:
            policy = Policy.from_json(p)
            storage.add(policy)

        print(" Policies Loaded Successfully")

    except Exception as e:
        print(" Error Loading Policies:", e)


def create_access_request(subject_as, service, action):
    """
    Create ABAC Access Request
    """

    request = {
        "subject": {
            "id": f"host_as_{subject_as}",
            "attributes": {
                "as": subject_as
            }
        },
        "resource": {
            "id": service,
            "attributes": {
                "service": service
            }
        },
        "action": {
            "id": action,
            "attributes": {
                "method": action
            }
        },
        "context": {}
    }

    return request
