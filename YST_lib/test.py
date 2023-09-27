import sys

def check_arg():
    if len(sys.argv) > 1:
        args = {}
        for argument in sys.argv[1:]:
            if argument.startswith("-"):
                arg_parts = argument.split("=")
                if len(arg_parts) == 2:
                    arg_name = arg_parts[0][1:]
                    arg_value = arg_parts[1]
                    args[arg_name] = arg_value

        return args

# Example usage
arguments = check_arg()
if not arguments:
    # Handle case when no arguments are passed
    print("No arguments provided")
else:
    # Use the argument values
    for arg_name, arg_value in arguments.items():
        print(f"{arg_name}: {arg_value}")
