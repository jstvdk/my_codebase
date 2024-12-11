#!/usr/bin/env python3

from ctapipe.tools import process
import yaml
from traitlets.config.loader import Config

input_file = '/Users/vdk/muons2024/simtel_files/2024year_tuned_nooulier_reflectivity_additional/run101_muon.simtel.gz'
config_file = '/Users/vdk/Software/ctapipe_processor_test/processor_tool_muon_configuration.yaml'
#config_file = '/Users/vdk/Software/ctapipe_processor_test/processor_tool_muon_configuration_no_ringquery.yaml'

with open(config_file) as yaml_file:    
    data = yaml.safe_load(yaml_file)

data['EventSource']['input_url'] = input_file

test_tool = process.ProcessorTool(
    config=Config(data),
    overwrite=True
)

test_tool.run()
