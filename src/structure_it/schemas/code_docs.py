"""Schema for code documentation extraction."""

from structure_it.schemas.base import BaseSchema


class Parameter(BaseSchema):
    """Function/method parameter."""

    name: str
    type: str | None = None
    description: str | None = None
    default_value: str | None = None
    required: bool = True


class ReturnValue(BaseSchema):
    """Function/method return value."""

    type: str | None = None
    description: str | None = None


class Example(BaseSchema):
    """Code example."""

    code: str
    description: str | None = None
    language: str = "python"


class FunctionDoc(BaseSchema):
    """Function or method documentation."""

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
    """Class documentation."""

    name: str
    description: str
    attributes: list[Parameter] = []
    methods: list[FunctionDoc] = []
    inherits_from: list[str] = []
    examples: list[Example] = []
    notes: list[str] = []


class ModuleDoc(BaseSchema):
    """Module/package documentation."""

    name: str
    description: str
    functions: list[FunctionDoc] = []
    classes: list[ClassDoc] = []
    constants: list[Parameter] = []
    examples: list[Example] = []
    dependencies: list[str] = []
    exports: list[str] = []


class CodeDocumentation(BaseSchema):
    """Complete code documentation extraction."""

    module: ModuleDoc | None = None
    functions: list[FunctionDoc] = []
    classes: list[ClassDoc] = []

    # Metadata
    language: str = "python"
    file_path: str | None = None
    repository_url: str | None = None
    version: str | None = None
    license: str | None = None
