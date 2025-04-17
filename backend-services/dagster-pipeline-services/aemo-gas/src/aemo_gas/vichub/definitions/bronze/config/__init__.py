# import importlib
# import pathlib as pt
#
# # Directory of the current package (same level as __init__.py)
# package_dir = pt.Path(__file__).parent
# package_name = __name__
#
# all = []
#
# # Loop through all Python files in the package directory
# for path in package_dir.glob("*.py"):
#     if path.stem != "__init__":
#         module_name = f"{package_name}.{path.stem}"
#         module = importlib.import_module(module_name)
#         print(module)
#         all.append(module.config)


from . import int029a_system_wide_notices

all = [int029a_system_wide_notices.config]
