"""Schema for code documentation extraction."""

from structure_it.schemas.base import BaseSchema


class Parameter(BaseSchema):
    """Function/method parameter.

    Attributes:
        name: Parameter name.
        type: Parameter type.
        description: Parameter description.
        default_value: Default value of the parameter.
        required: Boolean indicating if parameter is required.
    """

    name: str
    type: str | None = None
    description: str | None = None
    default_value: str | None = None
    required: bool = True


class ReturnValue(BaseSchema):
    """Function/method return value.

    Attributes:
        type: Return type.
        description: Description of the return value.
    """

    type: str | None = None
    description: str | None = None


class Example(BaseSchema):
    """Code example.

    Attributes:
        code: Code snippet.
        description: Description of the example.
        language: Programming language (default: "python").
    """

    code: str
    description: str | None = None
    language: str = "python"


class FunctionDoc(BaseSchema):
    """Function or method documentation.

    Attributes:
        name: Function name.
        signature: Function signature.
        description: Function description.
        parameters: List of parameters.
        returns: Return value documentation.
        raises: List of exceptions raised.
        examples: List of usage examples.
        notes: Additional notes.
        see_also: References to related functions/classes.
        deprecated: Boolean indicating if function is deprecated.
        deprecation_message: Message explaining deprecation.
    """

    name: str
    signature: str
    description: str
    parameters: list[Parameter] = []
    returns: ReturnValue | None = None
    raises: list[str] = []
    examples: list[Example] = []
    notes: list[str] = []
    see_also: list[str] = []
    deprecated: bool = False
    deprecation_message: str | None = None


class ClassDoc(BaseSchema):
    """Class documentation.

    Attributes:
        name: Class name.
        description: Class description.
        attributes: List of class attributes.
        methods: List of methods.
        inherits_from: List of parent classes.
        examples: List of usage examples.
        notes: Additional notes.
    """

    name: str
    description: str
    attributes: list[Parameter] = []
    methods: list[FunctionDoc] = []
    inherits_from: list[str] = []
    examples: list[Example] = []
    notes: list[str] = []


class ModuleDoc(BaseSchema):
    """Module/package documentation.

    Attributes:
        name: Module name.
        description: Module description.
        functions: List of functions in module.
        classes: List of classes in module.
        constants: List of constants in module.
        examples: List of usage examples.
        dependencies: List of module dependencies.
        exports: List of exported symbols.
    """

    name: str
    description: str
    functions: list[FunctionDoc] = []
    classes: list[ClassDoc] = []
    constants: list[Parameter] = []
    examples: list[Example] = []
    dependencies: list[str] = []
    exports: list[str] = []


class CodeDocumentation(BaseSchema):
    """Complete code documentation extraction.

    Attributes:
        module: Module-level documentation.
        functions: List of top-level functions.
        classes: List of top-level classes.
        language: Programming language.
        file_path: Path to the source file.
        repository_url: URL to the repository.
        version: Code version.
        license: License information.
    """

    module: ModuleDoc | None = None
    functions: list[FunctionDoc] = []
    classes: list[ClassDoc] = []

    # Metadata
    language: str = "python"
    file_path: str | None = None
    repository_url: str | None = None
    version: str | None = None
    license: str | None = None
