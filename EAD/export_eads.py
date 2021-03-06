from vandura.config import ead_dir
from vandura.config import aspace_credentials
from vandura.shared.scripts.archivesspace_authenticate import authenticate

import getpass
import requests
import json
from os.path import join
import time
from datetime import datetime
import os

migration_stats_dir = join(ead_dir, "migration_stats")
exporter_stats_file = join(migration_stats_dir, "exporter_stats.txt")
exports_dir = join(ead_dir, "exports")
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

aspace_url, username, password = aspace_credentials()
s = authenticate(aspace_url, username, password)

start_time = datetime.now()

# Uncomment one of these to export everything or select resources
ids_to_export = s.get('{}/repositories/2/resources?all_ids=true'.format(aspace_url)).json()
#ids_to_export = ["248"]


def pad_id(resource_id):
    file_id = str(resource_id)
    while len(file_id) < 4:
        file_id = '0' + file_id
    return file_id

for resource_id in ids_to_export:
    file_id = pad_id(resource_id)
    if file_id not in os.listdir(exports_dir):
        print "Writing {}".format(resource_id)
        ead = s.get('{0}/repositories/2/bhl_resource_descriptions/{1}.xml?include_unpublished=true&include_daos=true&numbered_cs=true'.format(aspace_url, resource_id),stream=True)
        with open(join(exports_dir, file_id +'.xml'),'wb') as ead_out:
             for chunk in ead.iter_content(10240):
                    ead_out.write(chunk)
        print "Wrote {0}".format(resource_id)

end_time = datetime.now()

script_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S %p")
script_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S %p")
script_running_time = end_time - start_time

print "Script start time:", script_start_time
print "Script end time:", script_end_time
print "Script running time:", script_running_time

exporter_stats = """
Script start time: {0}
Script end time: {1}
Script running time: {2}""".format(script_start_time, script_end_time, script_running_time)

with open(exporter_stats_file, "w") as f:
    f.write(exporter_stats)

s.post("{}/logout".format(aspace_url))
