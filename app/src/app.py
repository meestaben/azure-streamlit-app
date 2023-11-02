import streamlit as st
import importlib

# this list and other metadata could be read in from a json file or from a db call at startup
ALLOWED_MODULES = ['letter1', 'letter2', 'letter3']

def safe_import_module(module_name):
    
    if module_name in ALLOWED_MODULES:
        try:
            return importlib.import_module(f"includes.{module_name}")
        except ModuleNotFoundError:
            st.error(f"The module {module_name} could not be found.")
            return None
    else:
        # Handle unexpected module names safely
        st.error("Invalid module name.")
        return None

# Get the query params from the URL
query_params = st.experimental_get_query_params()

# Check if the expected query param 'module' is there
module_name = query_params.get('module', [None])[0]

if module_name:
    # Import the module safely based on the query string parameter
    module = safe_import_module(module_name)
    module.run()
else:
    st.write("No module specified in query string.")