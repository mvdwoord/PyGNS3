"""Regenerate the mock_api.py file with API responses."""
import json
from pygns3 import *

api = GNS3API
api.load_configuration()

base_paths = [
    '/v2/computes/local',
    '/v2/version',
    '/v2/version',
    '/v2/computes',
    '/v2/computes/local',
    '/v2/computes/11df1f68-23ab-42f5-9a93-af65b7daad2a',
    '/v2/projects',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/drawings',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/links',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/df2f8f9c-23cf-4001-a1d1-834f0ff66436',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/7e6c9433-dbab-4b34-a731-2b43a7f77fef',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/df2f8f9c-23cf-4001-a1d1-834f0ff66436',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/61c67710-3c63-4f0d-bc4c-9680593e1a19',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/7e6c9433-dbab-4b34-a731-2b43a7f77fef',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/a73e4d0e-2572-4945-8777-2b64919eba95',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/a73e4d0e-2572-4945-8777-2b64919eba95',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/6f58d4cf-2aea-40e4-9d1b-e5bf20f3d51a',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/be1673f7-b534-4263-bf83-ac05eb618360',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/df2f8f9c-23cf-4001-a1d1-834f0ff66436',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/61c67710-3c63-4f0d-bc4c-9680593e1a19',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes/a73e4d0e-2572-4945-8777-2b64919eba95',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/nodes',
    '/v2/projects/a1ea2a19-2980-41aa-81ab-f1c80be25ca7/snapshots',
    '/v2/projects/5daa48ff-dbd6-407c-a3c6-645e743f233a',
    '/v2/projects/5daa48ff-dbd6-407c-a3c6-645e743f233a/drawings',
    '/v2/projects/5daa48ff-dbd6-407c-a3c6-645e743f233a/links',
    '/v2/projects/5daa48ff-dbd6-407c-a3c6-645e743f233a/nodes',
    '/v2/projects/5daa48ff-dbd6-407c-a3c6-645e743f233a/snapshots',
]

responses = {}

def main():
    for path in base_paths:
        response = api.get_request(path).json()
        value = f"{json.dumps(response)}"
        responses.update({path: value})

    print(responses)

if __name__ == '__main__':
    main()