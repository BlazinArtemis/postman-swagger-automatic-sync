import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Import test modules to ensure they are included when running tests
from .test_endpoint_transfer import TestEndpointTransfer
from .test_helper_functions import TestHelperFunctions
from .test_main_script import TestMainScript
