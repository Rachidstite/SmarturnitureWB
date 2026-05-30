import os
def apply(project_path):
    init_py = os.path.join(project_path, "Init.py")
    with open(init_py, "w") as f:
        f.write("try:\n    from . import InitGui\nexcept ImportError:\n    import InitGui\n")
