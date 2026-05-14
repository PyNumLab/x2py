from .models import *
from fortran_parser.models import *


def _first_module(parsed):
    """Accept a FortranModule, FortranFile, or legacy signature list in tests."""
    if hasattr(parsed, "procedures") and hasattr(parsed, "derived_types") and hasattr(parsed, "uses"):
        return parsed
    if hasattr(parsed, "modules"):
        if not parsed.modules:
            raise ValueError("Expected at least one Fortran module in parsed file")
        return parsed.modules[0]
    if isinstance(parsed, list):
        module_name = next((getattr(sig, "module", None) for sig in parsed if getattr(sig, "module", None)), None)
        return FortranModule(name=module_name or "", procedures=[sig for sig in parsed if not getattr(sig, "in_interface", False)])
    raise TypeError(f"Unsupported Fortran parse object: {type(parsed)!r}")

FORTRAN_TYPE_MAP = {
    ("integer", None): "Int32",
    ("real", None): "Float64",
    ("real", "4"): "Float32",
    ("real", "8"): "Float64",
    ("logical", None): "Bool",
    ("character", None): "String",
}

def fortran_variable_to_semantic_type(var) -> SemanticType:

    kind = str(var.kind).lower() if var.kind is not None else None
    semantic_name = FORTRAN_TYPE_MAP.get(
        (var.base_type.lower(), kind),
        "Unknown"
    )

    semantic_type = SemanticType(
        name=semantic_name,
        rank=var.rank,
        dtype=semantic_name,
        shape=list(var.shape),
    )

    # --------------------------------------------------------
    # Array constraints
    # --------------------------------------------------------

    if var.rank > 0:

        semantic_type.constraints.append(
            SemanticConstraint(
                name="Shape",
                arguments=list(var.shape),
            )
        )

        semantic_type.constraints.append(
            SemanticConstraint(
                name="FortranContiguous"
            )
        )

    # --------------------------------------------------------
    # Parameters
    # --------------------------------------------------------

    if getattr(var, "is_parameter", False):

        semantic_type.constraints.append(
            SemanticConstraint("Constant")
        )

    return semantic_type
    
def fortran_argument_to_semantic_argument(
    arg
) -> SemanticArgument:

    semantic_type = fortran_variable_to_semantic_type(arg)

    if arg.allocatable:
        semantic_type.constraints.append(
            SemanticConstraint("Allocatable")
        )

    if arg.pointer:
        semantic_type.constraints.append(
            SemanticConstraint("Pointer")
        )

    ownership = semantic_type.ownership

    if arg.intent.lower() == "in":
        ownership.mutable = False

    else:
        ownership.mutable = True

    return SemanticArgument(
        name=arg.name,
        semantic_type=semantic_type,
        intent=arg.intent,
        optional=arg.optional,
    )
    
def fortran_procedure_to_semantic_function(
    proc
) -> SemanticFunction:

    semantic_args = [
        fortran_argument_to_semantic_argument(a)
        for a in proc.arguments
    ]

    return_type = None

    if proc.result:
        return_type = fortran_variable_to_semantic_type(
            proc.result
        )

    function = SemanticFunction(
        name=proc.name,
        native_name=proc.name,
        arguments=semantic_args,
        return_type=return_type,
    )

    return function

def fortran_derived_type_to_semantic_class(
    dtype,
    procedure_lookup: dict[str, SemanticFunction]
) -> SemanticClass:

    fields = [
        fortran_argument_to_semantic_argument(f)
        for f in dtype.fields
    ]

    methods = []

    for method_name in dtype.methods:

        if method_name in procedure_lookup:

            proc = procedure_lookup[method_name]

            methods.append(
                SemanticMethod(
                    name=proc.name,
                    native_name=proc.native_name,
                    arguments=proc.arguments,
                    return_type=proc.return_type,
                    contracts=proc.contracts,
                )
            )

    bases = []

    if dtype.extends:
        if isinstance(dtype.extends, str):
            bases.append(dtype.extends)
        else:
            bases.append(dtype.extends.name)

    return SemanticClass(
        name=dtype.name,
        native_name=dtype.name,
        fields=fields,
        methods=methods,
        base_classes=bases,
    )

def fortran_module_to_semantic_module(
    module
) -> SemanticModule:

    module = _first_module(module)

    semantic_functions = []
    for proc in module.procedures:

        semantic_functions.append(
            fortran_procedure_to_semantic_function(proc)
        )

    procedure_lookup = {
        f.name: f
        for f in semantic_functions
    }

    semantic_classes = []

    for dtype in module.derived_types:

        semantic_classes.append(
            fortran_derived_type_to_semantic_class(
                dtype,
                procedure_lookup,
            )
        )

    return SemanticModule(
        name=module.name,
        functions=semantic_functions,
        classes=semantic_classes,
        imports=list(module.uses.keys()),
    )

if __name__ == "__main__":
    pass

