import argparse
import json


def set_kernel_spec(notebook_filepath, display_name, kernel_name):
    with open(notebook_filepath, "r") as openfile:
        notebook = json.load(openfile)
    kernel_spec = {"display_name": display_name, "language": "python", "name": kernel_name}
    if "metadata" not in notebook:
        notebook["metadata"] = {}
    notebook["metadata"]["kernelspec"] = kernel_spec
    with open(notebook_filepath, "w") as openfile:
        json.dump(notebook, openfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook")
    parser.add_argument("--display-name")
    parser.add_argument("--kernel")
    args = parser.parse_args()
    set_kernel_spec(args.notebook, args.display_name, args.kernel)
